/** @odoo-module */

odoo.define('workflow_management.global_approval', function (require) {

const { usePopover } = require("@web/core/popover/popover_hook");
const { useService } = require("@web/core/utils/hooks");
const { globalApprovalInfos } = require("./approval_infos");
const { Component, onWillUnmount, useRef } = require("@odoo/owl");


function useOpenExternal() {
    const closeFns = [];
    function open(_open) {
        const close = _open();
        closeFns.push(close);
        return close;
    }

    onWillUnmount(() => {
        closeFns.forEach((cb) => cb());
    });
    return open;
}

export class globalApproval extends Component {
    static props = {
        approval: Object,
    };
    static template = "globalApproval";

    setup() {
        this.dialog = useService("dialog");
        this.popover = usePopover(globalApprovalInfos);
        this.rootRef = useRef("root");
        this.openExternal = useOpenExternal();
    }

    get approval() {
        return this.props.approval;
    }

    get state() {
        return this.approval.state;
    }

    toggleApprovalInfo() {
        if (this.env.isSmall) {
            if (this.isOpened) {
                this.closeInfos();
                this.closeInfos = null;
                return;
            }
            const onClose = () => {
                this.isOpened = false;
            };
            this.closeInfos = this.openExternal(() =>
                this.dialog.add(
                    globalApprovalInfos,
                    { approval: this.approval, isPopover: false },
                    { onClose }
                )
            );
        } else {
            this.popover.open(this.rootRef.el, { approval: this.approval, isPopover: true });
        }
    }

    getEntry(ruleId) {
        return this.state.entries.find((e) => e.rule_id[0] === ruleId);
    }
}
});