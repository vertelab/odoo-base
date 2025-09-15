import { patch } from "@web/core/utils/patch";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { useSubEnv } from "@odoo/owl";
import { getMin } from "@point_of_sale/utils";
import { deserializeDateTime, serializeDateTime } from "@web/core/l10n/dates";
const { DateTime } = luxon;

patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);
        useSubEnv({ position: {} });
    },
    async _createTableHelper() {
        const table = await super._createTableHelper(...arguments);
        const bookingResource = this.pos.models["booking.resource"].get(
            table.booking_resource_id?.id
        );

        if (!bookingResource) {
            await this.pos.data.searchRead(
                "booking.resource",
                [["pos_table_ids", "in", table.id]],
                this.pos.data.fields["booking.resource"],
                { limit: 1 }
            );
        }

        return table;
    },
    async duplicateTableOrFloor() {
        await super.duplicateTableOrFloor(...arguments);
        if (this.selectedTables.length == 0) {
            const tableWoBooking = [];

            for (const table of this.activeTables) {
                const bookingResource = this.pos.models["booking.resource"].get(
                    table.booking_resource_id?.id
                );

                if (!bookingResource) {
                    tableWoBooking.push(table.id);
                }
            }

            if (tableWoBooking.length > 0) {
                await this.pos.data.searchRead(
                    "booking.resource",
                    [["pos_table_ids", "in", tableWoBooking]],
                    this.pos.data.fields["booking.resource"]
                );
            }
        }
    },
    async createTableFromRaw(table) {
        delete table.booking_resource_id;
        return super.createTableFromRaw(table);
    },

    getFirstBooking(table) {
        if (!table.booking_resource_id) {
            return false;
        }

        const bookings = this.pos.models["calendar.event"].filter(
            (booking) => booking.booking_resource_ids.includes(table.booking_resource_id)
        );

        if (!bookings) {
            return false;
        }
        const startOfToday = DateTime.now().set({ hours: 0, minutes: 0, seconds: 0 });
        bookings.map((booking) => {
            if (
                deserializeDateTime(booking.start).toFormat("yyyy-MM-dd") <
                DateTime.now().toFormat("yyyy-MM-dd")
            ) {
                booking.start = serializeDateTime(startOfToday);
            }
        });
        const dt_now = DateTime.now();
        const dt_tomorrow_ts = dt_now
            .plus({ days: 1 })
            .set({ hours: 0, minutes: 0, seconds: 0 }).ts;
        const possible_bookings = bookings.filter((a) => {
            const ts_now = dt_now - (a.duration / 2) * 3600000;
            const dt_ts = deserializeDateTime(a.start).ts;
            return dt_ts > ts_now && dt_ts < dt_tomorrow_ts;
        });
        if (possible_bookings.length === 0) {
            return false;
        }
        return getMin(possible_bookings, {
            criterion: (a) => deserializeDateTime(a.start).ts,
        });
    },
    getFormatedDate(date) {
        return deserializeDateTime(date).toFormat("HH:mm");
    },
    isCustomerLate(table) {
        const dateNow = DateTime.now();
        const dateStart = deserializeDateTime(this.getFirstBooking(table)?.start).ts;
        return (
            dateNow > dateStart && this.getFirstBooking(table).booking_status === "booked"
        );
    },
    bookingStarted(table) {
        return (
            this.getFirstBooking(table) &&
            deserializeDateTime(this.getFirstBooking(table).start).ts < DateTime.now().ts
        );
    },
    onClickBooking(ev, table) {
        if (!this.pos.isEditMode) {
            ev.stopPropagation();
            return this.pos.editBooking(this.getFirstBooking(table));
        }
    },
});
