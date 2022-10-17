odoo.define('sign_documents.create_button', function(require) {
    'use strict';

    var core = require('web.core');
    var _t = core._t;

    var webListRenderer = require('web.ListRenderer');
    webListRenderer.include({
        _renderBody: function () {
            $('#downloadDocument').hide();
            return this._super();
        },
    });

//   Reference from mass mailing
    var webKanbanColumn = require('web.KanbanColumn');
    webKanbanColumn.include({
        init: function () {
            this._super.apply(this, arguments);
            if (this.data.viewType === "kanban" || this.data.context.params && this.data.context.params.view_type  === "kanban") {
                $('#downloadDocument').hide();
            }
            if (this.modelName === 'sign.request.details') {
                this.draggable = false;
            }
        },
    });

    var webKanbanRecord = require('web.KanbanRecord');
    webKanbanRecord.include({
        init: function () {
            this._super.apply(this, arguments);
            $('#downloadDocument').hide();
        },

        _openRecord: function () {
            var self = this;
            if (this.modelName === 'document.sign.template') {
                var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'sign.request.process',
                    view_mode: 'form',
                    view_type: 'form',
                    name: 'Sign Request Process',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        default_template_id: self.id,
                        default_file_name: self.recordData.file_name,
                        default_subject: 'Signature Request - ' + self.recordData.file_name
                    }
                };
                this.do_action(action);
            } else if (this.modelName === 'sign.request.details') {
                this._rpc({
                    model: 'sign.request.details',
                    method: 'edit_template',
                    args: [self.recordData.id],
                    context: {active_id: self.id},
                }).then(function(action) {
                    self.do_action(action);
                });
            } else {
                this._super.apply(this, arguments);
            }
        }
    });

    var webFormController = require("web.FormController");
        webFormController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons != undefined) {
                var self = this;
                this.$buttons.on('click', '#buttonUploadDocument', function (e) {
                    var state = self.initialState;
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    self._rpc({
                        model: 'hr.contract',
                        method: 'get_user_id',
                        args: [state.model, state.res_id],
                    }).then(function(record) {
                    UploadDocument(self, record);})
                    });
                }
            },
        });

    var webKanbanController = require("web.KanbanController");
    webKanbanController.include({
            renderButtons: function () {
                this._super.apply(this, arguments);
                var self = this;
                if (this.modelName === "document.sign.template" || this.modelName ===  "sign.request.details") {
                    if (this.$buttons != undefined) {
                        this.$buttons.find("button.o-kanban-button-new").text(_t("Upload Document")).on("click", function (e) {
                            e.preventDefault();
                            e.stopImmediatePropagation();
                            UploadDocument(self, false);
                        });
                        this.$buttons.find('button.o_button_import').hide();
                    }
                }
            },
        });

    function UploadDocument(self, partner) {
                var state = self.model.get(self.handle, {raw: true});
                var context = state.getContext()
                var $select_file = $('<input type="file" accept="pdf/*" name="files"/>');
                $select_file.on('change', function (e) {
                    var file = e.target.files[0];
                    var file_reader = new FileReader();
                    var ext = file.name.replace(/^.*\./, '');
                    if(ext !== 'pdf') {
                        alert("Please select only pdf file!")
                    }
                    else {
                        file_reader.onload = function(e) {
                            var data_of_file = e.target.result;
                            self._rpc({
                                model: 'document.sign.template',
                                method: 'upload_selected_document',
                                args: [file.name, file.name, file.type, data_of_file]
                            })
                            .then(function(data_template) {
                                self.do_action({
                                    type: "ir.actions.client",
                                    tag: 'sign_documents.pdf_template',
                                    name: _t(data_template['file_name']),
                                    context: {
                                        id: data_template['template_id'],
                                        edit: true,
                                        res_model: state.model,
                                        res_id: state.res_id,
                                        partner: partner,
                                        },
                                });
                            });
                        };
                        file_reader.readAsDataURL(file);
                    }
                });
                $select_file.click();
           };
});

