odoo.define('tree_menu.tree_view_button', function (require){
"use strict";
 
 
var core = require('web.core');
var ListView = require('web.ListView');
var QWeb = core.qweb;

ListView.include({       
     
        render_buttons: function($node) {
                var self = this;
                this._super($node);
                    this.$buttons.find('.o_list_tender_button_create').click(this.proxy('tree_view_action'));
        },
 
        tree_view_action: function () {  
    
                var rawDateTo = $('#dateTo').val();
                var rawDateFrom = $('#dateFrom').val();

                var reqDateTo = rawDateTo.split('/');
                var reqDateFrom = rawDateFrom.split('/');

                var dateTo = reqDateTo[1].concat('/',reqDateTo[0],'/',reqDateTo[2]);
                var dateFrom = reqDateFrom[1].concat('/',reqDateFrom[0],'/',reqDateFrom[2]);

        return this.do_action({          
                name: "Filtered Invoice(s)",       
                res_model: "account.invoice",               
                domain : [['date_invoice','>=',dateTo],['date_invoice','<=',dateFrom]],
                views: [[false, "list"],[false, "tree"],[false, "form"]],              
                type: "ir.actions.act_window",               
                view_type : "list",
                view_mode : "list",
        });
    },
 
});
 
});

