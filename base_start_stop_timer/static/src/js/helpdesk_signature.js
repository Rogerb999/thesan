odoo.define('helpdesk_ticket_customer_signature.helpdesk_signature', function (require){
    "use strict";

    require('web_editor.ready');

    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var core = require('web.core');
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");

    var qweb = core.qweb;

    var SignatureForm1 = Widget.extend({
        template: 'portal.portal_signature',
        events: {
            'click #o_portal_sign_clear': 'clearSign',
            'click .o_portal_sign_submit': 'submitSign',
            'init #o_portal_sign_accept': 'initSign',
        },

        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.options = _.extend(options || {}, {
                csrf_token: odoo.csrf_token,
            });
        },

        willStart: function() {
            return this._loadTemplates();
        },

        start: function() {
            this.initSign();
        },

        // Signature
        initSign: function () {
            this.$("#o_portal_signature").empty().jSignature({
                'decor-color': '#D1D0CE',
                'color': '#000',
                'background-color': '#fff',
                'height': '142px',
                'width': '302',
                'class':'form-control',
            });
            $('#o_portal_sign_name').hide()
            this.empty_sign = this.$("#o_portal_signature").jSignature('getData', 'image');
        },

        clearSign: function () {
            this.$("#o_portal_signature").jSignature('reset');
        },

        submitSign: function (ev) {
            ev.preventDefault();

            // extract data
            var self = this;
            var $confirm_btn = self.$el.find('button[type="submit"]');

            // process : display errors, or submit
            var signature = self.$("#o_portal_signature").jSignature('getData', 'image');
            var is_empty = signature ? this.empty_sign[1] === signature[1] : true;

            this.$('#o_portal_sign_draw').toggleClass('panel-danger', is_empty).toggleClass('panel-default', !is_empty);

            $confirm_btn.prepend('<i class="fa fa-spinner fa-spin"></i> ');
            $confirm_btn.attr('disabled', true);

            return rpc.query({
                route: '/record_signature',
                params: {
                    'res_id': this.options.resId,
                    'res_model': this.options.resModel,
                    'access_token': this.options.accessToken,
                    'signature': signature ? signature[1] : false,
                },
            }).then(function (data) {
                self.$('.fa-spinner').remove();
                location.reload();
            });
        },

        _loadTemplates: function () {
            return ajax.loadXML('/portal/static/src/xml/portal_signature.xml', qweb);
        },
    });

    base.ready().then(function () {
        $('.ticket_signature').each(function () {
            var $elem = $(this);
            var form = new SignatureForm1(null, $elem.data());
            form.appendTo($elem);
        });
    });

    return {
        SignatureForm1: SignatureForm1,
    };
});