odoo.define('document.sign.template', function(require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var core = require('web.core');
    var config = require('web.config');
    var framework = require('web.framework');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var EditPDFIframe = require('sign_documents.EditPDFIframe');
    var _t = core._t;

    var DocumentTemplate = AbstractAction.extend(ControlPanelMixin, {
        className: "sign_pdf_document",

        events: {'templateUpdate iframe.pdf_iframe': function(e) {this.UpdatePDF();}},

        init: function(parent, options) {
            this._super.apply(this, arguments);
            if(options.context.id === undefined) {
                return
//                var base_url = window.location.origin;
//                if (options.params.active_id) {
//                    window.location.href = base_url + "/web?debug=assets#id=" + options.params.active_id + "&model=document.sign.template&view_type=form";
//                }
//                else {
//                    window.location.href = base_url + "/web?debug=assets#model=document.sign.template&view_type=kanban";
//                }
            }
            this.check_edit_template = options.context.edit
            this.request_state = options.context.request_state
            this.requestId = options.context.request_id
            this.model = options.context.res_model;
            this.res_id = options.context.res_id;
            var self = this;
            self._updateControlPanel()
            if ($('#downloadDocument').length == 0) {
                $('.o_cp_right').append($('<a/>', {
                    role: "button",
                    html: _t("Download Document"),
                    class:"btn btn-primary",
                    id:"downloadDocument"
                    }));
            }
            $('#downloadDocument').attr('href', "/get_download/" + self.requestId)
            this.file_name = options.name;
            this.template_id = options.context.id;
            this.subject =  'Signature Request - ' + this.file_name;
            this.email_to = options.context.partner;
        },

        start: function() {
            if(this.template_id === undefined) {
                return;
            }
            this.$el.append(core.qweb.render('document.sign.template', {widget: this}));
            this.update_control_panel_details();
            var self = this;
            if (self.request_state != 'signed') {
                $('#downloadDocument').hide();
            }
            if(this.$('iframe').length) {
                core.bus.on('DOM_updated', this, function () {
                    var datadict =  {fieldTypes: this.sign_item_types, SignatureFieldType: this.sign_fields_items}
                    this.pdfiframe = new EditPDFIframe(this, datadict);
                    return this.pdfiframe.attachTo(this.$('iframe')).then(function() {framework.unblockUI();});
                });
            }
            return this._super();
        },

        willStart: function() {
            if(this.template_id === undefined) {
                return this._super.apply(this, arguments);
            }
            return $.when(this._super(), this.get_model_details());
        },

        get_model_details: function() {
            var self = this;
            var AttachmentSignDetails = this._rpc({
                    model: 'document.sign.template',
                    method: 'get_details',
                    args: [[this.template_id]],
                }).then(function(template) {
                    self.sign_fields_items = template[1];
                    self.attachment_id = template[2];
                    return $.when(template[1], template[2]);
                });
            var SignFieldType = this._rpc({
                    model: 'sign.field.type',
                    method: 'search_read',
                    kwargs: {context: session.user_context},
                })
                .then(function(fieldTypes) {
                    self.sign_item_types = fieldTypes;
                });

            return $.when(AttachmentSignDetails, SignFieldType);
        },

        _updateControlPanel: function () {
            var self = this;
            var check_data = "";
            if (self.check_edit_template) {
                $('#downloadDocument').hide();
                this.cp_content = {
                    $buttons: $('<button/>', {
                        type: "button",
                        class:"btn btn-primary",
                        html: _t("Send Document"),
                        })
                    .on('click', function() {
                            self._rpc({
                            model: 'document.sign.template',
                            method: 'search_read',
                            domain: [["id", "=", self.template_id]],
                            fields: ['sign_document_item_ids'],
                        }).then(function(check_record) {
                            if (check_record[0].sign_document_item_ids.length <= 0) {
                                alert("Please defines sign field(Box) items in documents first!");
                            }
                            else{
                                self.do_action({
                                res_model: 'sign.request.process',
                                views: [[false, 'form']],
                                type: 'ir.actions.act_window',
                                target: 'new',
                                context: {
                                    'default_template_id': self.template_id,
                                    'default_file_name': self.file_name,
                                    'default_subject': self.subject,
                                    'default_email_to': self.email_to,
                                    'model': self.model,
                                    'res_id': self.res_id},
                                });
                            }
                        });
                    })
                }
             }
             else if (self.request_state != 'signed') {
                 this.cp_content = {
                    $buttons: $('<button/>', {
                        type: "button",
                        id: "ValidateButton",
                        class:"btn btn-primary",
                        html: _t("Validate Document"),
                        }).on('click', function() {
                         self._rpc({
                            model: 'sign.request.details',
                            method: 'update_with_pdf_document',
                            args: ['sign.request.details', self.requestId, JSON.stringify(self.sign_fields_items)]
                        }).then(function(check) {
                            if (check){
                                $('#ValidateButton').hide();
                                $('#downloadDocument').show();
                            }
                            else {
                                alert("Please fill all defines fields details");
                            }
                        });
                     })
                 }
            }
            else if (self.request_state === 'signed') {
                $('#downloadDocument').show();
            }
        },

        update_control_panel_details: function() {
            this.update_control_panel({
                search_view_hidden: true,
                cp_content: this.cp_content,
                clear: true
            });
        },

        getDataValues: function(pageItem, index) {
            return {
                'name': pageItem.data('name'),
                'page': index,
                'sign_field_type_id': pageItem.data('sign_type'),
                'pos_X': pageItem.data('pos_X'),
                'pos_Y': pageItem.data('pos_Y'),
                'item_width': pageItem.data('item_width'),
                'item_height': pageItem.data('item_height'),
                'template_id': this.template_id,
            };
        },

        CreatePDFData: function() {
            var config = this.pdfiframe.config;
            var fieldData = {};
            for(var index in config) {
                for(var i = 0 ; i < config[index].length ; i++) {
                    fieldData[index + i] = this.getDataValues(config[index][i], index)
                }
            }
            return fieldData;
        },

        UpdatePDF: function() {
            this._rpc({
                model: 'document.sign.template',
                method: 'update_sign_document_items',
                args: [this.template_id, this.CreatePDFData()],
            });
        },
    });

    core.action_registry.add('sign_documents.pdf_template', DocumentTemplate);
});


