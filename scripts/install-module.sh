#!/bin/bash
# install-module.sh — install ONE module in an edition's test database and
# record the outcome as one line: <module> <edition> <OK|FAIL> <exception>.
#
# The error is read from the LOGFILE (odoo.conf's logfile), not stdout: Odoo
# exits 0 even when a module becomes `uninstallable` as a dependency, and
# stdout is truncated by the worker pool. The log is marked before each run so
# an old error is never read as a new one.
#
# Usage: install-module.sh <edition> <database> <module> [resultfile]
set -u

EDITION="${1:?edition}"
DB="${2:?database}"
MODULE="${3:?module}"
RESULT="${4:-/tmp/install-${EDITION}.txt}"

ROOT="/opt/odoo/pfile/${EDITION}"
ODOO="${ROOT}/src/odoo-bin"
PY="${ROOT}/venv/bin/python"
CONF="/etc/odoo/pfile/${EDITION}/odoo.conf"
LOG=$(sed -n 's/^logfile *= *//p' "$CONF" | head -1)
PORT=$((8000 + ${EDITION%%.*} * 10))

MARK="=== install-module ${MODULE} $(date -Is) ==="
sudo tee -a "$LOG" >/dev/null <<< "$MARK"

sudo -u odoo "$PY" "$ODOO" -c "$CONF" -d "$DB" -i "$MODULE" \
    --stop-after-init --http-port="$PORT" >/dev/null 2>&1

STATE=$(sudo -u postgres psql -d "$DB" -tAc \
    "select state from ir_module_module where name='${MODULE}'")
VERSION=$(sudo -u postgres psql -d "$DB" -tAc \
    "select latest_version from ir_module_module where name='${MODULE}'")

if [ "$STATE" = "installed" ]; then
    echo "${MODULE} ${EDITION} OK ${VERSION}" >> "$RESULT"
    echo "${MODULE} ${EDITION} OK ${VERSION}"
    exit 0
fi

# The reason: the last exception line after our mark, else the module-level
# warning that explains why it never got as far as running.
REASON=$(sudo awk -v mark="$MARK" '$0==mark{f=1;next} f' "$LOG" \
    | grep -E "ValueError|KeyError|ParseError|UserError|psycopg2\.|^[A-Za-z_.]+Error:" \
    | tail -1)
if [ -z "$REASON" ]; then
    REASON=$(sudo awk -v mark="$MARK" '$0==mark{f=1;next} f' "$LOG" \
        | grep -E "incompatible version|not installable|depends are not loaded|module .* not found" \
        | tail -1)
fi
[ -z "$REASON" ] && REASON="state=${STATE:-missing} (no exception in log)"

echo "${MODULE} ${EDITION} FAIL ${REASON}" >> "$RESULT"
echo "${MODULE} ${EDITION} FAIL ${REASON}"
exit 1
