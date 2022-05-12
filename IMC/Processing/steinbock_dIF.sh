#!/bin/bash

shopt -s expand_aliases
alias steinbock="docker run -e STEINBOCK_MASK_DTYPE=uint32 -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.13.5"

steinbock utils mosaics tile img_full --size 4096 -o img

steinbock segment deepcell --minmax

steinbock utils mosaics stitch masks -o masks_full --relabel

steinbock measure intensities --img img_full --masks masks_full
steinbock measure regionprops --img img_full --masks masks_full
