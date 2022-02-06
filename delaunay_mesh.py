from matplotlib import patches
import matplotlib.pyplot as plt

from pathlib import Path

from matplotlib.animation import FFMpegWriter

import numpy as np
import math

from geometry import *

from draw import draw_mesh_external 
from mesh_utils import orderEdgesPolyline, orderEdgesLoop, findSingleElementEdges

class mesh:
    def __init__(self):
        self.nodes = []         # A list of nodes.
        self.edges = []         # A list of edges.
        self.elements = []      # A list of elements.
        
        # The following data members are used when producing an animation.
        # They are initialized by a call to vplot_init() and referenced subsequently by
        # calls to vplot().
        
        self.fig = None         # A matplotlib Figure object.
        self.axs = None         # A matplotlib Axis object.
        self.fpath = None       # file path for the mpeg file.
        
    def addNodes(self, nodeList):
        self.nodes.extend([np.array(qq) for qq in nodeList])
        
    def addEdges(self, edgeList):
        edgeList = [{'nodes':ix, 'parent_elements':[], 'bnd': False} for ix in edgeList]
        self.edges.extend(edgeList)        
        
    def addElements(self, elementList):
        
        numElements = len(self.elements)    
        
        elementList = [ [{'edge':iq[0], 'orn':iq[1]} for iq in ix] for ix in elementList]
        self.elements.extend(elementList) 
        
        # update edge connectivity
               
        for ix, ee in enumerate(elementList):          
            for xx in ee:
                self.edges[xx['edge']]['parent_elements'].append(numElements + ix)
    
    def getElementNodes(self, ielem):
        res = []
        if len(self.elements[ielem])>0:
            iedge = self.elements[ielem][0]['edge']
            res   = self.edges[iedge]['nodes'].copy()
    
            for xx in self.elements[ielem][1:]:
                for yy in self.edges[xx['edge']]['nodes']:
                    if yy not in res: res.append(yy)
            
        return res
    
    def getElementOrderedNodes(self, ielem):
        xx = self.elements[ielem]     
        return list(self.getOrderedEdgeNodes(xx))
    
    def getOrderedEdgeNodes(self, xx):
        
        if len(xx)==1:          
            nn  = self.edges[xx[0]['edge'] ]['nodes']
            n1 = nn[0] if xx[0]['orn'] else nn[1]
            n2 = nn[1] if xx[0]['orn'] else nn[0]
                    
            return n1, n2
        
        elif len(xx) == 3:
            nn = self.edges[xx[0]['edge']]['nodes']
            n1 = nn[0] if xx[0]['orn'] else nn[1]
            nn = self.edges[xx[1]['edge']]['nodes']
            n2 = nn[0] if xx[1]['orn'] else nn[1]
            nn = self.edges[xx[2]['edge']]['nodes']
            n3 = nn[0] if xx[2]['orn'] else nn[1]
            
            return n1, n2, n3
   
    def findEdge(self, nodes):
        for ix, xx in enumerate(self.edges):
             if (xx['nodes'] == nodes) | (xx['nodes'] == nodes[-1::-1]):
                return ix
            
        return None
    
    def isElementObscured(self, ielem, txy):
        # Is the view of element ielem from co-ordinate xy obscured by any feature ?
        # txy is the test point (numpy array)
        
        nodes = self.getElementNodes(ielem)
        
        pxy1 = self.nodes[nodes[0]]
        pxy2 = self.nodes[nodes[1]]
        
        if len(self.elements[ielem]) == 1: 
            iedge = self.elements[ielem][0]['edge']
                  
            for ix, xx in enumerate(self.edges):
                if not xx['feature']: continue
                               
                if iedge==ix:
                    bleft = pointOnFeatureLeft(txy, pxy1, pxy2)
                    born  = self.elements[ielem][0]['orn']                  
                    
                    if born & (not bleft): return True
                    if (not born) & bleft: return True                   
                
                fxy1 = self.nodes[xx['nodes'][0]]
                fxy2 = self.nodes[xx['nodes'][1]]
                               
                if lineInFeatureShadow(pxy1, pxy2, fxy1, fxy2, txy): return True
                
            return False
        else:
            pxy3 = self.nodes[nodes[2]]
            
            for ix, xx in enumerate(self.edges):
                if not xx['feature']: continue
                fxy1 = self.nodes[xx['nodes'][0]]
                fxy2 = self.nodes[xx['nodes'][1]]
                               
                if elementInFeatureShadow(pxy1, pxy2, pxy3, fxy1, fxy2, txy): return True
                
            return False  

    def remove_element(self, ix, xx, islist, iolist):
          
        if xx[0]['edge'] not in islist: islist[xx[0]['edge']] = 0
        if xx[1]['edge'] not in islist: islist[xx[1]['edge']] = 0
        if xx[2]['edge'] not in islist: islist[xx[2]['edge']] = 0
            
        islist[xx[0]['edge']] += 1
        islist[xx[1]['edge']] += 1
        islist[xx[2]['edge']] += 1
        
        iolist[xx[0]['edge']] = xx[0]['orn']
        iolist[xx[1]['edge']] = xx[1]['orn']
        iolist[xx[2]['edge']] = xx[2]['orn']
        
        pelist = self.edges[xx[0]['edge']]['parent_elements']
        if ix in pelist: pelist.remove(ix)
        pelist = self.edges[xx[1]['edge']]['parent_elements']
        if ix in pelist: pelist.remove(ix)
        pelist = self.edges[xx[2]['edge']]['parent_elements']
        if ix in pelist: pelist.remove(ix)
    
    def identifyAffectedElements(self, nodes, checkVisibility=False):
    
        if len(nodes)<2: 
            xynew = nodes[0]
        else:
            xynew = self.nodes[nodes[1]]
        
        # node - co-ordinates of the new node.
    
        islist = {} # holder for the edge connectivity counts
        iolist = {} # holder for the orientations.
        
        affectedElements = [] # List of candidate elements to be deleted, not considering features.
    
        for ix, xx in enumerate(self.elements):
            if len(xx) <1: 
                continue
            elif len(xx)==1:
                # xx is a boundary element.
                
                n1, n2 = self.getOrderedEdgeNodes(xx)
                
                disc = pointOnFeatureLeft(xynew, self.nodes[n1], self.nodes[n2])
                             
                if disc>0.0:
                    # The new node is to the left of [a, b]
                    if checkVisibility:                     
                        if self.isElementObscured(ix, xynew): 
                            continue
                 
                    affectedElements.append(ix)
                    
                    if xx[0]['edge'] not in islist: islist[xx[0]['edge']] = 0
                    islist[xx[0]['edge']] += 1
                    iolist[xx[0]['edge']] = xx[0]['orn']
                    pelist = self.edges[xx[0]['edge']]['parent_elements']
                    if ix in pelist: pelist.remove(ix)
                
            else: 
                n1, n2, n3 = self.getOrderedEdgeNodes(xx)
               
                if point_in_ccircle(xynew, self.nodes[n1], self.nodes[n2], self.nodes[n3]):
        
                    if checkVisibility:                    
                        if self.isElementObscured(ix, xynew): 
                            continue
                    
                    affectedElements.append(ix)
                    self.remove_element(ix, xx, islist, iolist)
                    
                    continue
                    
                # Does the new feature given by 'nodes' penetrate the element ?
                
                bBadElement = False
                
                if checkVisibility:
                
                    xyprev = self.nodes[nodes[0]]               
                    bnorm = xyprev - xynew
                    bnorm = bnorm / np.linalg.norm(bnorm)  
                
                    if not bBadElement:
                        bint1 = lineInRayPath(xyprev,-bnorm, self.nodes[n1], self.nodes[n2])
                        bint2 = lineInRayPath(xynew,  bnorm, self.nodes[n1], self.nodes[n2])
                        if bint1 & bint2: bBadElement  = True                      
                    
                    if not bBadElement:
                        bint1 = lineInRayPath(xyprev,-bnorm, self.nodes[n1], self.nodes[n3])
                        bint2 = lineInRayPath(xynew,  bnorm, self.nodes[n1], self.nodes[n3])
                        if bint1 & bint2: bBadElement  = True    
                    
                    if not bBadElement:
                        bint1 = lineInRayPath(xyprev,-bnorm, self.nodes[n2], self.nodes[n3])
                        bint2 = lineInRayPath(xynew,  bnorm, self.nodes[n2], self.nodes[n3])
                        if bint1 & bint2: bBadElement  = True 
  
                    if bBadElement:   
                        affectedElements.append(ix)
                        self.remove_element(ix, xx, islist, iolist)
                        
        return islist, iolist, affectedElements
    
    def createElementsPolyline(self, ielist2, inode):
        
        # Generate the new edges.             
            
        numEdges       = len(self.edges)
        numElements    = len(self.elements) 
        numNewElements = len(ielist2)
        
        # Create indices for the boundary elements.
        ielBnd0 = numElements + numNewElements
        ielBnd1 = numElements + numNewElements + 1
        
        for ix, q in enumerate(ielist2):
            
            iel1 = numElements+ix
            iel2 = numElements+ix-1
            
            self.edges[q[0]]['parent_elements'].append(iel1)        
            
            if ix==0:
                # First element.
                self.edges.append({'nodes':[q[2], inode], 'parent_elements':[iel1, ielBnd0], 'bnd':True, 'feature':False})

                if numNewElements == 1:
                    self.edges.append({'nodes':[q[3], inode], 'parent_elements':[ielBnd1, iel1], 'bnd':True, 'feature':False})
                    
            elif ix==numNewElements-1:
                # Last element.
                self.edges.append({'nodes':[q[2], inode], 'parent_elements':[iel1, iel2], 'bnd':False, 'feature':False})
                self.edges.append({'nodes':[q[3], inode], 'parent_elements':[ielBnd1, iel1], 'bnd':True, 'feature':False})
            else:
                # Intermediate element.                             
                self.edges.append({'nodes':[q[2], inode], 'parent_elements':[iel1, iel2], 'bnd':False, 'feature':False})
                               
            is1 = {'edge': q[0], 'orn':q[1]}
            is2 = {'edge': numEdges+ix+1, 'orn':True}
            is3 = {'edge': numEdges+ix, 'orn':False}
            
            self.elements.append([is1, is2, is3])
            
            iel1 = self.edges[q[0]]['parent_elements'][0]
            iel2 = self.edges[q[0]]['parent_elements'][1]
            
            if(len(self.elements[iel1])==3 & len(self.elements[iel2])==3): self.edges[q[0]]['bnd'] = False
        
        # Create the boundary elements.
        is1 = {'edge': numEdges, 'orn':True}
        self.elements.append([is1])
        
        is1 = {'edge': numEdges+numNewElements, 'orn':False}
        self.elements.append([is1])
        
    def createElementsLoop(self, ielist2, inode):
        # Generate the new edges.             
            
        numEdges       = len(self.edges)
        numElements    = len(self.elements)   
        numNewElements = len(ielist2) 
        
        for ix, q in enumerate(ielist2):
            
            ienew = numElements + ix
            self.edges[q[0]]['parent_elements'].append(ienew)
            self.edges.append({'nodes':[q[2], inode], 'parent_elements':[ienew, ienew-1], 'bnd':False, 'feature':False})
                               
            is1 = {'edge': q[0], 'orn':q[1]}
            is2 = {'edge': numEdges+ix+1, 'orn':True}
            is3 = {'edge': numEdges+ix, 'orn':False}
                               
            self.elements.append([is1, is2, is3])
        
        iel = numElements + numNewElements - 1
        self.elements[iel][1]['edge'] = numEdges
        self.edges[numEdges]['parent_elements'][1] = len(self.elements) - 1
        
    def removeNonFeatureBoundaryEdges(self):    
        bCont = True
        
        while(bCont):

            bCont = False
            edgeRemovalList = []
        
            for ix, xx in enumerate(self.edges):
                if len(xx['parent_elements']) > 0:
                    if (xx['bnd']) & (not xx['feature']):
                        edgeRemovalList.append(ix)
                        
            for ie in edgeRemovalList:
                for iel in self.edges[ie]['parent_elements']:
                    xxdel = None
                    for xx in self.elements[iel]:
                        if xx['edge'] == ie:
                            xxdel = xx
                            break
                    if xxdel: self.elements[iel].remove(xxdel)
                    edgeList = [xx['edge'] for xx in self.elements[iel]]
                    
                    for iedge in edgeList:
                        self.edges[iedge]['bnd'] = True
                    
                self.edges[ie]['parent_elements'] = []
            
            if len(edgeRemovalList) > 0: bCont = True      
                
    def insertNode(self, node):
        
        numNodes = len(self.nodes)
        self.nodes.append(node)
        
        if numNodes == 0:
            return
        if numNodes == 1:
            self.edges.append({'nodes':[0,1], 'parent_elements':[], 'bnd':False, 'feature':False})
        elif numNodes == 2:
            
            self.edges.append({'nodes':[0,2], 'parent_elements':[0,2], 'bnd':True, 'feature':False})
            self.edges.append({'nodes':[1,2], 'parent_elements':[0,3], 'bnd':True, 'feature':False})
            self.edges[0]['parent_elements'] = [0,1]
            self.edges[0]['bnd'] = True
            
            v1 = np.array(self.nodes[1]) - np.array(self.nodes[0])
            v2 = np.array(node) - np.array(self.nodes[0])
            disc = np.cross(v1, v2)
            if disc>0.0:
                self.elements.append([{'edge':0, 'orn':True}, {'edge':2, 'orn':True}, {'edge':1, 'orn':False}])
                self.elements.append([{'edge':0, 'orn':False}])              
                self.elements.append([{'edge':1, 'orn':True}])
                self.elements.append([{'edge':2, 'orn':False}])
            else:
                self.elements.append([{'edge':0, 'orn':False}, {'edge':1, 'orn':True}, {'edge':2, 'orn':False}])
                self.elements.append([{'edge':0, 'orn':True}])
                self.elements.append([{'edge':1, 'orn':False}])
                self.elements.append([{'edge':2, 'orn':True}])
                
            
        else:
            # For which elements is the node in the circumcricle ?
            
            TBDList = [] # A list of elements to be deleted.
            islist = {} # holder for the edge connectivity counts
            iolist = {} # holder for the orientations.
            
            bBoundaryElement = False
            
            nodes = [node]
            
            islist, iolist, TBDList = self.identifyAffectedElements(nodes)
            
            for ix in TBDList:
                if len(self.elements[ix]) == 1: bBoundaryElement = True
            
            # Make a list of edges that are referenced by one element only.
            
            #ielist = self.findSingleElementEdges(islist, iolist)
            ielist = findSingleElementEdges(islist, iolist, self.edges)
                    
            # Order the edges. 
            
            if bBoundaryElement:
                ielist2 = orderEdgesPolyline(ielist)            
            else: 
                ielist2 = orderEdgesLoop(ielist)
                
            # Generate the new edges.             
            
            numEdges       = len(self.edges)
            numElements    = len(self.elements)         
            numNewElements = len(ielist2)
                     
            if bBoundaryElement:               
                self.createElementsPolyline(ielist2, numNodes)             
            else:
                self.createElementsLoop(ielist2, numNodes)
            
            # Delete elements.
            for ix in TBDList:
                self.elements[ix] = [] 
        
    def flip(self, iedge):
        
        if self.edges[iedge]['bnd']: return
            
        if len(self.edges[iedge]['parent_elements']) == 2:
            # Flip requires an edge that is referenced twice.
            
            ielem1 = self.edges[iedge]['parent_elements'][0]
            ielem2 = self.edges[iedge]['parent_elements'][1]
            
            isides1 = [ix['edge'] for ix in self.elements[ielem1]]
            isides2 = [ix['edge'] for ix in self.elements[ielem2]]
            
            # Roll the list of edges until the common edge 'iedge' is last in each list.
            
            irr = 2 - isides1.index(iedge) # right roll amount = irr
            self.elements[ielem1] = self.elements[ielem1][-irr:] + self.elements[ielem1][:-irr]
            
            irr = 2 - isides2.index(iedge) # right roll amount = irr
            self.elements[ielem2] = self.elements[ielem2][-irr:] + self.elements[ielem2][:-irr]
            
            ia1 = self.elements[ielem1][0]
            ib1 = self.elements[ielem1][1]
            ia2 = self.elements[ielem2][0]
            ib2 = self.elements[ielem2][1]
            
            ia1_last = self.edges[ia1['edge']]['nodes'][1] if ia1['orn'] else self.edges[ia1['edge']]['nodes'][0]
            ia2_last = self.edges[ia2['edge']]['nodes'][1] if ia2['orn'] else self.edges[ia2['edge']]['nodes'][0]
            
            # Redefine the edge:
            
            self.edges[iedge]['nodes'] = [ia1_last, ia2_last]
            
            islist1 = [self.elements[ielem1][1], self.elements[ielem2][0], {'edge':iedge, 'orn':False}]
            islist2 = [self.elements[ielem2][1], self.elements[ielem1][0], {'edge':iedge, 'orn':True}]
            
            self.elements[ielem1] = islist1
            self.elements[ielem2] = islist2
            
            ix = self.edges[ia1['edge']]['parent_elements'].index(ielem1)
            self.edges[ia1['edge']]['parent_elements'][ix] = ielem2
            
            ix = self.edges[ia2['edge']]['parent_elements'].index(ielem2)
            self.edges[ia2['edge']]['parent_elements'][ix] = ielem1

            
    def isFlippable(self, iedge):
        
        if self.edges[iedge]['bnd']: return False
        
        if len(self.edges[iedge]['parent_elements']) == 2:
            # Flip requires an edge that is referenced twice.
            
            ielem1 = self.edges[iedge]['parent_elements'][0]
            ielem2 = self.edges[iedge]['parent_elements'][1]
            
            iind = [xx['edge'] for xx in self.elements[ielem1]].index(iedge)
            iind_next = (iind+1) % 3
            
            eside = self.elements[ielem1][iind_next]
            
            if eside['orn']:
                iother1 = self.edges[eside['edge']]['nodes'][1]
            else:
                iother1 = self.edges[eside['edge']]['nodes'][0]
                
            iind = [xx['edge'] for xx in self.elements[ielem2]].index(iedge)
            iind_next = (iind+1) % 3
            
            eside = self.elements[ielem2][iind_next]
            
            if eside['orn']:
                iother2 = self.edges[eside['edge']]['nodes'][1]
            else:
                iother2 = self.edges[eside['edge']]['nodes'][0]
                
            ptest = self.nodes[iother1]
            
            inods = self.edges[iedge]['nodes'].copy()
            inods.append(iother2)
            
            node_list = self.getElementOrderedNodes(ielem2)
            node_list = [self.nodes[xx] for xx in node_list]
            
            if point_in_ccircle(ptest, *node_list):
                return True
            
        return False

    
    def addBoundaryLoop(self, nodeList, video=False):
    
        self.addNodes(nodeList)
        for ixn in range(len(nodeList)-1):
            self.insertBoundaryEdge([ixn, ixn+1])
            if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)
    
        self.insertBoundaryEdge([len(nodeList)-1, 0])
        if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)
        
        self.removeNonFeatureBoundaryEdges()
        if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)
        
    def addBoundaryLoopWithVideo(self, nodeList):
        with self.writer.saving(self.fig, self.fpath, 200):
            self.addBoundaryLoop(nodeList, video=True)
            
    def plot(self, figsize=(6,6), labels=True, arrows=True, internal=True):
    
        fig, axs = plt.subplots(1,1, figsize=figsize)
        axs.set_aspect(aspect = 1.0)
        
        self.draw_mesh(axs, labels = labels, arrows = arrows, internal=internal)
        
        axs.autoscale()
        
        plt.show()
    
    def draw_mesh(self, axs, labels=True, arrows=True, internal=True):
        draw_mesh_external(axs, self.nodes, self.edges, self.elements, labels=labels, arrows=arrows, internal=internal)
        
    def vplot_init(self, fpath, figsize=(6,6)):
    
        fle = Path(fpath)
        fle.touch(exist_ok=True)
        self.fpath = fpath
        
        self.fig, self.axs = plt.subplots(1,1, figsize=figsize)
        self.writer = FFMpegWriter(fps=2)
            
    def vplot(self, writer, fig, axs, labels=True, arrows=True):
        
        axs.set_aspect(aspect = 1.0)
        axs.cla()
        
        self.draw_mesh(axs, labels = labels, arrows = arrows)
                                   
        axs.autoscale()
    
        writer.grab_frame()
        
    def insertBoundaryEdge(self, nodes):
        
        # assumes that the outer loop edges are inserted in correct order.
        numEdges = len(self.edges)
        
        xynew = self.nodes[nodes[1]]
  
        if numEdges == 0:
            self.edges.append({'nodes':nodes, 'parent_elements':[], 'bnd':True, 'feature':True})
        elif numEdges == 1:       
            v1 = self.nodes[1] - self.nodes[0]
            v2 = xynew - self.nodes[0]
            disc = np.cross(v1, v2)
                    
            if abs(disc) < 1.0e-9:
                self.edges.append({'nodes':nodes, 'parent_elements':[], 'bnd':True, 'feature':True})
            else:
                self.edges.append({'nodes':[0,2], 'parent_elements':[0,2], 'bnd':True, 'feature':False})
                self.edges.append({'nodes':[1,2], 'parent_elements':[0,3], 'bnd':True, 'feature':True})
                self.edges[0]['parent_elements'] = [0,1]
                self.edges[0]['bnd'] = True
                            
                if disc>0.0:
                    self.elements.append([{'edge':0, 'orn':True}, {'edge':2, 'orn':True}, {'edge':1, 'orn':False}])
                    self.elements.append([{'edge':0, 'orn':False}])              
                    self.elements.append([{'edge':1, 'orn':True}])
                    self.elements.append([{'edge':2, 'orn':False}])
                else:
                    self.elements.append([{'edge':0, 'orn':False}, {'edge':1, 'orn':True}, {'edge':2, 'orn':False}])
                    self.elements.append([{'edge':0, 'orn':True}])
                    self.elements.append([{'edge':1, 'orn':False}])
                    self.elements.append([{'edge':2, 'orn':True}])
        elif len(self.elements) == 0:
 
            v1 = self.nodes[1] - self.nodes[0]
            v2 = xynew - self.nodes[0]
            disc = np.cross(v1, v2) 
            #v1 = np.array(self.nodes[1]) - np.array(self.nodes[0])
            #v2 = np.array(node) - np.array(self.nodes[0])
            #disc = np.cross(v1, v2)
            
            if (abs(disc) < 1.0e-9):
                self.edges.append({'nodes':nodes, 'parent_elements':[], 'bnd':True, 'feature':True})
            else:
                # Create an element for each edge.
                
                inod = nodes[1] # This will be the new node number.
                
                self.edges.append({'nodes':nodes, 'parent_elements':[2*inod-1,inod-1], 'bnd':True, 'feature':True})
                self.edges.append({'nodes':[0,inod], 'parent_elements':[inod,inod+1], 'bnd':True, 'feature':False})
                             
                for ii in range(1, inod-1):              
                    self.edges.append({'nodes':[ii,inod], 'parent_elements':[inod+ii,inod+ii+1], 'bnd':False, 'feature':False})
            
                if disc>0.0:
                    
                    for ii in range(inod-1): self.elements.append([{'edge':ii, 'orn':False}])
                        
                    self.elements.append([{'edge':inod-1, 'orn':False}])
                    self.elements.append([{'edge':inod, 'orn':True}])
                
                    for ii in range(inod-1):
                        self.elements.append([{'edge':ii, 'orn':True}, {'edge':inod+ii+1, 'orn':True}, {'edge':inod+ii, 'orn':False}])
                
                    self.elements[2*inod - 1][1]['edge'] = inod-1        
                else:
                    
                    for ii in range(inod-1): self.elements.append([{'edge':ii, 'orn':True}])
                        
                    self.elements.append([{'edge':inod-1, 'orn':True}])
                    self.elements.append([{'edge':inod, 'orn':False}])
                
                    for ii in range(inod-1):
                        self.elements.append([{'edge':ii, 'orn':False}, {'edge':inod+ii, 'orn':True}, {'edge':inod+ii+1, 'orn':False}])
                
                    self.elements[2*inod - 1][2]['edge'] = inod-1     
                    
                for ii in range(inod-1):
                    self.edges[ii]['parent_elements'] = [inod+ii, ii]
                
        else:
            
            # Need to check that the edge doesn't already exist ... if it does then change the 'feature' designation.
            
            ie = self.findEdge(nodes)
            if ie:
                self.edges[ie]['feature'] = True
                return
            
            bBoundaryElement = False
            
            islist, iolist, TBDList = self.identifyAffectedElements(nodes, checkVisibility=True)
                
            for ix in TBDList:
                if len(self.elements[ix]) == 1: bBoundaryElement = True
                                      
            if len(TBDList) == 0: 
                
                numElements = len(self.elements)
                numEdges = len(self.edges)
                
                ie = self.findEdge(nodes)
                if ie:
                    self.edges[ie]['feature'] = True
                else:
                    self.edges.append({'nodes':nodes, 'parent_elements':[numElements,numElements+1], 'bnd':True, 'feature':True})
                    
                self.elements.append([{'edge':numEdges, 'orn':True}])
                self.elements.append([{'edge':numEdges, 'orn':False}])
                    
                return
        
            # Make a list of edges that are referenced by one element only.
            
            #ielist = self.findSingleElementEdges(islist, iolist)
            ielist = findSingleElementEdges(islist, iolist, self.edges)
            
            conn_dict = {}
            for q in ielist:
                if not q[2] in conn_dict: conn_dict[q[2]]=0 
                if not q[3] in conn_dict: conn_dict[q[3]]=0
                
                conn_dict[q[2]] += 1
                conn_dict[q[3]] += 1
            
            bBoundaryElement = False
            for q in conn_dict:
                if conn_dict[q] == 1:
                    bBoundaryElement = True
                    break
            
            # Need a test here to determine whether it's a polyline or a loop.
                    
            # Order the edges.           

            if bBoundaryElement:
                ielist2 = orderEdgesPolyline(ielist)            
            else: 
                ielist2 = orderEdgesLoop(ielist) 
                
            # Create elements.
            
            if bBoundaryElement:                  
                self.createElementsPolyline(ielist2, nodes[1])
            else:
                self.createElementsLoop(ielist2, nodes[1])
                
            # Delete elements.
            for ix in TBDList:
                self.elements[ix] = []  
                
            ie = self.findEdge(nodes)
            if ie:
                self.edges[ie]['feature'] = True
        




