#!/bin/bash
# Script to generate ome.tiff files for easy alignment with mIF images

shopt -s expand_aliases
alias steinbock="docker run -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/forJulien:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.13.5"

steinbock preprocess imc panel --namecol Clean_Target

steinbock preprocess imc images --hpf 50

steinbock export ome
