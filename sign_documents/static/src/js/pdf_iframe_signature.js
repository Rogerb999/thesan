odoo.define('sign_documents.EditPDFIframe', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    var rpc = require('web.rpc');

    var SignatureDialog = Dialog.extend({
        template: 'sign_documents.signature_dialog',
        events: {
            'click #o_portal_sign_clear': 'clearSign',
            'click .o_portal_sign_submit': 'submitSign',
        },

        initSign: function () {
            self.$(".o_portal_signature").jSignature({
                'background-color': '#FFF',
                'color': '#000',
                'height': '142px',
                'width': '100%',
                'decor-color': 'transparent',
            });
            this.empty_sign = self.$(".o_portal_signature").jSignature('getData', 'image');
        },

        clearSign: function () {
            this.$(".o_portal_signature").jSignature('reset');
        },

        submitSign: function (ev) {
            ev.preventDefault();
            var self = this;
            var $confirm_btn = self.$el.find('button[type="submit"]');
            var signature = self.$(".o_portal_signature").jSignature('getData', 'image');
            var is_empty = signature ? self.empty_sign[1] === signature[1] : true;
            if (is_empty) {
                return false;
            }
            this.$('#o_portal_sign_draw').toggleClass('bg-danger text-white', is_empty);
            $confirm_btn.prepend('<i class="fa fa-spinner fa-spin"></i> ');
            $confirm_btn.attr('disabled', true);

            var left = (self.data[0].style.left.slice(0,-1) / 100).toFixed(2);
            var top = (self.data[0].style.top.slice(0,-1) / 100).toFixed(2);
            var width = (self.data[0].style.width.slice(0,-1) / 100).toFixed(2);
            var height = (self.data[0].style.height.slice(0,-1) / 100).toFixed(2);
                rpc.query({
                model: 'sign.document.item',
                method: "set_document_item_value",
                args: ['sign.document.item', self.template_id, height, width, top, left, false, signature ? signature[1] : false, false],
            });

            var divWidth = $(self.dialog_parent).width();
            var divHeight = $(self.dialog_parent).height();
            var image = new Image;
            image.src = "data:" + signature[0] + "," + signature[1]
//            $(self.dialog_parent).empty().append($('<img/>', {src: image.src}).css({height: divheigth, width: divWidth}));
            $(self.dialog_parent).empty().append($('<span/>').addClass("fa fa-edit pull-right"), $('<img/>', {src: image.src}).css({height: divHeight, width: divWidth}));
            this.close();
        },

        init: function(parent, options) {
            this.dialog_parent = {};
            this.template_id = {};
            this.data = {}
            options = (options || {});
            options.size = 'medium';
            this._super(parent, options);
        },

        setParent: function(parent, template_id, data){
            var self = this;
            self.dialog_parent = parent;
            self.template_id = template_id;
            self.data = data;
        },

        start: function() {
           this.initSign();
           return this._super.apply(this, arguments);
        },

        open: function() {
            var self = this;
            this.opened(function(e) {
                self.initSign();
                $("footer.modal-footer").css("display", "none");
                $("header.modal-header").css("display", "none");
            });
            return this._super.apply(this, arguments);
        },
    });

    var EditPDFIframe = Widget.extend({
        events: {
            'click span.fa.fa-trash.pull-right': '_sectionHide',
            'click span.fa.fa-edit.pull-right': '_signatureWidget',
//            'click .o_field_type': '_signatureWidget',
            'change input.o_field_type': '_inputName',
        },

        _inputName: function(e) {
            var self = this;
            var $target = $(e.currentTarget);
            var data = $target.parent();
            var style = data.context.style
            var left = (style.left.slice(0,-1) / 100).toFixed(2);
            var top = (style.top.slice(0,-1) / 100).toFixed(2);
            var width = (style.width.slice(0,-1) / 100).toFixed(2);
            var height = (style.height.slice(0,-1) / 100).toFixed(2);
            return rpc.query({
                model: 'sign.document.item',
                method: "set_document_item_value",
                args: ['sign.document.item', self.template_id, height, width, top, left, e.currentTarget.value, false, false],
            });
        },

        _signatureWidget: function(e) {
            var self = this;
            var $target = $(e.currentTarget);
            var data = $target.parent();
            var signDialog = new SignatureDialog();
//            signDialog.setParent(e.currentTarget, self.template_id, data);
            signDialog.setParent(e.currentTarget.offsetParent, self.template_id, data);
            signDialog.open();
        },

        unlinkRecord: function (data, template_id) {
            var style = data[0].style;
            var left = (style.left.slice(0,-1) / 100).toFixed(2);
            var top = (style.top.slice(0,-1) / 100).toFixed(2);
            var width = (style.width.slice(0,-1) / 100).toFixed(2);
            var height = (style.height.slice(0,-1) / 100).toFixed(2);
            return rpc.query({
                model: 'sign.document.item',
                method: "set_document_item_value",
                args: ['sign.document.item', template_id, height, width, top, left, false, false, true],
            });
        },

        _sectionHide: function (e) {
            var self = this;
            Dialog.confirm(self, "Are you sure you want to delete this sections?", {
                confirm_callback: function () {
                    var $target = $(e.currentTarget);
                    var data = $target.parent();
                    self.unlinkRecord(data, self.template_id);
                    var div = $target.parent()[0];
                    $(div).css("display", "none");
                }
            });
        },

        _getFileURI: function(){
            var fileURI = "/web/static/lib/pdfjs/web/viewer.html?file=";
            fileURI += encodeURIComponent(this.location);
            return fileURI
        },

        get_position: function(value1, value2) {
            if(value1 < 0) {
                value1 = 0;
            } else if(value1 + value2 > 1.0) {
                value1 = 1.0 - value2;
            }
            return (Math.round(value1*10000)/100)
        },

        getRoundValue: function(value1, value2) {
            return Math.round((value1 / value2) * 100 ) / 100
        },

        init: function(parent, datadict) {
            this._super(parent);
            this.loadPdf = new $.Deferred();
            this.location = '/web/image/' + parent.attachment_id.id;
            this.emode = parent.check_edit_template;
            this.request_state = parent.request_state
            this.config = {};
            this.template_id = parent.template_id;
            for(var dataField in datadict) {
                var value = datadict[dataField];
                this[dataField] = {};
                for(var i = 0 ; i < value.length ; i++) {
                    this[dataField][value[i].id] = value[i];
                }
            }
        },

        start: function() {
            this.$pageFrame = this.$el;
            var self = this;
            this.pdfView = (this.$pageFrame.attr('readonly') === "readonly");
            this.rField = this.pdfView || this.emode;
            this.$pageFrame.load(function() {self.delayPdf();});
            this.$pageFrame.attr('src', self._getFileURI() + "#page=1");
            return $.when(this._super(), this.loadPdf);
        },

        _droppableItems: function(e, ui) {
            var helper = ui.helper;
            helper.removeClass('check_drag');
            var self = this;
            var offset = ui.offset;
            var pw = $(e.target).innerWidth();
            var ph = $(e.target).innerHeight();
            var textLayer = $(e.target).find('.textLayer').offset();
            var FieldItem = helper.clone(true)
            FieldItem.removeClass()
            FieldItem.addClass('o_field_type');
            FieldItem.data({pos_X: (offset.left - textLayer.left) / pw, pos_Y: (offset.top - textLayer.top) / ph});
            self.config[parseInt($(e.target)[0]['dataset']['pageNumber'])].push(FieldItem);
            self.reloadSignFieldType();
            self.updateSignFieldItem(FieldItem);
            self.customizeSignFieldType(FieldItem);
            return false;
        },

        _whenReadyForActions: function (active) {
            reloadData();
            active.$('.o_field_type').each(function(i, el) { active.updateSignFieldItem($(el));});
            active.loadPdf.resolve();
            function reloadData() {
                try {
                    active.reloadSignFieldType();
                    active.refresh_timer = setTimeout(reloadData, 2000);
                } catch (e) {}
            }
        },

        reloadSignFieldType: function() {
            for(var pIndex in this.config) {
                var $pc = this.$('#pageContainer' + pIndex);
                var conP = this.config[pIndex];
                for(var i = 0 ; i < conP.length ; i++) {
                    if(!conP[i].parent().hasClass('page')) {
                        $pc.append(conP[i]);
                    }
                }
            }
            var size = (this.$('.page').first().innerHeight() * 0.015) * 0.8;
            this.$('.o_field_type').each(function(i, e) { $(e).css('font-size', size);});
        },

        createSignFieldItem: function(type, posX, posY, width, height, value, signature, name) {
            if (signature) {
                signature = "data:image/png;base64," + signature;
            }
            var editable = this.rField || !!value || signature;
            var datadict = {emode: this.emode, sign_type: type['sign_type'], field_value: value, signature: signature, display_name: type['name'] || type['display_name'], editable: editable}
            var FieldItem = $(core.qweb.render('sign_documents.sign_item', datadict));
            if (self.request_state === 'signed') {
                FieldItem.attr('disabled','disabled');
            }
            return FieldItem.data({
                name:type['name'] || type['display_name'],
                sign_type: type['id'],
                pos_X: posX, pos_Y: posY,
                item_width: width, item_height: height});
        },

        delayPdf: function() {
            var containts = this.$pageFrame.contents();
            var pdfpage = containts.find('.page').length;
            if(pdfpage > 0) {
                this.pdfpage = pdfpage;
                var self = this;
                this.loadPdf.then(function() {
                    if(self.emode) {
                        self.$('button#signature_button').remove();
                        var $fieldTypeButtons = $(core.qweb.render('sign_documents.sign_field_type', {sign_field_types: _.toArray(self.fieldTypes)}));
                            $fieldTypeButtons.prependTo(self.$('#viewerContainer')).draggable({
                            cancel: false,
                            helper: function(e) {
                                var fieldType = self.fieldTypes[$(this).data('field-type-id')];
                                var FieldItem = self.createSignFieldItem(fieldType, 0, 0, fieldType.width, fieldType.height, '', '', fieldType.name);
                                FieldItem.addClass('check_drag ui-selected');
                                self.$('.page').first().append(FieldItem);
                                self.updateSignFieldItem(FieldItem);
                                var fw = FieldItem.css('width');
                                var fh = FieldItem.css('height');
                                FieldItem.css({'width': fw, 'height': fh});
                                return FieldItem;
                            }
                        });
                        self.$('.page').droppable({
                            accept: '*',
                            drop: function(e, ui) {
                                if(!ui.helper.hasClass('check_drag')) {
                                    return true;
                                }
                                self._droppableItems(e, ui);
                                self.$pageFrame.trigger('templateUpdate');
                            },
                        });
                    self.$('.o_field_type').each(function(i, el) {self.customizeSignFieldType($(el)); });
                    }
                });
                this.setElement(containts.find('html'));
                this.$('#openFile').hide()
                this.$('#viewBookmark').hide()
                for(var i = 1 ; i <= this.pdfpage ; i++) {
                    this.config[i] = [];
                }
                var $jsJqueryUi = $("<script></script>", {
                    type: "text/javascript", src: "/web/static/lib/jquery.ui/jquery-ui.js"
                });
                var href_list = [
                    "/sign_documents/static/src/css/sign_documents.css",
                    "/web/static/lib/jquery.ui/jquery-ui.css",
                    "/web/static/lib/fontawesome/css/font-awesome.css",
                    "/web/static/lib/select2/select2.css"];

                for (var l = 0 ; l <= href_list.length; l++) {
                    this.$('head')[0].appendChild($("<link/>", {
                        rel: "stylesheet", type: "text/css",
                        href: href_list[l]
                    })[0]);
                }
                this.$('head')[0].appendChild($jsJqueryUi[0]);

                $(Object.keys(this.SignatureFieldType).map(function(id) {
                    return self.SignatureFieldType[id];
                })).each(function(i, fieldTypeId) {
                    var FieldItem = self.createSignFieldItem(
                    self.fieldTypes[parseInt(fieldTypeId.sign_field_type_id[0])],
                    fieldTypeId.pos_X, fieldTypeId.pos_Y, fieldTypeId.item_width,
                    fieldTypeId.item_height, fieldTypeId.value, fieldTypeId.signature, fieldTypeId.name);
                    self.config[parseInt(fieldTypeId.page)].push(FieldItem);
                });
                self._whenReadyForActions(self);
            } else {
                var self = this;
                setTimeout(function() { self.delayPdf(); }, 50);
            }
        },

        updateSignFieldItem: function(FieldItem) {
            var self = this;
            var posX = FieldItem.data('pos_X'), posY = FieldItem.data('pos_Y');
            var width = FieldItem.data('item_width'), height = FieldItem.data('item_height');
            posX = self.get_position(posX, width);
            posY = self.get_position(posY, height);
            FieldItem.data({
                pos_X: posX/100,
                pos_Y: posY/100}
            ).css({
                top: posY+'%',
                left: posX+'%',
                width: width*100+'%',
                height: height*100+'%'
            });
        },

        customizeSignFieldType: function(FieldItem) {
            var self = this;
            FieldItem.draggable({
                handle: ".fa-arrows",
                containment: this.draggable ? false : 'parent'
                }).resizable().css('position', 'absolute');

            FieldItem.on('dragstop dragstart resizestart resizestop', function(e, ui) {
                var type = e.type;
                var Sparent = FieldItem.parent();
                var width = Sparent.innerWidth();
                var height = Sparent.innerHeight();
                if (type === 'dragstop') {
                    var Upos = ui.position;
                    FieldItem.data({
                        pos_X: self.getRoundValue(Upos.left, width),
                        pos_Y: self.getRoundValue(Upos.top, height),
                    });
                    self.UpdateAfterDrag(FieldItem);
                 }
                 else if (type === 'dragstart' || type === 'resizestart' ) {
                    self.$('.o_sign_sign_item').removeClass('ui-selected');
                    FieldItem.addClass('ui-selected');
                 }
                 else if (type === 'resizestop') {
                    FieldItem.data({
                        item_width: self.getRoundValue(ui.size.width, width),
                        item_height: self.getRoundValue(ui.size.height, height),
                    });
                    self.UpdateAfterDrag(FieldItem);
                 }
            });
        },

        UpdateAfterDrag: function(FieldItem) {
            var self = this;
            self.updateSignFieldItem(FieldItem);
            self.$pageFrame.trigger('templateUpdate');
            FieldItem.removeClass('ui-selected');
        },
    });

    return EditPDFIframe;
});
