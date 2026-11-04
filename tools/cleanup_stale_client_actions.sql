-- ============================================================================
-- Odoo 18: Remove stale ir.actions.client records
-- ============================================================================
--
-- Usage:
--   psql -d <database> -f cleanup_stale_client_actions.sql
--   psql -d <database> -c "SELECT cleanup_stale_client_actions();"
--
-- What this does:
--   Deletes client actions whose 'tag' field does not match any JavaScript
--   registration in Odoo 18's "actions" registry.  These are leftovers from
--   older Odoo versions (e.g. 'apps.updates') and cause the browser error:
--     KeyNotFoundError: Cannot find key "..." in the "actions" registry
--
-- ============================================================================

-- List of valid client‑action tags registered in Odoo 18's JS actions registry.
-- Update this list when upgrading Odoo or adding custom modules.
CREATE OR REPLACE FUNCTION cleanup_stale_client_actions()
RETURNS TABLE(action_id INT, action_name VARCHAR, action_tag VARCHAR, action_deleted BOOLEAN)
LANGUAGE plpgsql AS $$
DECLARE
    valid_tags TEXT[] := ARRAY[
        -- Odoo 18 core (web)
        'home',
        'reload',
        'reload_context',
        'soft_reload',
        'display_notification',
        'install_kiosk_pwa',
        'import',
        -- Odoo 18 core (apps)
        'action_spreadsheet_dashboard',
        'backend_dashboard',
        'website_preview',
        'website_configurator',
        'website_view_hierarchy',
        'open_website_custom_menu',
        'event.event_barcode_scan_view',
        'mail.action_discuss',
        'mail.discuss_notification_settings_action',
        'mail.discuss_call_settings_action',
        'hr_attendance_greeting_message',
        'account_peppol.what_is_peppol',
        'generate_pricelist_report',
        'mrp_mo_overview',
        'mrp_display',
        'mrp_bom_report',
        'reception_report',
        'stock_forecasted',
        'stock_report_generic',
        'do_multi_print',
        'pos_qr_stands',
        'l10n_ke_post_send',
        -- Odoo 18 tests (will never appear in production)
        'someaction',
        '__test__client__action__',
        'TestClientAction',
        'clientAction',
        'clientActionNew',
        'my_component',
        'failing'
    ];
    r RECORD;
BEGIN
    FOR r IN
        SELECT id, name, tag FROM ir_actions_client
        WHERE tag IS NOT NULL
          AND tag <> ''
          AND NOT (tag = ANY(valid_tags))
        ORDER BY tag
    LOOP
        action_id := r.id;
        action_name := r.name;
        action_tag := r.tag;
        DELETE FROM ir_actions_client WHERE id = r.id;
        action_deleted := true;
        RETURN NEXT;
    END LOOP;
END;
$$;

-- Preview-only (no delete): what would be removed?
SELECT id, name, tag, create_date
FROM ir_actions_client
WHERE tag IS NOT NULL
  AND tag <> ''
  AND tag NOT IN (
    'home', 'reload', 'reload_context', 'soft_reload',
    'display_notification', 'install_kiosk_pwa', 'import',
    'action_spreadsheet_dashboard', 'backend_dashboard',
    'website_preview', 'website_configurator', 'website_view_hierarchy',
    'open_website_custom_menu',
    'event.event_barcode_scan_view',
    'mail.action_discuss', 'mail.discuss_notification_settings_action',
    'mail.discuss_call_settings_action',
    'hr_attendance_greeting_message',
    'account_peppol.what_is_peppol',
    'generate_pricelist_report',
    'mrp_mo_overview', 'mrp_display', 'mrp_bom_report',
    'reception_report', 'stock_forecasted', 'stock_report_generic',
    'do_multi_print', 'pos_qr_stands', 'l10n_ke_post_send',
    'someaction', '__test__client__action__', 'TestClientAction',
    'clientAction', 'clientActionNew', 'my_component', 'failing'
  )
ORDER BY tag;

-- To actually delete, uncomment:
-- SELECT cleanup_stale_client_actions();


 Kör mot vilken Odoo 18-databas som helst:

     # 1. Förhandsgranska vad som tas bort
     psql -d skog-test -f /path/to/cleanup_stale_client_actions.sql

     # 2. Om det ser rätt ut, kör själva rensningen
     psql -d skog-test -c "SELECT cleanup_stale_client_actions();"

     Skriptet:

     - Skapar en funktion cleanup_stale_client_actions() som raderar alla client actions vars tag inte matchar Odoo 18:s
       JS-registry
     - Visar först en SELECT-förhandsgranskning
     - Listan med valida tags uppdateras enkelt i toppen av filen när ni lägger till custom actions
