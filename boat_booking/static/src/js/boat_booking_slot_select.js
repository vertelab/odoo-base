/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.bookingSlotSelect.include({
    /**
     * @override
     */
    _onRefresh: function () {
        const result = this._super.apply(this, arguments);
        if (this.el.classList.contains('o_boat_booking')) {
            // _onRefresh is async, so we wait for it to finish
            result.then(() => {
                this.el.dispatchEvent(new CustomEvent('boat_booking_refresh_map', {
                    bubbles: true,
                    composed: true,
                }));
            });
        }
        return result;
    },

    /**
     * @override
     */
    _onClickHoursSlot: function (ev) {
        if (!this.el.classList.contains('o_boat_booking')) {
            return this._super.apply(this, arguments);
        }

        this.el
            .querySelector(".o_slot_hours.o_slot_hours_selected")
            ?.classList.remove("o_slot_hours_selected", "active");
        ev.currentTarget.classList.add("o_slot_hours_selected", "active");

        const availableResourcesData = ev.currentTarget.dataset.availableResources;
        const availableResources = availableResourcesData ? JSON.parse(availableResourcesData) : [];
        const availableResourceIds = availableResources.map(r => r.id);

        this.el.dispatchEvent(new CustomEvent('boat_booking_update_map_availability', {
            bubbles: true,
            composed: true,
            detail: {
                resourceIds: availableResourceIds,
            }
        }));
    },
});
