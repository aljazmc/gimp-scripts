#!/bin/bash
#
# Helpers for the tests of project.sh: a sandbox with a copy of project.sh, a
# few fake projects and export scripts, and a stand-in for gimp-console-3.0,
# so a test can run project.sh without painting anything or touching build/
# and xcf/.
#
# Source it from a test: . "$(dirname "$0")/lib.sh"

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
failures=0

# Make a sandbox and cd into it. Each fake script in scripts/ holds only its
# own name, so the stand-in GIMP can tell which one it got on stdin. It writes
# each call, with PROJECT, PYTHONPATH, its arguments and that script, to
# calls.log, and exits with $GIMP_EXIT (default 0).
sandbox() {

    SANDBOX=$(mktemp -d)
    trap 'rm -rf "$SANDBOX"' EXIT
    cp "$ROOT/project.sh" "$SANDBOX/"
    cd "$SANDBOX" || exit 1

    local project format
    for project in cyberpunk-butterfly00 nature-fern01 steampunk-gear02; do
        mkdir -p "scripts/$project"
        touch "scripts/$project/${project##*-}.py"
    done
    while IFS= read -r format; do
        echo "export$format" > "scripts/export$format.py"
    done < <(formats)
    echo "savexcf" > scripts/savexcf.py

    mkdir bin
    cat > bin/gimp-console-3.0 <<'EOF'
#!/bin/bash
echo "PROJECT=$PROJECT PYTHONPATH=$PYTHONPATH gimp-console-3.0 $* < $(cat).py" >> calls.log
exit "${GIMP_EXIT:-0}"
EOF
    chmod +x bin/*
    PATH="$SANDBOX/bin:$PATH"
    : > calls.log

}

# the FORMATS array of project.sh, one per line, without running it
formats() {
    sed -n '/^FORMATS=(/,/^)/p' "${1:-$ROOT/project.sh}" | sed '1d;$d' | tr -s ' ' '\n' | sed '/^$/d'
}

pass() {
    echo "ok: $1"
}

fail() {
    echo "FAIL: $1" >&2
    failures=$((failures + 1))
}

# check <description> <command...>: passes if the command succeeds
check() {
    local description=$1
    shift
    if "$@"; then
        pass "$description"
    else
        fail "$description"
    fi
}

finish() {
    if [ "$failures" -gt 0 ]; then
        echo "FAILED: $failures" >&2
        exit 1
    fi
    echo "PASS"
}
