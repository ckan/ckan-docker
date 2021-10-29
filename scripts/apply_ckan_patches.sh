#!/bin/bash
shopt -s nullglob
for patch in patches/*.patch; do
    /usr/bin/patch -p0 -i $patch
done
