# Delaunay Meshing Videos
<strong>Purpose:</strong> Creation of animations that depict iterations from the Delaunay algorithm for the generation of optimal, unrefined triangular meshes.

## Introduction

<p>
The purpose of this project is to demonstrate how the 'frame-grabbing' portion of the Python library matplotlib can be used to generate an animation of the
Delaunay triangulation algorithm. The objective of Delaunay triangulation is to generate a mesh of geometrically optimal triangles within a prescribed boundary.
The work presented here entails the first step of this process, which is to generate the 'unrefined' mesh, in which the only nodes present within the mesh are those 
that define the boundary itself. If the mesh were to be used as part of an Engineering analysis (such as Finite Element modeling), then an additional refinement stage is required,
wherein nodes are then added to the interior of the boundary to improve mesh quality. The animations produced here only capture the first stage of meshing.
</p>
<p>
An example of the type of animation that can be generated is shown in the .mp4 video that follows. 
	
https://user-images.githubusercontent.com/28033215/152684731-83638954-8195-4f29-a57e-888f02dcd39f.mp4

<p align="center">
    <strong><small>Example of an unrefined Delaunay Triangulation</small></strong>
</p>

## Delaunay Meshing


<p align="center">
    <img src="https://raw.githubusercontent.com/JerryGreenough/Delaunay-Meshing-Videos/master/images/boundary_nodes.png" width="300" height="300">  
</p>

<p align="center">
    <img src="https://raw.githubusercontent.com/JerryGreenough/Delaunay-Meshing-Videos/master/images/mesh.png" width="300" height="300">  
</p>

## Frame Grabbing

<p>
The frame-grabbing functionality is implemented using the Python graphics library matplotlib. This library has a submodule named 'animation', 
which contains the FFMpegWriter class.
</p>

```   
from matplotlib.animation import FFMpegWriter
```

During the initialization phase, a number of objects are created for later reference by the frame-grabbing functions during the Delaunay
triangulation process. This is achieved with a call to the mesh object's ```vplot_init()``` meothd.

```

def vplot_init(self, fpath, figsize=(6,6)):

    fle = Path(fpath)
    fle.touch(exist_ok=True)
    self.fpath = fpath
    
    self.fig, self.axs = plt.subplots(1,1, figsize=figsize)
    self.writer = FFMpegWriter(fps=2)
		
def addBoundaryLoopWithVideo(self, nodeList):
    with self.writer.saving(self.fig, self.fpath, 200):
        self.addBoundaryLoop(nodeList, video=True)

def addBoundaryLoop(self, nodeList, video=False):

    self.addNodes(nodeList)
    for ixn in range(len(nodeList)-1):
        self.insertBoundaryEdge([ixn, ixn+1])
        if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)

    self.insertBoundaryEdge([len(nodeList)-1, 0])
    if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)
    
    self.removeNonFeatureBoundaryEdges()
    if video: self.vplot(self.writer, self.fig, self.axs, labels=False, arrows=False)
```
  
## Example

```
m6 = mesh()

nodeList = [[0.0, 0.0], [2.0, 0.0], [1.0, 3.0], [0.5, 2.5], [-0.3, 1.9], [-0.3, 0.4]]

fpath = ".\m6.mp4"

m6.vplot_init(fpath, figsize=(6,6))  # Initialize the frame-grabbing functionality.
m6.addBoundaryLoopWithVideo(nodeList)
```

## Requirements

In order for the frame-grabbing to work with matplotlib, it may be necessary to install (and sometimes
uninstall and reinstall) ffmpeg and ffmpeg-python.

```
conda install ffmpeg
pip install ffmpeg-python
```


