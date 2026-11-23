#!/bin/bash
#
# project.sh runs GIMP the right way for each request: the console GIMP
# without its user interface, data, fonts or splash, never handing the batch
# to a running GIMP, with the export script on stdin, the project in PROJECT
# and scripts/ on the PYTHONPATH; for one project or all of them, from any
# directory. It skips outputs that exist, reports a failed export with exit
# code 1, and stops when GIMP is missing.
#
# Runs in a sandbox (see lib.sh) with a stand-in GIMP, so nothing is painted.
# Run from anywhere: bash tests/sh/test_run.sh

# shellcheck source=tests/sh/lib.sh
. "$(dirname "$0")/lib.sh"
sandbox

GIMP_ARGS="-i -d -f -s -n -c --batch-interpreter=python-fu-eval -b - --quit"

# expect_calls <description> <expected calls.log> -- <project.sh arguments>
expect_calls() {

    local description=$1 expected=$2
    shift 3
    : > calls.log
    ./project.sh "$@" > output.log 2>&1
    if [ "$(cat calls.log)" = "$expected" ]; then
        pass "$description"
    else
        fail "$description: ./project.sh $* ran"$'\n'"$(cat calls.log)"$'\n'"expected"$'\n'"$expected"
    fi

}

expect_calls "one project, one format, with the script on stdin" \
    "PROJECT=cyberpunk-butterfly00 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < exportpng.py" \
    -- cyberpunk-butterfly00 png

expect_calls "xcf runs savexcf.py" \
    "PROJECT=nature-fern01 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < savexcf.py" \
    -- nature-fern01 xcf

expect_calls "all runs every project, sorted" \
    "PROJECT=cyberpunk-butterfly00 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < exportjpg.py
PROJECT=nature-fern01 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < exportjpg.py
PROJECT=steampunk-gear02 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < exportjpg.py" \
    -- all jpg

: > calls.log
(cd / && "$SANDBOX/project.sh" nature-fern01 webp > /dev/null 2>&1)
check "it runs from any directory" \
    grep -qx "PROJECT=nature-fern01 PYTHONPATH=scripts gimp-console-3.0 $GIMP_ARGS < exportwebp.py" calls.log

: > calls.log
./project.sh steampunk-gear02 all > /dev/null 2>&1
count=$(formats | wc -l)
check "<project> all runs every format and xcf ($((count + 1)) runs)" \
    [ "$(wc -l < calls.log)" -eq $((count + 1)) ]
check "and each of them once" [ "$(sort -u calls.log | wc -l)" -eq $((count + 1)) ]

mkdir -p build
touch build/nature-fern01.gif
expect_calls "an existing output is skipped" "" -- nature-fern01 gif
check "and says so" grep -q "Skipping build/nature-fern01.gif" output.log
rm -rf build

GIMP_EXIT=64 ./project.sh all png > output.log 2>&1
code=$?
check "a failed export exits with 1" [ "$code" -eq 1 ]
check "and names the project" grep -q "FAILED: exportpng for nature-fern01" output.log
check "and goes on with the other projects" [ "$(grep -c FAILED output.log)" -eq 3 ]

# only the basic tools project.sh uses on the PATH, without GIMP
mkdir tools
for tool in bash find sort head paste dirname; do
    ln -s "$(command -v "$tool")" "tools/$tool"
done
PATH="$SANDBOX/tools" ./project.sh cyberpunk-butterfly00 png > output.log 2>&1
code=$?
check "without GIMP it exits with 1" [ "$code" -eq 1 ]
check "and names it" grep -q "gimp-console-3.0 is required" output.log

finish
