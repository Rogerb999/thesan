# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
import psycopg2
from odoo import fields, models, api
from odoo.tools import pycompat
_logger = logging.getLogger(__name__)


class Import(models.TransientModel):

    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, columns, options, dryrun=False):
        """ Actual execution of the import

        :param fields: import mapping: maps each column to a field,
                       ``False`` for the columns to ignore
        :type fields: list(str|bool)
        :param columns: columns label
        :type columns: list(str|bool)
        :param dict options:
        :param bool dryrun: performs all import operations (and
                            validations) but rollbacks writes, allows
                            getting as much errors as possible without
                            the risk of clobbering the database.
        :returns: A list of errors. If the list is empty the import
                  executed fully and correctly. If the list is
                  non-empty it contains dicts with 3 keys ``type`` the
                  type of error (``error|warning``); ``message`` the
                  error message associated with the error (a string)
                  and ``record`` the data which failed to import (or
                  ``false`` if that data isn't available or provided)
        :rtype: dict(ids: list(int), messages: list({type, message, record}))
        """
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')

        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)

        except ValueError as error:
            return {
                'messages': [{
                    'type': 'error',
                    'message': pycompat.text_type(error),
                    'record': False,
                }]
            }

        _logger.info('importing %d rows...', len(data))

        if self.res_model == 'hr.novelty':
            get_state = import_fields.index("state")
            if get_state:
                for field_data in data:
                    if field_data[get_state] not in ['Draft', 'Wait']:
                        return {
                            'messages': [{
                                'type': 'error',
                                'message': pycompat.text_type(
                                    "You Can't import  novelty which "
                                    "is not in Draft or Wait state!"),
                                'record': False,
                            }]
                        }

        name_create_enabled_fields = options.pop(
            'name_create_enabled_fields', {})
        model = self.env[self.res_model].with_context(
            import_file=True,
            name_create_enabled_fields=name_create_enabled_fields)
        import_result = model.load(import_fields, data)
        _logger.info('done')

        # If transaction aborted, RELEASE SAVEPOINT is going to raise
        # an InternalError (ROLLBACK should work, maybe). Ignore that.
        # TODO: to handle multiple errors, create savepoint around
        #       write and release it in case of write error (after
        #       adding error to errors array) => can keep on trying to
        #       import stuff, and rollback at the end if there is any
        #       error in the results.
        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                # cancel all changes done to the registry/ormcache
                self.pool.reset_changes()
            else:
                self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        # Insert/Update mapping columns when import complete successfully
        if import_result['ids'] and options.get('headers'):
            BaseImportMapping = self.env['base_import.mapping']
            for index, column_name in enumerate(columns):
                if column_name:
                    # Update to latest selected field
                    exist_records = BaseImportMapping.search(
                        [('res_model', '=', self.res_model), (
                            'column_name', '=', column_name)])
                    if exist_records:
                        exist_records.write({'field_name': fields[index]})
                    else:
                        BaseImportMapping.create({
                            'res_model': self.res_model,
                            'column_name': column_name,
                            'field_name': fields[index]
                        })

        return import_result
