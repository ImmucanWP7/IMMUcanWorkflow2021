#!/bin/bash

# Check if path is supplied
if [ -z "$1" ]
then
	echo "Please specify a path to the alignment folder"
	exit 1
fi

# Check if path contains 'zip_files'
if [ ! -d "$1/zip_files" ]
then
	echo "'zip_files' folder does not exist"
        exit 1
fi

# Create folder structure
if [ ! -d "$1/csv_coordinates" ]
then
        mkdir "$1/csv_coordinates"
fi

if [ ! -d "$1/csv_coordinates_transformed" ]
then
        mkdir "$1/csv_coordinates_transformed"
fi

if [ ! -d "$1/czi_to_mcd_transformation" ]
then
        mkdir "$1/czi_to_mcd_transformation"
fi

if [ ! -d "$1/IF_images" ]
then
        mkdir "$1/IF_images"
	mkdir "$1/IF_images/aligned"
fi

if [ ! -d "$1/jpg_to_czi_transformation" ]
then
        mkdir "$1/jpg_to_czi_transformation"
fi

if [ ! -d "$1/mcd_files" ]
then
        mkdir "$1/mcd_files"
fi

if [ ! -d "$1/Slidescanner" ]
then
        mkdir "$1/Slidescanner"
fi

if [ ! -d "$1/control_points" ]
then
        mkdir "$1/control_points"
fi

if [ ! -d "$1/control_points_posttransformation" ]
then
        mkdir "$1/control_points_posttransformation"
fi

# Unzip files
for f in $1/zip_files/*.zip
do
	
	cur_name=$(basename -- "$f")
	cur_name="${cur_name%.*}" 
        
	file_count=$(find $1/IF_images -name $cur_name.jpg | wc -l)

	if [[ $file_count -eq 0 ]]; then
		unzip -q $f -d $1/zip_files	
		mv $1/zip_files/$cur_name.jpg $1/IF_images
		mv $1/zip_files/$cur_name.csv $1/csv_coordinates
	fi
done

