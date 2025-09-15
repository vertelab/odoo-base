/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { browser } from "@web/core/browser/browser";
import { registry } from '@web/core/registry';
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class BookingInviteCopyClose extends Component {
    static props = {
        ...standardWidgetProps,
    };
    static template = "base_booking.BookingInviteCopyClose";
    /**
     * We want to disable the "Save & Copy" button if there is a warning that could
     * result to have an incorrect/empty link.
     */
    setup() {
        this.notification = useService("notification");
    }
    /**
     * Save the invitation and copy the url in the clipboard
     * @param ev
     */
    async onSaveAndCopy(ev) {
        if (this.props.readonly) {
            return;
        }
        if (await this.props.record.save()) {
            const bookUrl = this.props.record.data.book_url;
            setTimeout(async () => {
                await browser.navigator.clipboard.writeText(bookUrl);
                this.notification.add(
                    _t("Link copied to clipboard!"),
                    { type: "success" }
                );
                this.env.dialogData.close();
                this.env.model.action.loadState();
            });
        }
    }
}

export const bookingInviteCopyClose = {
    component: BookingInviteCopyClose,
    fieldDependencies: [
        { name: "disable_save_button", type: "boolean" },
    ],
};
registry.category("view_widgets").add("booking_invite_copy_close", bookingInviteCopyClose);
