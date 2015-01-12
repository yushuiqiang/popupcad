# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import PySide.QtGui as qg
import shapely.ops as ops
import popupcad
from popupcad.filetypes.laminate import Laminate
from popupcad.filetypes.layer import Layer
from popupcad.filetypes.sketch import Sketch
import popupcad.widgets
from popupcad.filetypes.operation import Operation
from popupcad.filetypes.design import NoOperation
import popupcad.geometry.customshapely as customshapely
from popupcad.widgets.listmanager import SketchListManager
from popupcad.widgets.dragndroptree import DraggableTreeWidget
from popupcad.manufacturing.nulloperation import NullOp


class Dialog(qg.QDialog):
    def __init__(self,cls,design,operations,selectedoutput = None,sketch = None):
        super(Dialog,self).__init__()
        self.design = design
        self.operations = [NullOp()]+operations
        self.cls = cls

        self.sketchwidget = SketchListManager(self.design)
        for ii in range(self.sketchwidget.itemlist.count()):
            item = self.sketchwidget.itemlist.item(ii)
            if item.value==sketch:
                item.setSelected(True)
        
        if selectedoutput == None:
            selectedoutput = [item.id for item in design.return_layer_definition().layers]
            
        self.outputlayerselector = qg.QListWidget()
        self.outputlayerselector.setSelectionBehavior(qg.QListWidget.SelectionBehavior.SelectRows)
        self.outputlayerselector.setSelectionMode(qg.QListWidget.SelectionMode.MultiSelection)
        
        outputitems = [popupcad.filetypes.listwidgetitem.ListWidgetItem(item,self.outputlayerselector) for item in design.return_layer_definition().layers]
        [item.setSelected(item.customdata.id in selectedoutput) for item in outputitems]        

        button1 = qg.QPushButton('Ok')
        button2 = qg.QPushButton('Cancel')
        buttonlayout = qg.QHBoxLayout()
        buttonlayout.addWidget(button1)
        buttonlayout.addWidget(button2)

        layout = qg.QVBoxLayout()
        layout.addWidget(self.sketchwidget)
        layout.addWidget(qg.QLabel('Select Layers'))
        layout.addWidget(self.outputlayerselector)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)        

        button1.pressed.connect(self.accept)
        button2.pressed.connect(self.reject)

    def sketch(self):
        try:
            return self.sketchwidget.itemlist.selectedItems()[0].value
        except IndexError:
            return None

    def acceptdata(self):
        sketchid =  self.sketch().id
        layer_links = [item.customdata.id for item in self.outputlayerselector.selectedItems()]
        return sketchid,layer_links

class SimpleSketchOp(Operation):
    name = 'Sketch Operation'
    def copy(self):
        new = type(self)(self.sketchid,self.layer_links)
        new.id = self.id
        new.customname = self.customname
        return new

    def __init__(self,*args):
        super(SimpleSketchOp,self).__init__()
        self.editdata(*args)
        self.id = id(self)
        
    def editdata(self,sketchid,layer_links):        
        super(SimpleSketchOp,self).editdata()
        self.sketchid = sketchid
        self.layer_links = layer_links

    def operate(self,design):
        operationgeom = design.sketches[self.sketchid].output_csg()
#        operationgeom = popupcad.geometry.customshapely.multiinit(operationgeom)
        layers = [design.return_layer_definition().getlayer(item) for item in self.layer_links]        
        laminate = Laminate(design.return_layer_definition())
        for layer in layers:
            laminate.replacelayergeoms(layer,operationgeom)
        return laminate

    def sketchrefs(self):
        return [self.sketchid]

    @classmethod
    def buildnewdialog(cls,design,currentop):
        dialog = Dialog(cls,design,design.operations)
        return dialog
        
    def buildeditdialog(self,design):
        sketch = design.sketches[self.sketchid]
        dialog = Dialog(self,design,design.prioroperations(self),self.layer_links,sketch)
        return dialog