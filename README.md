# IMMUcanWorkflow2021

This repo contains code to reproduce figures from the publication ...

## Background

[IMMUcan](https://immucan.eu/) is a large IMI funded consortium with the goal to
characterize samples from close to 3000 cancer patients from 5 cancer
indications. We apply H&E staining, whole slide immunofluorescence (mIF),
Imaging Mass Cytometry (IMC), bulk RNAseq and whole-exome Seq to FFPE sections
from all patient samples. To generate workflows compatible with the throughput
of the project two pipelines consisting of optimized experimental and
computational procedures were generated for mIF and IMC. Here we provide code to
reproduce the figures from the publication.
The IMC data has been processed using
[steinbock](https://github.com/BodenmillerGroup/steinbock) and for analysis we
generally followed the workflow as explained in detail in the [IMCDataAnalysis
book](https://bodenmillergroup.github.io/IMCDataAnalysis/)

## Data repositories

### Data for publication

1. data to reproduce all figures from the original publication: [Zenodo](https://zenodo.org/records/13132656)

### Accompanying data repositories

2. whole slide mIF qptiff files from 10 patients [Zenodo](https://zenodo.org/records/12699335)
3. data for IMC panel 1 cell type classification [Zenodo](https://zenodo.org/records/12912567)

## Accompanying code repositories

- [IFQuant](https://github.com/BICC-UNIL-EPFL/IFQuant)
- [IMC panel 1 cell type classifier](https://github.com/ImmucanWP7/IMMUcan_IMC_panel_1_cell_type_classifier)

## Figure reproduction

Please download Zenodo repo 1 and keep the structure of the folders. Clone this
repo and modify the file `mount_path` under `data` to be the path to the
directory containing all the data from Zenodo to execute the code.

A [workflowr][] project.
[workflowr]: https://github.com/workflowr/workflowr
