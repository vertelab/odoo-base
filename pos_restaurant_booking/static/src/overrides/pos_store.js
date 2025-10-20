import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { deduceUrl, random5Chars, uuidv4, getOnNotified } from "@pos_restaurant_booking/utils";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);

        await this.initServerData();
        if (this.useProxy()) {
            await this.connectToProxy();
        }

        this.onNotified("TABLE_BOOKING", (payload) => {
            const { command, event } = payload;
            console.log("command", command)
            console.log("event", event)
            if (!event) {
                return;
            }
            if (command === "ADDED") {
                this.models.loadData({ "calendar.event": [event] });
            } else if (command === "REMOVED") {
                this.models["calendar.event"].get(event.id)?.delete?.();
            }
        });
    },
    async manageBookings() {
        this.orderToTransferUuid = null;
        this.showScreen("ActionScreen", { actionName: "ManageBookings" });
        await this.action.doAction(
            await this.data.call("calendar.event", "action_open_booking_calendar_view", [
                this.config.raw.booking_type_id,
            ])
        );
    },
    async editBooking(appointment) {
        const action = await this.data.call("calendar.event", "action_open_booking_form_view", [
            appointment.id,
        ]);
        return this.action.doAction(action);
    },

    async initServerData() {
        await this.processServerData();
        this.onNotified = getOnNotified(this.bus, this.config.access_token);
        return await this.afterProcessServerData();
    }
});
