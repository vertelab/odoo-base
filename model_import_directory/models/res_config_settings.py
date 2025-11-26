
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    model_import_directory = fields.Char(
        string='Model Import Directory',
        config_parameter='model_import_directory',
        help="Path to a directory for loading Res Partners. "
    )
