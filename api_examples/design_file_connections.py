# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import networkx
#import matplotlib.pyplot as plt
#plt.ion()


import os
import sys
import yaml
import popupcad
import glob

def fix(*args):
    return os.path.normpath(os.path.join(*args))
    
def get_subfiles_r(d,parent_name):
    for key,subdesign in d.subdesigns.items():
        subdesign_name = subdesign.get_basename()
        subdesign_name = os.path.splitext(subdesign_name)[0]
        dg.add_node(subdesign_name)    
        dg.add_edge(parent_name,subdesign_name)
        get_subfiles_r(subdesign,subdesign_name)
if __name__=='__main__':
    
    #app = qg.QApplication(sys.argv)
#    original_directory = 'C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified'
    directory = 'C:/Users/danaukes/Dropbox/zhis sentinal 11 files/modified'
    
    globstring = fix(directory,'*.cad')
    
    files = glob.glob(globstring)
    subfiles = {}
    allfiles = []
    
    connections = []
    
    
    print(files)
    dg = networkx.DiGraph()
    
    for filename in files[:]:
        print(filename)
        full_filename = fix(filename)
        d = popupcad.filetypes.design.Design.load_yaml(full_filename,upgrade=False)
        design_name = d.get_basename()
        design_name = os.path.splitext(design_name)[0]
        
        allfiles.append(design_name)
        parent_name = d.get_basename()
        parent_name = os.path.splitext(parent_name)[0]
        get_subfiles_r(d,parent_name)
    
    #plt.figure()
    #pos = networkx.circular_layout(dg)
    #networkx.draw_networkx_labels(dg,pos)
    #networkx.draw(dg,pos)
    #plt.show()
    
    nodes = dg.nodes()
    edges = dg.edges()
    
    nodes = list(set(nodes))
    edges = list(set(edges))
    
    with open(directory+'/graph1.yaml','w') as f:
        yaml.dump({'nodes':nodes,'edges':edges},f)
    
