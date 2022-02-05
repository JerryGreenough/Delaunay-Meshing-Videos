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

https://user-images.githubusercontent.com/28033215/152605590-f96d97b6-c4c1-4f1a-be33-4a3f9f41a6f4.mp4

<p align="center">
    <strong><small>Example of an unrefined Delaunay Triangulation</small></strong>
</p>

## Frame Grabbing

<p>
The frame-grabbing functionality has been implemented using the Python graphics library matplotlib. This library has a submodule named 'animation', 
which contains the FFMpegWriter class.
    
    from matplotlib.animation import FFMpegWriter

</p>


