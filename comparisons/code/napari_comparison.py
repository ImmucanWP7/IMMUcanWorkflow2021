#!/usr/bin/env python

# Copyright (C) 2022 by Julien Dorier, BioInformatics Competence Center, University of Lausanne, Switzerland.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import argparse
import tifffile
import napari
import sys
import re
from matplotlib import colors
from xml.etree import ElementTree
from vispy.color import Colormap
import numpy as np
from qtpy.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QSlider, QScrollArea, QSpacerItem, QSizePolicy, QColorDialog, QRadioButton, QStyle
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor,QPixmap,QIcon

###########################################
# main function
###########################################
def napari_comparison(imc_image, 
                      imc_dir,
                      imc_panel, 
                      imc_cells,
                      mIF_image,
                      mIF_dir,
                      mIF_panel,
                      mIF_cells) -> None:

    ####################
    # viewer1 for mIF
    ####################
    viewer1 = napari.Viewer(title=mIF_dir)

    #hide "layer controls" and "layer list" docks
    viewer1.window._qt_viewer.dockLayerControls.hide()
    viewer1.window._qt_viewer.dockLayerList.hide()

    ####################
    #panel metadata
    ####################
    channel_names = mIF_panel.name[::-1].tolist()
    channel_colors = mIF_panel.color[::-1].tolist()

    #convert to [0,1] r,g,b
    channel_colors = [colors.to_rgb(i) for i in channel_colors]
    cmaps=[Colormap([[0,0,0],col]) for col in channel_colors]
    channel_colormaps=[("colormap_"+str(i),cmaps[i]) for i in range(len(cmaps))]    
        
        
    ####################
    #mIF: unmixed images
    ####################
    viewer1.add_image(mIF_image[::-1], 
                      channel_axis=0, 
                      colormap=channel_colormaps, 
                      name=channel_names, 
                      visible=True, 
                      blending="additive")

    ###############################
    # mIF: Nuclei
    ###############################

    # nucleus centers
    mIF_cell_centers = mIF_cells[["nucleus.y", "nucleus.x"]] #order (y,x)
    # phenotype
    mIF_cell_phenotype = mIF_cells["phenotype"]
    mIF_cell_type_matched = mIF_cells["matched_celltype"]

    mIF_phenotypes = sorted(list(set(mIF_cell_phenotype)))
    mIF_celltypes_matched = sorted(list(set(mIF_cell_type_matched)))
    
    cm = [(x.min(),np.quantile(x,0.99)) for x in mIF_image]

    ###############################
    # Add nuclei centers
    ###############################

    # add points
    point_size=1 #0.7
    point_size_selected=8 #4
    point_edge_width=0.3 #0.3
    mIF_all_cells = viewer1.add_points(mIF_cell_centers, 
                                       name="Nuclei (all)",
                                       size=point_size,
                                       edge_width=point_edge_width,
                                       face_color="black",
                                       edge_color="white",
                                       visible=True,
                                       features={'Phenotype': mIF_cell_phenotype,
                                                 'Matched cell type': mIF_cell_type_matched})

    ###############################
    # Add GUI to play with marker intensity
    ###############################
    channels_controls1 = WidgetChannelsIntensity(viewer1, channel_names)
    scrollArea = QScrollArea()
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(channels_controls1)
    viewer1.window.add_dock_widget(scrollArea, area='left', name="Channel controls")
    
    ###############################
    # Add GUI to select specific cells (using QWidget)
    ###############################
        #celltypes + marker positivity
    class WidgetHighlightNuclei(QWidget):
        def __init__(self,layer_points,celltypes,channel_names_tmp) -> None:
            super().__init__()
            self.layer_points=layer_points
            self.celltypes=celltypes
            self.channel_names_tmp=channel_names_tmp
            self.phenotypes=[x+'+' for x in self.channel_names_tmp]

            self.setLayout(QVBoxLayout())

            self.radiobuttons=[]
            b=QRadioButton("<None>")
            b.setChecked(True)
            b.toggled.connect(self.btn_toggled)
            self.radiobuttons.append(b)
            self.layout().addWidget(b)
            self.radiobutton_none=b

            self.layout().addWidget(QLabel("Matched cell types:"))
            self.radiobuttons_celltypes=[]
            for n in self.celltypes:
                b=QRadioButton(n)
                b.toggled.connect(self.btn_toggled)
                self.radiobuttons.append(b)
                self.radiobuttons_celltypes.append(b)
                self.layout().addWidget(b)

            self.layout().addWidget(QLabel("Marker positivity:"))
            self.radiobuttons_phenotypes=[]
            for n in self.phenotypes:
                b=QRadioButton(n)
                b.toggled.connect(self.btn_toggled)
                self.radiobuttons.append(b)
                self.radiobuttons_phenotypes.append(b)
                self.layout().addWidget(b)

            #add spacer (when the widget is inside a QScrollArea)
            self.layout().addStretch(1)

        def btn_toggled(self):
            #Note: called twice, once for the button unchecked and once the button checked.
            if self.sender().isChecked():
                #unselect all cells
                mIF_all_cells.size=[point_size,point_size]
                mIF_all_cells.face_color=[0,0,0,1]
                mIF_all_cells.edge_color=[1,1,1,1]
                if self.sender() in self.radiobuttons_celltypes: #select celltypes group
                    #select nuclei based on cell types
                    selected=(mIF_all_cells.features['Matched cell type']==self.sender().text())
                    mIF_all_cells.size[selected]=[point_size_selected,point_size_selected] 
                    mIF_all_cells.face_color[selected]=[1,0,0,1]
                    mIF_all_cells.edge_color[selected]=[1,1,1,1]
                if self.sender() in self.radiobuttons_phenotypes: #select phenotype group
                    #select nuclei based on marker positivity    
                    pattern=""
                    for channel in self.channel_names_tmp:
                        if channel+"+"==self.sender().text():
                            pattern=pattern+"("+channel+".)"
                        else:
                            pattern=pattern+channel+"."
                    tmp=np.array([re.match(pattern,x).group(1) for x in mIF_all_cells.features['Phenotype']])
                    selected=(tmp==self.sender().text())
                    mIF_all_cells.size[selected]=[point_size_selected,point_size_selected] 
                    mIF_all_cells.face_color[selected]=[1,0,0,1]
                    mIF_all_cells.edge_color[selected]=[1,1,1,1]
                mIF_all_cells.refresh()
                mIF_all_cells.visible=True  #make sure it is visible
    
    channel_names_tmp=channel_names[1:-1] #ignore DAPI and autofluorescence
    scrollArea = QScrollArea()
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(WidgetHighlightNuclei(None,
                                               mIF_celltypes_matched,
                                               channel_names_tmp))
    viewer1.window.add_dock_widget(scrollArea, area='left',name="Highlight nuclei")
    
    ################################
    # Widget for selecting samples #
    ################################
    selector = QScrollArea()
    selector.setWidgetResizable(True)
    selector.setWidget(WidgetFileSelection(viewer1, "test"))
    viewer1.window.add_dock_widget(selector, area = 'right', name='Select sample')
    
    ####################
    # viewer2 for IMC
    ####################
    viewer2 = napari.Viewer(title=imc_dir)

    #hide "layer controls" and "layer list" docks
    viewer2.window._qt_viewer.dockLayerControls.hide()
    viewer2.window._qt_viewer.dockLayerList.hide()

    #contrast limits
    cm = [(x.min(),np.quantile(x,0.99)) for x in imc_image]
    layer_names = imc_panel.name.tolist()

    #default colormap black-white
    layer_colormaps=[("colormap_white",Colormap([[0,0,0],[1,1,1]]))]*len(layer_names)
    #match channel names to mIF image (very specific to this IMC image from zurich and mIF image from ILL)
    mlabels = layer_names
    rlabels = channel_names
    
    try:
        layer_colormaps[mlabels.index("DNA1")] = channel_colormaps[rlabels.index("DAPI")]
    except:
        print("not found")

    try:
        layer_colormaps[mlabels.index("CarbonicAnhydrase")] = channel_colormaps[rlabels.index("CK")]
    except:
        print("not found")

    try:
        layer_colormaps[mlabels.index("Ecad")] = channel_colormaps[rlabels.index("CK")]
    except:
        print("not found")

    for ch in ["CD15","CD163","CD20","CD11c","CD3"]:
        try:
            layer_colormaps[mlabels.index(ch)] = channel_colormaps[rlabels.index(ch)]
        except:
            print("not found")


    #add image (scaled to match img1 size), using enlarged contrast_limits to fix slider limits
    imc_scale=(mIF_image.shape[0]/imc_image[0].shape[0]+mIF_image.shape[1]/imc_image[0].shape[1])/2
    viewer2.add_image(imc_image,
                      channel_axis=0,
                      name=layer_names,
                      colormap=layer_colormaps,
                      blending="additive",
                      contrast_limits=cm,
                      visible = False,
                      scale=(imc_scale,imc_scale)
                     )

    # #link views: does not work well. Seems to automatically change zoom sometimes... Problem seems to be solved in napari v0.4.16
    # def viewer1_camera_event(event: napari.utils.events.Event):
    #     viewer2.camera.update(viewer1.camera)
    # 
    # def viewer2_camera_event(event: napari.utils.events.Event):
    #     viewer1.camera.update(viewer2.camera)
    # 
    # viewer1.camera.events.connect(viewer1_camera_event)
    # viewer2.camera.events.connect(viewer2_camera_event)
    # #see also
    # #https://forum.image.sc/t/different-ways-to-control-camera-in-napari/60552
    # #https://github.com/napari/napari/issues/3723
    # #https://github.com/vispy/vispy/pull/2312
    # #https://github.com/napari/napari/issues/561
    # #https://github.com/napari/napari/issues/662
    # #https://github.com/napari/napari/issues/760


    #Simpler workaround (Public access to Window.qt_viewer is deprecated and will be removed in napari v0.5.0)
    viewer2.window.qt_viewer.view.camera.link(viewer1.window.qt_viewer.view.camera)

    ###############################
    # IMC Nuclei
    ###############################
    # nucleus centers
    IMC_cell_centers = imc_cells[["Pos_Y", "Pos_X"]] #order (y,x)
    
    # phenotype
    IMC_cell_phenotype = imc_cells["celltypes"]
    IMC_cell_type_matched = imc_cells["matched_celltype"]

    IMC_phenotypes = sorted(list(set(IMC_cell_phenotype)))
    IMC_celltypes_matched = sorted(list(set(IMC_cell_type_matched)))
 
    ###############################
    #Add nuclei center
    ###############################
  
    #add points (scaled to match img1 size)
    IMC_all_cells=viewer2.add_points(IMC_cell_centers, 
                                     name="Nuclei (all)",
                                     size=point_size/imc_scale,
                                     edge_width=point_edge_width/imc_scale,
                                     face_color="black",
                                     edge_color="white",
                                     visible=True,
                                     features={'Cell type': IMC_cell_phenotype,
                                               'Matched cell type': IMC_cell_type_matched},
                                     scale=(imc_scale,imc_scale))
    
    ###############################
    #Add GUI to play with marker intensity
    ###############################

    channels_controls2 = WidgetChannelsIntensity(viewer2,layer_names)
    scrollArea = QScrollArea()
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(channels_controls2)
    viewer2.window.add_dock_widget(scrollArea, area='left',name="Channel controls")
    #channels_controls2 = WidgetChannelsIntensity(viewer2,layer_names)
    #viewer2.window.add_dock_widget(channels_controls2, area='left',name="Channel controls")


    ###############################
    #Add GUI to select specific cells (using QWidget)
    ###############################
    #only celltypes
    class WidgetHighlightNuclei2(QWidget):    
        def __init__(self,layer_points,celltypes) -> None:
            super().__init__()
            self.layer_points=layer_points
            self.celltypes=celltypes

            self.setLayout(QVBoxLayout())

            self.radiobuttons=[]
            b=QRadioButton("<None>")
            b.setChecked(True)
            b.toggled.connect(self.btn_toggled)
            self.radiobuttons.append(b)
            self.layout().addWidget(b)
            self.radiobutton_none=b

            self.layout().addWidget(QLabel("Matched cell types:"))
            self.radiobuttons_celltypes=[]
            for n in self.celltypes:
                b=QRadioButton(n)
                b.toggled.connect(self.btn_toggled)
                self.radiobuttons.append(b)
                self.radiobuttons_celltypes.append(b)
                self.layout().addWidget(b)


            #add spacer (when the widget is inside a QScrollArea)
            self.layout().addStretch(1)

        def btn_toggled(self):
            #Note: called twice, once for the button unchecked and once the button checked.
            if self.sender().isChecked():
                #unselect all cells
                IMC_all_cells.size=[point_size/imc_scale,point_size/imc_scale]
                IMC_all_cells.face_color=[0,0,0,1]
                IMC_all_cells.edge_color=[1,1,1,1]
                if self.sender() in self.radiobuttons_celltypes: #select celltypes group
                    #select nuclei based on cell types
                    selected=(IMC_all_cells.features['Matched cell type']==self.sender().text())
                    IMC_all_cells.size[selected]=[point_size_selected/imc_scale,point_size_selected/imc_scale] 
                    IMC_all_cells.face_color[selected]=[1,0,0,1]
                    IMC_all_cells.edge_color[selected]=[1,1,1,1]
                IMC_all_cells.refresh()
                IMC_all_cells.visible=True  #make sure it is visible

    scrollArea = QScrollArea()
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(WidgetHighlightNuclei2(None,IMC_celltypes_matched))
    viewer2.window.add_dock_widget(scrollArea, area='left',name="Highlight nuclei")

      
    napari.run()


