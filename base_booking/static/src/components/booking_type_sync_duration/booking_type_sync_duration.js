import { onWillStart } from "@odoo/owl";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { registry } from "@web/core/registry";
import { useRecordObserver } from "@web/model/relational_model/utils";


export class BookingTypeSyncDuration extends Many2OneField {
    setup() {
        super.setup();
        this.bookingTypeId = this.props.record.data.booking_type_id[0];
        this.isDefaultDuration = false;

        onWillStart(async () => {
            if (this.bookingTypeId) {
                const bookingDuration = await this.orm.read(
                    "booking.type", [this.bookingTypeId], ['booking_duration']
                );
                this.isDefaultDuration = this.props.record.data.duration === bookingDuration?.[0].booking_duration;
            }
        });

        useRecordObserver(async (record) => {
            if (record.data.booking_type_id[0] !== this.bookingTypeId && this.isDefaultDuration) {
                this.bookingTypeId = record.data.booking_type_id[0];
                if (this.bookingTypeId) {
                    const bookingDuration = await this.orm.read(
                        "booking.type", [this.bookingTypeId], ['booking_duration']
                    );
                    if (bookingDuration.length !== 0) {
                        record.update({'duration': bookingDuration[0].booking_duration});
                    }
                }
            }
        });
    }
}

registry.category("fields").add("booking_type_sync_duration", {
    ...many2OneField,
    component: BookingTypeSyncDuration,
});
