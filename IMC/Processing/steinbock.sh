#!/bin/bash

shopt -s expand_aliases
alias steinbock="docker run -v /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC:/data -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/.Xauthority:/home/steinbock/.Xauthority:ro -u $(id -u):$(id -g) -e DISPLAY ghcr.io/bodenmillergroup/steinbock:0.13.5"

steinbock preprocess imc panel --namecol Clean_Target

steinbock preprocess imc images --hpf 50 &> /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC/steinbock_img_log.txt 

steinbock segment deepcell --minmax

steinbock segment deepcell --minmax --type nuclear -o masks_nucleus
cp NuclearExpansion.cppipe /mnt/immucan_volume/processed_data/Panel_1/2022_WORKFLOW/IMC
steinbock apps cellprofiler -p NuclearExpansion.cppipe -i masks_nucleus -c -r

steinbock measure intensities --masks masks -o intensities
steinbock measure regionprops --masks masks -o regionprops
steinbock measure neighbors --type expansion --dmax 4 --masks masks -o neighbors

steinbock measure intensities --masks masks_expanded -o intensities_expansion
steinbock measure regionprops --masks masks_expanded -o regionprops_expansion
steinbock measure neighbors --type expansion --dmax 4 --masks masks_expanded -o neighbors_expansion
