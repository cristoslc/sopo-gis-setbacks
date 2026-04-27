#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Install local pre-commit PII + safety hook
cat > "${ROOT_DIR}/.git/hooks/pre-commit" << 'HOOKEOF'
#!/bin/bash
set -euo pipefail

# --- PII blocker (personal) ---
STAGED=$(git diff --cached --name-only --diff-filter=ACM)
if [ -n "$STAGED" ]; then
    # Filter out known dataset / binary extensions
    FILTERED=$(echo "$STAGED" | grep -v -i -E '\.(geojson|csv|shp|shx|dbf|prj|cpg|tif|tiff|jpg|jpeg|png|gif|pdf|zip|xlsx?|mbtiles|las|laz|gdb)$' || true)
    # Also filter out large package-lock style files
    FILTERED=$(echo "$FILTERED" | grep -v -E '(package-lock\.json|yarn\.lock|Pipfile\.lock)$' || true)
    if [ -n "$FILTERED" ]; then
        ROOT=$(git rev-parse --show-toplevel)
        if [ -f "$ROOT/scripts/check_pii.py" ]; then
            echo "$FILTERED" | tr '\n' '\0' | xargs -0 python3 "$ROOT/scripts/check_pii.py"
        fi
    fi
fi

# --- Delegate to pre-commit if installed ---
if command -v pre-commit >/dev/null 2>&1; then
    echo "Running pre-commit..."
    pre-commit run --show-diff-on-failure
fi
HOOKEOF

chmod +x "${ROOT_DIR}/.git/hooks/pre-commit"
echo "Installed .git/hooks/pre-commit"
