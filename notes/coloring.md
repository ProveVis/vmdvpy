
## Coloring issues

* For Trees

  * **Adding vertices:** If the height of the tree does not increase, then update the `vtkLookupTable` object. In addition, update the `vtkIntArray` object.
  * **Removing vertices:** Do nothing.
  * **Highlighting vertices:** Update the `vtkIntArray` object.

* For DiGraphs

  * **Adding vertices:** Update both the `vtkLookupTable` and `vtkIntArray` objects.
  * **Highlighing vertices:** Update the `vtkIntArray` object.

  ​

