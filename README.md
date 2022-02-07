# Delaunay Meshing Videos
<strong>Purpose:</strong> Creation of animations that depict iterations from the Delaunay algorithm for the generation of optimal, unrefined triangular meshes.

## Introduction

<p>
The purpose of this project is to demonstrate how the Animation module of the Python library <code>matplotlib</code> can be used to generate an mp4 video that illustrates the
Delaunay triangulation algorithm. The objective of Delaunay triangulation is to generate a mesh of geometrically optimal triangles within a prescribed boundary.
The work presented here demonstrates the first step of this process, which is to generate the 'unrefined' mesh, in which the only nodes present within the mesh are those 
that define the boundary itself. If the mesh were to be used as part of an Engineering analysis (such as Finite Element modeling), then a second 'refinement' stage 
would be required, wherein additional nodes are inserted into the interior of the boundary in order to improve mesh quality. 
</p>

<p>
The following images illustrates a simple Delaunay triangulation (right hand image) constructed from a boundary loop (left hand image). The nodes that define the boundary are represented by red circles. The edges that form the boundary loop are blue, with the remaining interior edges being colored black.
</p>

<p float="left">
  <img src="https://raw.githubusercontent.com/JerryGreenough/Delaunay-Meshing-Videos/master/images/boundary_nodes.png" width="400" height="400"/>
  <img src="https://raw.githubusercontent.com/JerryGreenough/Delaunay-Meshing-Videos/master/images/mesh.png" width="400" height="400"/> 
</p>

<p align="center">
    <strong><small>Boundary loop (left) and a Delaunay mesh of its interior (right)</small></strong>
</p>

<p>
An example of an animation of the Delaunay triangulation algorithm is shown in the following mp4 video. The video starts with just the boundary nodes (in red). 
Each subsequent frame of the animation depicts the state of the mesh after the introduction of a boundary edge that is defined between two adjacent nodes of the boundary loop. The boundary edges are added between consecutively defined nodes and in an order that is counter-clockwise. The element edges that emerge during the process are colored black save for the boundary edges, which are colored blue. The meshing algorithm maintains a convex hull of all nodes that are contained in the boundary edges that have been added up to that point. This necessitates the generation of temporary edges and elements that lie outside the blue prescribed boundary edges. For any given iteration of the alogrithm, the edges of the convex hull of all hitherto-added edge nodes are colored gray. The final iteration of the algorthim removes all elements that lie outside the prescribed boundary loop to reveal the boundary loop plus any elements that are contained in its interior.
</p>

<p align="center">
<video src='https://user-images.githubusercontent.com/28033215/152694935-e5a97fbb-fac5-4f64-b7f7-5be8573b562c.mp4' width=500/>
</p>

<p align="center">
    <strong><small>Example of an Unrefined Delaunay Triangulation</small></strong>
</p>

## Delaunay Meshing
<p>
The Delaunay Meshing functionality used in this project is harnassed in a dedicated <code>mesh</code> class.
A mesh can be generated and displayed to the screen using a few lines of Python. In the following snippet, the
<code>mesh</code> class is imported from <code>delaunay_mesh.py</code> and a sample list of boundary nodes is imported from 
<code>boundaries.py</code>. The <code>square_oo()</code> function returns a counter-clockwise ordered list 
of <code>[x,y]</code> co-ordinate pairs which represent the locations of the boundary nodes. 
A mesh object is created, with boundary definintion and subsequent triangulation taking place
by calling the mesh object method <code>addBoundaryLoop(nodeList)</code>. 
Finally, the <code>plot()</code>
method (which uses the matplotlib <code>patches</code> library) depicts the resulting mesh on the screen.

A simple, unrefined mesh can be created using the following, ....
</p>

```
from delaunay_mesh import mesh
from boundaries import square_oo

nodeList = square_oo()

m8 = mesh()							# Create a mesh object.					
m8.addBoundaryLoop(nodeList)        # Generate the mesh.       
m8.plot(labels=False, arrows=False) # Draw the mesh.
```

<p> which should produce a mesh like this ... </p>

<p align="center">
<img src="https://raw.githubusercontent.com/JerryGreenough/Delaunay-Meshing-Videos/master/images/mesh_oo.png" width="300" height="300"/>
</p>


<p>
Note that the co-ordinates of the last node in the node list should not be the same as those of the first node. 
The <code>addBoundaryLoop(nodeList)</code>
call will take care of connecting the final node to the first node. 
Additional sample boundaries are contained in the repository's <code>boundaries.py</code> source file.
The matplotlib patches drawing commands are contained in the repository's <code>draw.py</code> file.
</p>

<p>
Many more examples of how to perform the 
mesh generation are contained in the accompanying <code>mesh.ipynb</code> Jupyter Notebook.
</p>

## Frame Grabbing

