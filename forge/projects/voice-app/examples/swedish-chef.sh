#!/bin/bash
# Swedish Chef post-processing script for Voxtype
#
# Toorns ell ooff yuoor deecteshun into-a Svedeesh Cheff speek! Bork bork bork!
#
# Usage: Configure in ~/.config/voxtype/config.toml:
#   [output.post_process]
#   command = "/path/to/swedish-chef.sh"
#   timeout_ms = 1000

INPUT=$(cat)

# Transform text to Swedish Chef speak using sed
# Based on classic Swedish Chef linguistic patterns
echo "$INPUT" | sed \
    -e 's/\bthe\b/zee/gi' \
    -e 's/\bThe\b/Zee/g' \
    -e 's/tion\b/shun/gi' \
    -e 's/\ban\b/un/gi' \
    -e 's/\bAn\b/Un/g' \
    -e 's/\ba\b/a/gi' \
    -e 's/\bu\b/oo/gi' \
    -e 's/\bU\b/Oo/g' \
    -e 's/ore\b/oore-a/gi' \
    -e 's/ore /oore-a /gi' \
    -e 's/ir\b/ur/gi' \
    -e 's/en\b/ee/gi' \
    -e 's/ew/oo/gi' \
    -e 's/\bi\b/i/gi' \
    -e 's/ow/oo/gi' \
    -e 's/o\b/oo/gi' \
    -e 's/O\b/Oo/g' \
    -e 's/v/f/g' \
    -e 's/V/F/g' \
    -e 's/w/v/g' \
    -e 's/W/V/g' \
    | sed 's/$/ Bork bork bork!/'
