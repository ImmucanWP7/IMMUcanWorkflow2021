#!/bin/bash

shopt -s expand_aliases
alias steinbock="docker run -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/mIF/steinbock:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.14.2"

steinbock segment deepcell --minmax

steinbock measure intensities --masks masks -o intensities
steinbock measure regionprops --masks masks -o regionprops
steinbock measure neighbors --type expansion --dmax 4 --masks masks -o neighbors
