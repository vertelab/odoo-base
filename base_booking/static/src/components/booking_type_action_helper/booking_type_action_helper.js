/** @odoo-module **/

import { useService } from '@web/core/utils/hooks';
import { Component, onWillStart } from '@odoo/owl';

export class BookingTypeActionHelper extends Component {
    static template = 'base_booking.BookingTypeActionHelper';
    static props = {};

    setup() {
        this.orm = useService('orm');
        this.action = useService('action');

        onWillStart(async () => {
            this.bookingTypeTemplateData = await this.orm.call(
                'booking.type',
                'get_booking_type_templates_data',
                []
            );
        });
    }

    async onTemplateClick(templateInfo) {
        const action = await this.orm.call(
            'booking.type',
            'action_setup_booking_type_template',
            [templateInfo.template_key],
        );
        this.action.doAction(action);
    }
};
