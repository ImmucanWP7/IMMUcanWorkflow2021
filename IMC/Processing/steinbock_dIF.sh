#!/bin/bash

shopt -s expand_aliases
alias steinbock="docker run -e STEINBOCK_MASK_DTYPE=float32 -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.14.1"

steinbock utils mosaics tile img_full --size 4096 -o img &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF/logs/tiling.txt

steinbock segment deepcell --minmax  &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF/logs/segmentation.txt

steinbock utils mosaics stitch masks -o masks_full --relabel  &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF/logs/stitching.txt

steinbock measure intensities --img img_full --masks masks_full  &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF/logs/intensities.txt
steinbock measure regionprops --img img_full --masks masks_full  &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/dIF/logs/regionsprops.txt
