def migrate(cr, version):
    # Odoo 18 removed the client action 'apps.updates' from the JS registry.
    # Clean up any stale database records migrated from older versions.
    cr.execute("SELECT id, tag FROM ir_actions_client WHERE tag = 'apps.updates'")
    stale_ids = [r[0] for r in cr.fetchall()]
    if stale_ids:
        # Remove menu items pointing to the stale action
        for aid in stale_ids:
            cr.execute(
                "DELETE FROM ir_ui_menu WHERE action = %s",
                [f'ir.actions.client,{aid}']
            )
        # Remove the stale client action itself
        cr.execute(
            "DELETE FROM ir_actions_client WHERE id = ANY(%s)",
            [stale_ids]
        )
