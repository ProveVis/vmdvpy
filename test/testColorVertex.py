
import vtk
class PTVisualizer:

    tree = vtk.vtkTree()
    view = vtk.vtkGraphLayoutView()
    graph = vtk.vtkMutableDirectedGraph()

    text_actor = vtk.vtkTextActor()
    text_widget = vtk.vtk.vtk.vtkTextWidget()

    # store data and mapping
    node_vert_map = {}
    vert_node_map = {}
    node_data = {}

    file = None

    def __init__(self):
        # self.tree.a
        self.text_actor.GetTextProperty().SetColor((0, 0, 1))
        self.text_actor.SetTextScaleModeToProp()

        self.view.AddRepresentationFromInput(self.tree)
        # view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategyToCone()

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)

        # theme = vtk.vtkViewTheme.CreateOceanTheme()
        # theme.SetLineWidth(4)
        # theme.SetPointSize(32)
        # self.view.ApplyViewTheme(theme)
        # theme.FastDelete()

        rep = self.view.GetRepresentation(0)
        link = rep.GetAnnotationLink()

        self.view.GetRenderWindow().SetSize(600, 600)

        v1 = self.graph.AddVertex()
        v2 = self.graph.AddVertex()
        v3 = self.graph.AddVertex()
        v4 = self.graph.AddVertex()

        print(v1,",",v2,",",v3,",",v4)

        self.graph.AddEdge(v1,v2)
        self.graph.AddEdge(v1,v3)
        self.graph.AddEdge(v2,v4)

        # self.view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

        

        self.vertexColors = vtk.vtkIntArray()
        self.vertexColors.SetNumberOfComponents(1)
        self.vertexColors.SetName("color")
        self.lookup = vtk.vtkLookupTable()
        self.lookup.SetNumberOfTableValues(4)
        self.lookup.SetTableValue(0,1.0,0.0,0.0)    # red
        self.lookup.SetTableValue(1,0.0,1.0,0.0)    # green
        self.lookup.SetTableValue(2,0.0,0.0,1.0)    # blue
        self.lookup.SetTableValue(3,1.0,1.0,1.0)    # white
        self.lookup.Build()

        self.vertexColors.InsertNextValue(0)
        self.vertexColors.InsertNextValue(1)
        self.vertexColors.InsertNextValue(2)
        self.vertexColors.InsertNextValue(3)
        # self.vertexColors.InsertValue(v1,0)
        # self.vertexColors.InsertValue(v2,1)
        # self.vertexColors.InsertValue(v3,2)
        # self.vertexColors.InsertValue(v4,3)

        # self.view.SetLayoutStrategyToPassThrough();

        self.graph.GetVertexData().AddArray(self.vertexColors)
        self.view.SetVertexColorArrayName("color")
        self.view.ColorVerticesOn()
        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.SetLineWidth(1)
        theme.SetPointSize(20)
        theme.SetPointLookupTable(self.lookup)
        self.view.ApplyViewTheme(theme)

        self.tree.CheckedShallowCopy(self.graph)

        self.vertexColors.InsertValue(v2, 2)
        self.tree.CheckedShallowCopy(self.graph)


        self.vertexColors1 = vtk.vtkIntArray()
        self.vertexColors1.SetNumberOfComponents(1)
        self.vertexColors1.SetName("color")
        self.vertexColors1.InsertValue(v1,0)
        self.vertexColors1.InsertValue(v2,2)
        self.vertexColors1.InsertValue(v3,1)
        self.vertexColors1.InsertValue(v4,3)
        self.graph.GetVertexData().AddArray(self.vertexColors1)
        self.view.SetVertexColorArrayName("color")


        # updating colors of each vertex
        self.vertexColors.InsertValue(v2,v2)
        self.lookup.SetNumberOfTableValues(4)
        self.lookup.SetTableValue(0,1.0,1.0,0.0)    
        self.lookup.SetTableValue(1,1.0,0.0,0.0)    
        self.lookup.SetTableValue(2,0.0,1.0,0.0)    
        self.lookup.SetTableValue(3,1.0,1.0,1.0)    
        self.tree.CheckedShallowCopy(self.graph)

        v5 = self.graph.AddVertex()
        print(v5)
        self.vertexColors1.InsertValue(v5, v5)
        self.lookup.SetNumberOfTableValues(5)
        self.lookup.SetTableValue(0,1.0,1.0,0.0)    
        self.lookup.SetTableValue(1,1.0,0.0,0.0)    
        self.lookup.SetTableValue(2,0.0,1.0,0.0)    
        self.lookup.SetTableValue(3,1.0,1.0,1.0)
        self.lookup.SetTableValue(4,0.5,0.8,0.5)    
        
        self.graph.AddEdge(v1, v5)
        self.tree.CheckedShallowCopy(self.graph)
        self.graph.RemoveVertex(v5)
        self.tree.CheckedShallowCopy(self.graph)
        v6 = self.graph.AddVertex()
        self.vertexColors1.InsertValue(v6, v6)
        print(v6)
        self.graph.AddEdge(v1, v6)
        self.tree.CheckedShallowCopy(self.graph)
        # Create the TextActor
        # text_representation = vtk.vtkTextRepresentation()
        # text_representation.GetPositionCoordinate().SetValue(0.6, 0.0)
        # text_representation.GetPosition2Coordinate().SetValue(0.4, 1.0)

        # self.text_widget.CreateDefaultRepresentation()
        # self.text_widget.SetRepresentation(text_representation)
        # self.text_widget.SetInteractor(self.view.GetInteractor())
        # self.text_widget.SetTextActor(self.text_actor)
        # self.text_widget.SelectableOff()
        # self.text_widget.On()
        def selection(obj, e):
            # print('selection triggered')
            sel = obj.GetCurrentSelection()
            selvs = sel.GetNode(0).GetSelectionList()
            print('selected', selvs.GetNumberOfTuples(),'nodes')
            for idx in range(selvs.GetNumberOfTuples()):
                print('node', selvs.GetValue(idx))


        self.view.GetRepresentation(0).GetAnnotationLink().AddObserver("AnnotationChangedEvent", selection)

    def show(self):
        camera = self.view.GetRenderer().GetActiveCamera()
        camera.SetPosition(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)

        self.view.ResetCamera()
        self.view.GetInteractor().Initialize()
        self.view.Render()
        self.view.GetInteractor().Start()



if __name__ == '__main__':
    vis = PTVisualizer()
    # vis.load('graphs_json/digraph.txt')
    vis.show()
