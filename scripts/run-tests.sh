#!/bin/bash
# run-tests.sh — run one module's tests in an edition's test database and
# record the outcome: <module> <edition> <PASS|FAIL> <failed>/<errors>/<total>
set -u
EDITION="${1:?}"; DB="${2:?}"; MODULE="${3:?}"; RESULT="${4:-/tmp/tests-${EDITION}.txt}"
ROOT="/opt/odoo/pfile/${EDITION}"
LOG=$(sed -n 's/^logfile *= *//p' "/etc/odoo/pfile/${EDITION}/odoo.conf" | head -1)
PORT=$((8000 + ${EDITION%%.*} * 10))
MARK="=== run-tests ${MODULE} $(date -Is) ==="
sudo tee -a "$LOG" >/dev/null <<< "$MARK"
sudo -u odoo "${ROOT}/venv/bin/python" "${ROOT}/src/odoo-bin" \
    -c "/etc/odoo/pfile/${EDITION}/odoo.conf" -d "$DB" -u "$MODULE" \
    --test-tags="/${MODULE}" --stop-after-init --http-port="$PORT" --workers=0 \
    >/dev/null 2>&1
LINE=$(sudo awk -v mark="$MARK" '$0==mark{f=1;next} f' "$LOG" \
    | grep -E "failed, .* error\(s\) of [0-9]+ tests" | tail -1)
if [ -z "$LINE" ]; then
    echo "${MODULE} ${EDITION} FAIL no test summary" >> "$RESULT"
    echo "${MODULE} ${EDITION} FAIL no test summary"; exit 1
fi
FAILED=$(echo "$LINE" | sed -E 's/.*: ([0-9]+) failed, ([0-9]+) error\(s\) of ([0-9]+) tests.*/\1/')
ERRORS=$(echo "$LINE" | sed -E 's/.*: ([0-9]+) failed, ([0-9]+) error\(s\) of ([0-9]+) tests.*/\2/')
TOTAL=$(echo "$LINE" | sed -E 's/.*: ([0-9]+) failed, ([0-9]+) error\(s\) of ([0-9]+) tests.*/\3/')
if [ "$FAILED" = "0" ] && [ "$ERRORS" = "0" ]; then
    echo "${MODULE} ${EDITION} PASS ${FAILED}/${ERRORS}/${TOTAL}" >> "$RESULT"
    echo "${MODULE} ${EDITION} PASS ${FAILED}/${ERRORS}/${TOTAL}"
else
    echo "${MODULE} ${EDITION} FAIL ${FAILED}/${ERRORS}/${TOTAL}" >> "$RESULT"
    echo "${MODULE} ${EDITION} FAIL ${FAILED}/${ERRORS}/${TOTAL}"; exit 1
fi
