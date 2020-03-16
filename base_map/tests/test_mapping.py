from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged('base_map')
class TestMapping(TransactionCase):

    def setUp(self):
        super(TestMapping, self).setUp()

    def test_1_create_partner ():
        # Create a res.partner
        self.partner = self.env['res.partner'].create({
            'company_id': self.env.ref("base.main_company").id,
            'name': "Crm Sales manager",
            'login': "csm",
            'email': "crmmanager@yourcompany.com",
            'groups_id': [(6, 0, [self.ref('sales_team.group_sale_manager')])]
        })