<p>
The frame-grabbing functionality is implemented using the Python graphics library <code>matplotlib</code>. This library has a submodule named <code>animation</code>, 
which contains the FFMpegWriter class. It is an instance of this class that serializes the content of a matplotlib Figure object into a frame of an mp4 file. The FFMpegWriter
class is imported using the following code:
</p>

```   
from matplotlib.animation import FFMpegWriter
```
<p>
The key ingredients of the process for writing frames to an .mp4 file are:
</p>

* A matplotlib Figure and Axis pair
* An instance of the matplotlib.animation MovieWriter class
* A MovieWriter context manager that hosts the frame-grabbing process
* The MovieWriter object's grab_frame() method - which saves the state of the Figure to a video frame

<p>
The matplotlib Figure and Axis objects are created in the standard way, with the width and height of the figure both
set to 6 inches:
</p>

```
figsize=(6,6)
fig, axs = plt.subplots(1,1, figsize=figsize)
```

<p>
The MovieWriter object is instantiated with the number of frames per second set to 2.
</p>

```
writer = FFMpegWriter(fps=2)
```

<p>
The process makes use of a context manger <code>saving</code> associated with the MovieWriter 
instance <code>writer</code>. The MovieWriter context manager <code>saving</code> is initialized with three parameters:
</p>

* The matplotlib Figure to which drawing commands are written.
* The name of the .mp4 file to which the animation data should be written.
* The DPI (or resolution) for the file. This controls the size in pixels of the resulting movie file.

<p>
The following 'conceptual' Python code illustrates how the MovieWriter object is instructed to extract information from
the matplotlib Figure object and write it to the mp4 video file. An 'iteration' of the Delaunay algorithm corresponds to the 
insertion into the mesh of a boundary edge. The mesh is duly updated (<code>update_mesh()</code>) and the Figure object is
updated to reflect changes to the mesh (<code>update_figure()</code>). The content of the updated Figure object is then
written to the mp4 file by calling the MovieWriter object's grab_frame() method. It is the earlier instantiation of the
MoviewWriter's context manager with the appropraite <code>file_name</code> that ensures the frame data is written to the 
desired file.
</p>

```
file_name = 'something.mp4'
	
with self.writer.saving(fig, file_name, 200):
	for iteration in Delaunay_algorithm:
		new_mesh = update_mesh()
		
		# Update the Matplotlib figure 'fig'
		
		update_figure(fig, new_mesh)
		
		# Grab the current state of the matplotlib Figure 'fig'.
	
		writer.grab_frame()
```
<p>
The process shown above is implemented by methods associated with the `mesh` object. The key methods are `vplot_init()`, `vplot()` and `addBoundaryLoop()`, 
all of which can be viewed in the <code>delaunay_mesh.py</code> source file.
During the initialization phase, a number of objects are created for later reference from the <code>MovieWriter</code> object during the Delaunay
triangulation process. This is achieved with a call to the mesh object's <code>vplot_init()</code> method. 
</p>

```
def vplot_init(self, fpath, figsize=(6,6)):

    fhandle = Path(fpath)
    fhandle.touch(exist_ok=True) # Create the mp4 file if it doesn't already exist.
	
    self.fpath = fpath
    
    self.fig, self.axs = plt.subplots(1,1, figsize=figsize)
    self.writer = FFMpegWriter(fps=2)
```
<p>
The implementation of the <code>update_figure()</code> function  is provided by the mesh object's <code>`vplot()</code> method. 
This method also contains the  call to the MovieWriter object's <code>grab_frame()</code>. The implementation of the
<code>update_mesh()</code> function is in the <code>insertBoundaryEdge()</code> function.
</p>

```
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

<p>
Here is a simple example of how to go from a list of boundary nodes to an animation 
of the Delaunay triangulation of its interior.
</p>

```
from delaunay_mesh import mesh

m6 = mesh() # Create a mesh object.

# Define a simple boundary loop.

nodeList = [[0.0, 0.0], [2.0, 0.0], [1.0, 3.0], [0.5, 2.5], [-0.3, 1.9], [-0.3, 0.4]]

# Specify the file that should contain the .mp4 video as well as how large the size of each
frame of the video should be.

fpath = ".\m6.mp4"
m6.vplot_init(fpath, figsize=(6,6))  # Initialize the frame-grabbing functionality.

# Add the boundary edges defined by consecutive nodes from the node list, recording the Delaunay
# mesh that results in each frame.

m6.addBoundaryLoopWithVideo(nodeList)
```

## Requirements

In order for the frame-grabbing to work with matplotlib, it may be necessary to install (and sometimes
uninstall and reinstall) the <code>ffmpeg</code> tool as well as the <code>ffmpeg-python</code> library.

```
conda install ffmpeg
pip install ffmpeg-python
```

Additional information on ffmpeg and ffmpeg-python can be found here:

https://www.ffmpeg.org/

https://github.com/kkroening/ffmpeg-python


