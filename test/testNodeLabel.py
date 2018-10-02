import vtk



g = vtk.vtkMutableDirectedGraph()



# Create 3 vertices

v1 = g.AddVertex()

v2 = g.AddVertex()

v3 = g.AddVertex()

v4 = g.AddVertex()



# Create a fully connected graph

g.AddGraphEdge(v1, v2)

g.AddGraphEdge(v1, v3)

g.AddGraphEdge(v1, v4)



# Create the edge weight array

labels = vtk.vtkStringArray()

labels.SetNumberOfComponents(1)

labels.SetName("labels")



# Set the edge labels

labels.InsertNextValue('a')

labels.InsertNextValue('b')

labels.InsertNextValue('c')

labels.InsertNextValue('d')



# Add the edge weight array to the graph

g.GetVertexData().AddArray(labels)
# g.GetVertexData().



graphLayoutView = vtk.vtkGraphLayoutView()

graphLayoutView.SetColorVertices(True)

graphLayoutView.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

graphLayoutView.SetLayoutStrategyToCone()

graphLayoutView.SetInteractionModeTo3D()

graphLayoutView.AddRepresentationFromInput(g)

graphLayoutView.SetVertexLabelArrayName("labels")

graphLayoutView.SetVertexLabelVisibility(True)




theme = vtk.vtkViewTheme.CreateMellowTheme()

theme.SetLineWidth(4)

theme.SetPointSize(32)

graphLayoutView.ApplyViewTheme(theme)

theme.FastDelete()

graphLayoutView.SetVertexLabelVisibility(not graphLayoutView.GetVertexLabelVisibility())



graphLayoutView.ResetCamera()

graphLayoutView.Render()



graphLayoutView.GetInteractor().Start()
