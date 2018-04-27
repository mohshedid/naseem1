odoo.define('del_button.FormViewButton', function (require){
"use strict";

var core = require('web.core');
var FormView = require('web.FormView');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

FormView.include({

    render_buttons: function($node) {
            var self = this;
            this._super($node);
                this.$buttons.find('.deleting_button').click(this.proxy('new_view_action'));
                // this.$buttons.on('click', '.deleting_button', this.new_view_action);
    },

    new_view_action: function() {
        var self = this;
        var def = $.Deferred();
        this.has_been_loaded.done(function() {
            if (self.datarecord.id && confirm(_t("Do you really want to delete this record?"))) {
                self.dataset.unlink([self.datarecord.id]).done(function() {
                    if (self.dataset.size()) {
                        self.reload();
                        self.update_pager();
                    } else {
                        self.do_action('history_back');
                    }
                    def.resolve();
                });
            } else {
                utils.async_when().done(function () {
                    def.reject();
                });
            }
        });
        return def.promise();
    },
 
});
 
});

