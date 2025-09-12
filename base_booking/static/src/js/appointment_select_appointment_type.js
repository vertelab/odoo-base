/** @odoo-module **/

import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { debounce } from "@web/core/utils/timing";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.bookingTypeSelect = publicWidget.Widget.extend({
    selector: '.o_booking_choice',
    events: {
        'change select[id="booking_type_id"]': '_onBookingTypeChange',
        'click .o_booking_select_button': '_onBookingTypeSelected',
    },

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        // Check if we cannot replace this by a async handler once the related
        // task is merged in master
        this._onBookingTypeChange = debounce(this._onBookingTypeChange, 250);
    },

    /**
     * @override
     */
    start: function () {
        return this._super(...arguments).then(() => {
            // Load an image when no booking types are found
            this.el.querySelector(".o_booking_svg i")?.replaceWith(renderToElement('Booking.booking_svg', {}));
            this.el
                .querySelectorAll(".o_booking_not_found div")
                .forEach((el) => el.classList.remove("d-none"));
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * On booking type change: adapt booking intro text and available
     * users. (if option enabled)
     *
     * @override
     * @param {Event} ev
     */
    _onBookingTypeChange: function (ev) {
        var self = this;
        const bookingTypeID = ev.target.value;
        const filterBookingTypeIds = this.el.querySelector(
            "input[name='filter_booking_type_ids']"
        ).value;
        const filterUserIds = this.el.querySelector("input[name='filter_staff_user_ids']").value;
        const filterResourceIds = this.el.querySelector("input[name='filter_resource_ids']").value;
        const inviteToken = this.el.querySelector("input[name='invite_token']").value;

        rpc(`/booking/${bookingTypeID}/get_message_intro`, {
            invite_token: inviteToken,
            filter_booking_type_ids: filterBookingTypeIds,
            filter_staff_user_ids: filterUserIds,
            filter_resource_ids: filterResourceIds,
        }).then(function (message_intro) {
            const parsedElements = new DOMParser().parseFromString(message_intro, 'text/html').body.childNodes;
            self.el.querySelector(".o_booking_intro")?.replaceChildren(...parsedElements);
        });
    },

    _onBookingTypeSelected: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const optionSelected = this.el.querySelector('select').selectedOptions[0];
        window.location = optionSelected.dataset.bookingUrl;
    },
});
