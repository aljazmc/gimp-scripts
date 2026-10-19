#!/bin/bash

GIMP=gimp-console-3.0

FORMATS=(
    avif bmp cel dcm dds eps exr ff fits fli gbr gif hdr heif icns ico jpg
    jxl ora pam pat pbm pcx pdf pfm pgm pix png pnm ppm ps psd qoi ras sgi
    tga tif webp xbm xpm xwd
)

cd "$(dirname "$0")" || exit 1

require() {

    local bin
    if bin=$(command -v "$1"); then
        echo "$1 found at: $bin"
    else
        echo "$1 is required but was not found" >&2
        exit 1
    fi

}

run() {

    require "$GIMP"
    mkdir -p build

    local script
    for script in scripts/*/$1; do
        [ -f "$script" ] || continue
        echo "Running $script"
        (
            cd "$(dirname "$script")" &&
            PYTHONPATH=. "$GIMP" -i --batch-interpreter=python-fu-eval -b - --quit < "$(basename "$script")"
        )
    done

}

build() {

    run "*.py"

}

clean() {

    rm -rf build

}

xcf() {

    run "savexcf.py"

}

export_format() {

    run "export$1.py"

}

usage() {

    local IFS="|"
    echo "You should use: $0 {build|clean|xcf|${FORMATS[*]}}" >&2
    exit 1

}

case "$1" in
    build|clean|xcf) "$1" ;;
    *)
        for format in "${FORMATS[@]}"; do
            [ "$1" = "$format" ] && { export_format "$1"; exit; }
        done
        usage
        ;;
esac
