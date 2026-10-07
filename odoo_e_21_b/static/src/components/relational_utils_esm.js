/** @odoo-module **/

import {Many2XAutocomplete} from "@web/views/fields/relational_utils";
import {patch} from "@web/core/utils/patch";
import {sprintf} from "@web/core/utils/strings";
import {useService} from "@web/core/utils/hooks";
const {Component, onWillStart} = owl;

patch(Many2XAutocomplete.prototype, {
    setup() {
        console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        this._super(...arguments);
        this.user = useService("user");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.ir_options = await this.user.hasGroup('odoo_e_21_b.master_access_control');
        });

    },

    async loadOptionsSource(request) {

        if (this.lastProm) {
            console.log("111111111111111111111111111111111111111111111111111111111111111")
            this.lastProm.abort(false);
        }
        this.lastProm = this.orm.call(this.props.resModel, "name_search", [], {
            name: request,
            operator: "ilike",
            args: this.props.getDomain(),
            limit: this.props.searchLimit + 1,
            context: this.props.context,
        });
        const records = await this.lastProm;
        console.log("2222222222222222222222222222222222222222222222222222222222222222222222222")

        const options = records.map((result) => ({
            value: result[0],
            label: result[1].split("\n")[0],
        }));

        if (this.props.quickCreate && request.length && this.ir_options) {
            console.log("3333333333333333333333333333333333333333333333333333333333333333")
            options.push({
                label: sprintf(this.env._t(`Create "%s"`), request),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_create",
                action: async (params) => {
                    try {
                        await this.props.quickCreate(request, params);
                    } catch (e) {
                        if (e && e.name === "RPC_ERROR") {
                            const context = this.getCreationContext(request);
                            return this.openMany2X({ context });
                        }
                        // Compatibility with legacy code
                        if (e && e.message && e.message.name === "RPC_ERROR") {
                            // The event.preventDefault() is necessary because we still use the legacy
                            e.event.preventDefault();
                            const context = this.getCreationContext(request);
                            return this.openMany2X({ context });
                        }
                        throw e;
                    }
                },
            });
        }

        if (!this.props.noSearchMore && this.props.searchLimit < records.length) {
            console.log("444444444444444444444444444444444444444444444444444444444444444")
            options.push({
                label: this.env._t("Search More..."),
                action: this.onSearchMore.bind(this, request),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_search_more",
            });
        }

        const canCreateEdit =
            "createEdit" in this.activeActions
                ? this.activeActions.createEdit
                : this.activeActions.create;
        if (!request.length && !this.props.value && (this.props.quickCreate || canCreateEdit)) {
            console.log("5555555555555555555555555555555555555555555555555555555555555555555555555555")
            options.push({
                label: this.env._t("Start typing..."),
                classList: "o_m2o_start_typing",
                unselectable: true,
            });
        }

        if (request.length && canCreateEdit && this.ir_options) {
            console.log("666666666666666666666666666666666666666666")
            const context = this.getCreationContext(request);
            options.push({
                label: this.env._t("Create and edit..."),
                classList: "o_m2o_dropdown_option o_m2o_dropdown_option_create_edit",
                action: () => this.openMany2X({ context }),
            });
        }

        if (!records.length && !this.activeActions.create) {
            options.push({
                label: this.env._t("No records"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }

        return options;
    }
});





Many2XAutocomplete.defaultProps = {
    ...Many2XAutocomplete.defaultProps,
    nodeOptions: {},
};
