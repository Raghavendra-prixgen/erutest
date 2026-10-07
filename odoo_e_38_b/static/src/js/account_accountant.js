/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useRef, onPatched  } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

class PivotHeaderFreeze extends Component {
        constructor() {
            super(...arguments);
            console.log('hshashsa');
            this.$pivot = useRef('pivot');
            console.log('hshashsa',this.$pivot);
            this.$thead = useRef('thead');
        }
        mounted() {
            this.$pivot.addEventListener('scroll', this._onPivotScroll.bind(this));
        }

        willUnmount() {
            this.$pivot.removeEventListener('scroll', this._onPivotScroll.bind(this));
        }

        _onPivotScroll() {
            this.$thead.style.transform = `translateY(${this.$pivot.scrollTop}px)`;
        }
    }

    PivotHeaderFreeze.template = 'odoo_e_38_b.PivotHeaderFreeze';
    PivotHeaderFreeze.components = {};

    return PivotHeaderFreeze;
