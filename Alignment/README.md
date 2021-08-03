# IF to IMC alignment 

This folder contains relevant scripts to perform pre- and post-processing of files for IF to IMC region alignment.
We also give instructions here, how alignment is done.

## Setting up the environment

In the first instance, [napping](https://github.com/BodenmillerGroup/napping) needs to be installed via a `conda` environment.
To recreate the alignment, we provide the used environment here. 
Please set it up via:

```
conda env create -f environment.yml
```

## Preparing the files

For the alignment process, it is recommended to create an `alignment_folder` where all files will be stored.
Within the `alignment_folder`, a folder called `zip_files` needs to be created:

```
mkdir alignment_folder
mkdir alignment_folder/zip_files
```

After region selection, you will have obtained .zip files containing the whole slide .jpg files of the IF and .csv files containing the coordinates of the selected regions in the IF coordinate system.
These files need to be saved in `alignment_folder/zip_files`. 

In the following paragraphs, we will refer to certain types of image files by their extensions: whole slide IF images are refered to as `.jpg`, whole slide bright field images are refered to as `.czi` and overview panorama scans of the slides for IMC acquisition are refered to as `.mcd`.

The `processing/create_folders.sh` script will create an ideal folder structure for image alignment, will unzip the downloaded files and distribute the individual files into their dedicated folders.
The script can be execuded via:

```
processing/create_folders.sh path/to/alignment_folder
```

This script creates the following folders:

* control_points: storing control points set for the .jpg to .czi transformation  
* control_points_posttransformation: storing control points set for the .czi to .mcd transformation  
* csv_coordinates: .csv files containing the centers of selected regions in the .jpg coordinate system  
* csv_coordinates_transformed: .csv files containing the transformed centers of selected regions in the .mcd coordinate system  
* czi_to_mcd_transformation: .pickle files containg the transformation matrix used to transform cooridinates from the .czi cooridnate system to the .mcd coordinate system  
* IF_images: containing the whole slide IF images in .jpg format. The `alignment` subfolder can be used to keep track on which images were already aligned  
* jpg_to_czi_transformation: .pickel files containing the transformation matrix to transform coordinates from the .jpg coordinate system to the .czi coordinate system  
* mcd_files: stores .mcd files containing the panoramas  
* Slidescanner: this folder should contain the whole slide bright field images in .czi format  
