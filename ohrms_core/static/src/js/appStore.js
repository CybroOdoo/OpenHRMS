odoo.define('ohrms.ohrms_apps', function (require) {
    'use strict';
    var core = require('web.core');
    var form_widget = require('web.FormRenderer');
    var ajax = require('web.ajax');
    var framework = require('web.framework');
    var Dialog = require('web.Dialog');
    var _t = core._t;
    $(document).ready(function(){
        form_widget.include({
        _addOnClickAction: function ($el, node) {
            var self = this;
            var flag=true;
            //check if the download button is clicked
            $el.click(function(){
                if(node.attrs.custom==='button')
                {
                    //add spinner
                    framework.blockUI();
                    //calls python method to download file
                    return ajax.jsonRpc("/ohrms/download", 'call', {
                    'url': node.attrs.zip_loc
                    }).then(function(data) {
                        //remove spinner
                        framework.unblockUI();
                        //check if download is success
                        if(data==true)
                        {
                            //creates success dialog
                            new Dialog(this, {
                    size: 'medium',
                    title: _t("Success"),
                    $content: '<span>App Successfully Download, Please Restart Open HRMS Service and Update App List</span>',
                    buttons: [
                        {text: _t("Ok"), close: true}
                    ],
                }).open();
                        }else{
                            //creates error dialog
                            new Dialog(this, {
                    size: 'medium',
                    title: _t("<span style='color:#dd0000;'>Error</span>"),
                    $content: '<span>The App Can Not Be Downloaded Due To Some Erro.</span>',
                    buttons: [
                        {text: _t("Ok"), close: true}
                    ],
                }).open();
                        }
                    });
                }
            });
            //if the button clicked is note the download button
            if(!(node.attrs.custom==='button')){
                //calls super method
                this._super($el,node);
            }
    },
    });
    });

});