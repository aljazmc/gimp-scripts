#!/bin/bash
#
# project.sh names its outputs as the README says, and its clean commands
# remove exactly those: build/<project>.<format>, and xcf/<project>.xcf for
# the layered GIMP image.
#
# Runs in a sandbox (see lib.sh), so it never touches the real build/ or xcf/.
# Run from anywhere: bash tests/sh/test_outputs.sh

# shellcheck source=tests/sh/lib.sh
. "$(dirname "$0")/lib.sh"
sandbox

# expect_outputs <project> <format> <file>: clean removes the file and no other
expect_outputs() {

    mkdir -p build xcf
    touch "$3" build/keep.png xcf/keep.xcf build/nature-fern01.jpg
    ./project.sh "$1" "$2" clean > /dev/null 2>&1
    if [ -e "$3" ]; then
        fail "./project.sh $1 $2 clean should remove $3"
    elif [ ! -e build/keep.png ] || [ ! -e xcf/keep.xcf ] || [ ! -e build/nature-fern01.jpg ]; then
        fail "./project.sh $1 $2 clean removed other files"
    else
        pass "$1 $2 -> $3"
    fi
    rm -rf build xcf

}

expect_outputs cyberpunk-butterfly00 png build/cyberpunk-butterfly00.png
expect_outputs cyberpunk-butterfly00 psd build/cyberpunk-butterfly00.psd
expect_outputs cyberpunk-butterfly00 xcf xcf/cyberpunk-butterfly00.xcf
expect_outputs cyberpunk-butterfly00 h build/cyberpunk-butterfly00.h
expect_outputs steampunk-gear02 icns build/steampunk-gear02.icns

# <project> clean removes every output of that project
mkdir -p build xcf
while IFS= read -r format; do
    touch "build/cyberpunk-butterfly00.$format"
done < <(formats)
touch xcf/cyberpunk-butterfly00.xcf build/nature-fern01.png
./project.sh cyberpunk-butterfly00 clean > /dev/null 2>&1
check "<project> clean removes all its outputs" \
    [ -z "$(find build xcf -name 'cyberpunk-butterfly00*')" ]
check "<project> clean keeps other projects' outputs" [ -e build/nature-fern01.png ]

./project.sh clean > /dev/null 2>&1
check "clean removes build/" [ ! -e build ]
check "clean removes xcf/" [ ! -e xcf ]

finish
