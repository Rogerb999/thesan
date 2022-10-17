odoo.define('base_start_stop_timer.base_start_stop_timer', function(require) {

    'use strict';
    require('website.website');
    require('web.dom_ready');
    var ajax = require('web.ajax');

    $(".time_record").on("click", function(e){
        var kw_data = $(this).data()
        ajax.jsonRpc('/record/work_time', 'call', kw_data).then(function (data){
            if (data.url){
                window.location = data.url
            } else{
                window.location.reload();
            }
        });
    });

});
