odoo.define('base_extended.import_buttons_invisible', function (require) {
"use strict";

var KanbanController = require('web.KanbanController');
var ListController = require('web.ListController');

var ImportControllerMixin = {

    /**
     * @override
     */
    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this._rpc({
            model: 'res.users',
            method: 'has_group',
            args: ['base_extended.group_import_files']}).then((has_group) => {
            var importbtn = document.getElementsByClassName("o_button_import")
            if (importbtn && importbtn.length > 0) {
                if (!has_group) {
                      importbtn[0].remove()
                } else {
                    importbtn[0].style.display =""
                }
            }
        })
    }
};

ListController.include({
    init: function () {
        this._super.apply(this, arguments);
        ImportControllerMixin.init.apply(this, arguments);
    },
});

KanbanController.include({
    init: function () {
        this._super.apply(this, arguments);
        ImportControllerMixin.init.apply(this, arguments);
    },
});

});
