odoo.define('ks_custom_report.ks_model_relations_widget', function (require) {
"use strict";

    /*
    * This module contains the Query Builder Type Tool to create custom view
    * Required : Model Name
    */

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');
    var ModelFieldSelector = require("web.ModelFieldSelector");

    var KsQueryBuilder = AbstractField.extend({

        custom_events: {
            "field_chain_changed": "_onFieldChainChange",
        },

        init: function () {
            this._super.apply(this, arguments);
            this.ksModelNameField = this.nodeOptions.model || false;
            this.className = "ks_column_field_widget";
        },

        _render: function() {
            if (!this.fieldSelector){
                this.ks_model_name = this.recordData[this.ksModelNameField];
                this.chain = this.value || "id";
                this.options = {
                    readonly: this.mode==="readonly" ? true : false,
                    debugMode: odoo.debug==='assets'? true : false,
                    filter: function (field) {
                        return field.store === true && field.type !== 'binary';
                    },
                }
                this.fieldSelector = new ModelFieldSelector(
                    this,
                    this.ks_model_name,
                    this.chain !== undefined ? this.chain.toString().split(".") : [],
                    this.options
                );
                this.fieldSelector.appendTo(this.$el);
            }
        },


        _onFieldChainChange: function (e) {
            this._setValue(e.data.chain.join("."));
        },

        start: function() {
            if (this.mode ==="edit" && this.viewType === "form"){
                $('body.o_web_client').addClass('ks_cr_body_client');
            }
            return this._super.apply(this, arguments);
        },

        destroy: function (){
            if (this.mode ==="edit" && this.viewType === "form"){
                $('body.o_web_client').removeClass('ks_cr_body_client');
            }
            return this._super.apply(this, arguments);
        },
    });

    registry.add('ks_model_relations', KsQueryBuilder);
    return KsQueryBuilder;
})