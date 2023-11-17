#!/bin/bash

shopt -s expand_aliases
alias steinbock="docker run -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.14.1"

steinbock preprocess imc panel --namecol Clean_Target

steinbock preprocess imc images --hpf 50 &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC/log/steinbock_img_log.txt 

# Remove one image due to imperfect alignment
rm /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC/img/IMMUcan_Batch20210921_10082495-SPECT-VAR-TIS-01-IMC-01_003.tiff

steinbock segment deepcell --minmax

steinbock measure intensities --masks masks -o intensities
steinbock measure regionprops --masks masks -o regionprops
steinbock measure neighbors --type expansion --dmax 4 --masks masks -o neighbors
