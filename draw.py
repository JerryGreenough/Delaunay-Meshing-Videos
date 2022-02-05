from matplotlib import patches
import matplotlib.pyplot as plt

import numpy as np

def draw_nodelist_external(axs, nodeList):

    labels = True
    
    xmin = min([xx[0] for xx in nodeList])
    xmax = max([xx[0] for xx in nodeList])
    ymin = min([xx[1] for xx in nodeList])
    ymax = max([xx[1] for xx in nodeList])
    
    dx = xmax-xmin
    dy = ymax-ymin
    
    radius = 0.01 * max(dx, dy)

    for ix, nn in enumerate(nodeList):
        e2 = patches.Circle(nn, radius=radius, color = 'red')
        
        xy = [nn[0] + radius, nn[1] - 4.0*radius]
        
        if labels:
            axs.text(*xy, str(ix), color = 'blue')
        axs.add_patch(e2)
        
    for ix in range(len(nodeList)-1):
   
        pntList = [nodeList[ix], nodeList[ix+1]]
    
        e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=1)
        axs.add_patch(e1)
        
    pntList = [nodeList[-1], nodeList[0]]
    
    e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=1)
    axs.add_patch(e1)
    
def plot_nodelist(nodeList, figsize=(6,6)):
    
    fig, axs = plt.subplots(1,1, figsize=figsize)
    axs.set_aspect(aspect = 1.0)
    
    draw_nodelist_external(axs, nodeList)
    
    axs.autoscale()
    
    plt.show()


def draw_mesh_external(axs, nodes, edges, elements, labels=True, arrows=True, internal=True):

# internal=False prevents the internal edges from being drawn.
         
    for ee in edges:    
        if len(ee['parent_elements']) == 0:
            continue
        
        n1 = ee['nodes'][0]
        n2 = ee['nodes'][1]
        
        pntList = [nodes[n1], nodes[n2]]
        
        if ee['feature']:
            if internal:
                e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=3, color='yellow')
            else:
                e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=1)
        elif ee['bnd'] & internal:
            e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=2, color='blue')
        elif internal:
            e1 = patches.Polygon(pntList, closed=False, fill=False, linewidth=1)                    
        axs.add_patch(e1)
   
    xmin = min([xx[0] for xx in nodes])
    xmax = max([xx[0] for xx in nodes])
    ymin = min([xx[1] for xx in nodes])
    ymax = max([xx[1] for xx in nodes])
    
    dx = xmax-xmin
    dy = ymax-ymin
    
    radius = 0.01 * max(dx, dy)
    
    # Label the edges.
    
    if internal:
        for ie, ee in enumerate(edges):    
            if len(ee['parent_elements']) == 0:
                continue
            
            n1 = ee['nodes'][0]
            n2 = ee['nodes'][1]
            
            p1 = np.array(nodes[n1])
            p2 = np.array(nodes[n2])
            
            dp = p2-p1
            dp = dp / np.linalg.norm(dp)
            
            xy = 0.5 * (p1 + p2)  -2.5*radius * dp 
            dxy = 5*radius * dp
            
            if arrows:
                e1 = patches.Arrow(*xy, *dxy, width=2*radius, color = 'black')
                axs.add_patch(e1)
            
            xy += 2*radius*np.array([-dp[1], dp[0]])
            
            if labels:
                axs.text(*xy, str(ie), color = 'orange')
        
    
    # Plot and label the nodes.
    
    for ix, nn in enumerate(nodes):
        e2 = patches.Circle(nn, radius=radius, color = 'red')
        
        xy = [nn[0] + radius, nn[1] - 4.0*radius]
        
        if labels:
            axs.text(*xy, str(ix), color = 'blue')
        axs.add_patch(e2)
        
    for ix, xx in enumerate(elements):
        if len(xx) == 3:
            # This is not a null or a boundary element.
            
            nodeList = []
            nodeList = nodeList + edges[xx[0]['edge']]['nodes'] \
            + edges[xx[1]['edge']]['nodes']  \
            + edges[xx[2]['edge']]['nodes'] 
            
           
            cent = sum([np.array(nodes[qq]) for qq in nodeList]) / 6.0
            
            if labels:
                axs.text(*cent, str(ix), color = 'red')