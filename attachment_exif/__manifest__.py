{
    'name': 'Base: Attachment Exif',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Extract and display EXIF metadata from image attachments.',
    'description': """
    Attachment Exif
    ===============

    Extracts EXIF metadata from image attachments (JPEG, TIFF, etc.)
    and displays it in the attachment form view.
    Uses Pillow for EXIF reading — no additional dependencies required.
    """,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-base/attachment_exif',
    'license': 'AGPL-3',
    'repository': 'https://github.com/vertelab/odoo-base.git',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_attachment_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
