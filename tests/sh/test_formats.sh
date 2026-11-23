#!/bin/bash
#
# The formats in project.sh, the exporters in scripts/ and the README agree:
# every format has an exporter that writes its own file, every exporter is
# listed, the README's Formats table names every format, and its count of
# formats is right. Formats that keep layers are the ones the README names.
#
# Run from anywhere: bash tests/sh/test_formats.sh

# shellcheck source=tests/sh/lib.sh
. "$(dirname "$0")/lib.sh"
cd "$ROOT" || exit 1

mapfile -t known < <(formats)

if [ "${#known[@]}" -lt 40 ]; then
    fail "read the FORMATS of project.sh, got ${#known[@]}: ${known[*]}"
fi

for format in "${known[@]}"; do
    script="scripts/export$format.py"
    if [ ! -f "$script" ]; then
        fail "$format has no $script"
        continue
    fi
    check "$script writes .$format" grep -qF "output + \".$format\"" "$script"
    check "$script writes into build/" grep -qF 'load_project("build"' "$script"
    check "the README lists $format" grep -qE "^\|.*\`$format\`" README.md
done

for script in scripts/export*.py; do
    format=${script#scripts/export}
    format=${format%.py}
    listed=no
    for name in "${known[@]}"; do
        [ "$name" = "$format" ] && listed=yes
    done
    check "$script is in the FORMATS of project.sh" [ "$listed" = yes ]
done

check "scripts/savexcf.py saves the layered XCF into xcf/" \
    grep -qF 'load_project("xcf", flatten=False)' scripts/savexcf.py
check "the README lists xcf" grep -qE "^\|.*\`xcf\`" README.md

# the README says xcf, psd and ora keep the layers: exactly those don't flatten
layered=$(grep -l 'flatten=False' scripts/export*.py scripts/savexcf.py \
    | sed -E 's#scripts/(export|save)##; s#\.py$##' | sort | paste -sd' ')
check "only ora, psd and xcf keep the layers (got: $layered)" [ "$layered" = "ora psd xcf" ]

# every format and the XCF
outputs=$(( ${#known[@]} + 1 ))
readme=$(tr '\n' ' ' < README.md)
check "the README counts $outputs formats" grep -qE "$outputs formats in all.*\*\*$outputs outputs\.\*\*" <<< "$readme"

finish
