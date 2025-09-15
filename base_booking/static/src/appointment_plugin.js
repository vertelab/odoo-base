import { _t } from "@web/core/l10n/translation";
import { Plugin } from "@html_editor/plugin";
import { MAIN_PLUGINS } from "@html_editor/plugin_sets";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";

class BookingFormViewDialog extends FormViewDialog {
    static props = {
        ...FormViewDialog.props,
        insertLink: { type: Function },
    };
    setup() {
        super.setup();
        this.viewProps.insertLink = this.props.insertLink;
        this.viewProps.closeDialog = this.props.close;
    }
}

class BookingPlugin extends Plugin {
    static id = "booking";
    static dependencies = ["selection", "link", "dialog"];
     resources = {
        user_commands: [
            {
                id: "insertBooking",
                title: _t("Booking"),
                description: _t("Add a specific booking"),
                icon: "fa-calendar",
                run: this.addBooking.bind(this),
            },
        ],
        powerbox_items: [
            {
                categoryId: "navigation",
                commandId: "insertBooking",
            },
        ],
    };

    addBooking() {
        this.dependencies.dialog.addDialog(BookingFormViewDialog, {
            resModel: "base_booking.invite",
            context: {
                form_view_ref: "base_booking.booking_invite_view_form_insert_link",
                default_booking_type_ids: [],
                default_staff_user_ids: [],
            },
            size: "md",
            title: _t("Insert Booking Link"),
            mode: "edit",
            insertLink: (url) =>
                this.dependencies.link.insertLink(url, _t("Schedule an Booking")),
        });
    }
}

// add booking plugin for all standard use cases
MAIN_PLUGINS.push(BookingPlugin);
