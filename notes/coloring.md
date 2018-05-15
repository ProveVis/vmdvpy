# Coloring issues

* **How to change colors of vertices?**

  Colors of vertices or edges can be set up or changed by two steps: first, define a color mapping which maps a scalar value to a specific color, and then, define the scalar value for each vertex or edge. After doing so, the color of vertices or edges are automatically set up.

  The `vtkLookupTable` object is used to define the color mapping of the 3D graph, while the `vtkIntArray` object is used to define the index of each vertex (or edge) in the color mapping.

* **What's the the way `vtkLookupTable` and `vtkIntArray` take effect?**

  We use examples to express the functionality of both `vtkLookupTable` and `vtkIntArray`.

  For instance, the following code built a color mapping which maps `0` to the red color, `1` to the green bolor and `2` to the blue color.

  ```python
    lookup = vtk.vtkLookupTable()
    lookup.SetNumberOfColors(3)
    lookup.SetTableValue(0,1,0,0) # red
    lookup.SetTableValue(1,0,1,0) # green
    lookup.SetTableValue(2,0,0,1) # blue
    lookup.Build()
  ```

  With the above color mapping, we can define the color of each vertex, as demonstrationed by the following code, where vertex `v0` in the graph `graph` has red color, `v1` has green color, and `v2` has blue color.

  ```python
    graph = vtk.vtkMutableDirectedGraph()
    colorArray = vtk.vtkIntArray()
    colorArray.SetNumberOfComponents(1)
    v0 = graph.AddVertex()
    v1 = graph.AddVertex()
    v2 = graph.AddVertex()
    colorArray.InsertValue(v0, 0) # vertex v0 has red color
    colorArray.InsertValue(v1, 1) # vertex v1 has green color
    colorArray.InsertValue(v2, 2) # vertex v2 has blue color
  ```

  It should be noticed that the `InsertValue` method of the `colorArray` object defines the "relative" index in the color mapping for each vertex, not the "exact" index. To be more precise, in the following code, even if we insert different values for each vertex, the color of each vertex remains the same with that in the above code. The reason is that, `4` (resp. `9`) is the second (resp. third) value among `0`, `4`, and `9`, so vertex `v1` (resp. `v2`) will have the second (resp. third) color in the color mapping, which is green (resp. blue).

  ```python
    colorArray.InsertValue(v0, 0) # vertex v0 has red color
    colorArray.InsertValue(v1, 4) # vertex v1 still has green color
    colorArray.InsertValue(v2, 9) # vertex v2 still has blue color
  ```

* **How to change the colors of specific vertices dynamically?**

  Usually, values in the `vtkIntArray` object do not change: when a vertex `vid` is added to the 3D graph, insert a value equals to `vid` for this vertex in the `vtkIntArray` object, as demonstrated in the following code.

  ```python
    vid = graph.AddVertex()
    colorArray.InsertValue(vid, vid)
  ```

  Then, when
  * **adding a new vertex:**

    insert a new table value into the `vtkLookupTable` object.
  * **removing a vertex:**

    remove the corresponding table value from the `vtkLookupTable` object.
  * **changing the color of a specific vertex:**

    change the corresponding table value in the `vtkLookupTable` object.

**Note: operations for edges are analogous to that for vertices.**
<!--  
* For Trees

  * **Adding vertices:** If the height of the tree does not increase, then update the `vtkLookupTable` object. In addition, update the `vtkIntArray` object.
  * **Removing vertices:** Do nothing.
  * **Highlighting vertices:** Update the `vtkIntArray` object.

* For DiGraphs

  * **Adding vertices:** Update both the `vtkLookupTable` and `vtkIntArray` objects.
  * **Highlighing vertices:** Update the `vtkIntArray` object.
-->
  ​

