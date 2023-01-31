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
#WidgetChannelsIntensity
###########################################

#simple widget to control layer contrast_limits, visibility and color.
#layer_names: names of the layers to add controls (must be image layers, not checked).
#default contrast_limits will be taken from viewer.layers[layer_names].contrast_limits
#Note: not updated if layer colormap or contrast_limits are changed elsewhere.

class WidgetChannelsIntensity(QWidget):
    def __init__(self,viewer,layer_names) -> None:
        super().__init__()
        self.layer_names=layer_names
        self.viewer=viewer
        
        self.colordialog=QColorDialog()
        #set custom colors
        try:
            color_list=[]
            #add layer colors
            col_ind=0
            for i in range(len(self.layer_names)):
                colRGB=self.viewer.layers[i].colormap.colors[1]
                color=QColor(round(colRGB[0]*255), round(colRGB[1]*255),round(colRGB[2]*255))
                if col_ind<self.colordialog.customCount() and not color.name() in color_list:
                    self.colordialog.setCustomColor(col_ind,color)
                    color_list.append(color.name())
                    col_ind=col_ind+1
            #add plain colors
            for r in [0,255]:
                for g in [0,255]:
                    for b in [0,255]:
                        color=QColor(r,g,b)
                        if col_ind<self.colordialog.customCount() and not color.name() in color_list:
                            self.colordialog.setCustomColor(col_ind,color)
                            color_list.append(color.name())
                            col_ind=col_ind+1
        except:
            print('cannot set custom colors')
      
        #store original contrast limits
        self.contrast_limits=[]
        for i in range(len(self.layer_names)):
            self.contrast_limits.append(self.viewer.layers[self.layer_names[i]].contrast_limits)

        self.setLayout(QVBoxLayout())

        self.buttons_showhide=[]
        for i in range(len(self.layer_names)):
            self.buttons_showhide.append(QPushButton("Hide"))
            self.buttons_showhide[i].setCheckable(True)
            self.buttons_showhide[i].setChecked(True)
            self.buttons_showhide[i].clicked.connect(self.btn_show_hide_click)

        self.buttons_color=[]
        for i in range(len(self.layer_names)):
            self.buttons_color.append(QPushButton())
            self.buttons_color[i].clicked.connect(self.btn_color_click)
            colRGB=self.viewer.layers[i].colormap.colors[1]
            colname=QColor(round(colRGB[0]*255), round(colRGB[1]*255),round(colRGB[2]*255)).name()
            self.buttons_color[i].setStyleSheet("QPushButton{ background-color: "+colname+" }")
            
        self.sliders=[]
        self.slider_lim=100
        for i in range(len(self.layer_names)):
            self.sliders.append(QSlider(Qt.Horizontal))
            self.sliders[i].setMinimum(-self.slider_lim)
            self.sliders[i].setMaximum(self.slider_lim)
            self.sliders[i].setValue(0)
            self.sliders[i].valueChanged.connect(self.slider_change)
            
        for i in range(len(self.layer_names)):
            self.layout().addWidget(QLabel(self.layer_names[i]+":"))
            tmplayout=QHBoxLayout()
            tmplayout.addWidget(self.buttons_showhide[i])
            tmplayout.addWidget(self.buttons_color[i])
            tmplayout.addWidget(self.sliders[i])
            self.layout().addLayout(tmplayout)

        #add spacer (when the widget is inside a QScrollArea)
        self.layout().addStretch(1)
        
    def slider_change(self):
        for i in range(len(self.layer_names)):
            if self.sender()==self.sliders[i]:
                max_factor=50
                x=max_factor**(-self.sliders[i].value()/self.slider_lim)
                self.viewer.layers[self.layer_names[i]].contrast_limits=(self.contrast_limits[i][0],self.contrast_limits[i][1]*x)

    def btn_show_hide_click(self):
        for i in range(len(self.layer_names)):
            if self.sender()==self.buttons_showhide[i]:
                if self.buttons_showhide[i].isChecked():
                    self.buttons_showhide[i].setText("Hide")
                    self.viewer.layers[self.layer_names[i]].visible=True
                    self.sliders[i].setEnabled(True)
                else:
                    self.buttons_showhide[i].setText("Show")
                    self.viewer.layers[self.layer_names[i]].visible=False
                    self.sliders[i].setEnabled(False)

    def btn_color_click(self):
        for i in range(len(self.layer_names)):
            if self.sender()==self.buttons_color[i]:
                #get layer color
                colRGB=self.viewer.layers[i].colormap.colors[1]
                color=QColor(round(colRGB[0]*255), round(colRGB[1]*255),round(colRGB[2]*255))
                color=self.colordialog.getColor(initial=color)
                if color.isValid():
                    #set layer color
                    cm=self.viewer.layers[i].colormap
                    cm.update({'colors':[cm.colors[0],[color.redF(),color.greenF(),color.blueF(),color.alphaF()]]})
                    self.viewer.layers[i].colormap=cm
                    #set button color
                    self.buttons_color[i].setStyleSheet("QPushButton{ background-color: "+color.name()+" }")