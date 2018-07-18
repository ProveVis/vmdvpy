import json
import vtk
import utils


def parseLabel(label):
    result = ''
    flag = False

    for c in label:
        if c == '[':
            flag = True
        if c == ']':
            flag = False

        result += c
        if (c == ';' or c == '{' or c == '}') and not flag:
            result += '\n'

    return result


def parseNode(node):
    result = 'node:' + node['id'] + '\n'
    result += 'state:' + node['state'] + '\n'
    result += 'label:' + parseLabel(node['label']) + '\n'

    return result



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
        self.view.SetGlyphType(vtk.vtkGraphToGlyphs.SPHERE)

        self.view.SetInteractionModeTo3D()
        self.view.SetLayoutStrategyToCone()

        

        self.vertexColors = vtk.vtkIntArray()
        self.vertexColors.SetNumberOfComponents(1)
        self.vertexColors.SetName("color")
        self.lookup = vtk.vtkLookupTable()
        self.lookup.Build()
        self.vertexColors.InsertValue(0,0)
        self.graph.GetVertexData().AddArray(self.vertexColors)
        self.view.SetVertexColorArrayName("color")
        # self.lookup.SetNumberOfTableValues(1)
        # self.lookup.SetTableValue(0,0.0,1.0,0.0)   

        self.view.SetColorVertices(True)
        self.view.SetEdgeSelection(False)

        self.vertexHeight = {}
        self.vertexHeight[0] = 0
        self.treeHeight = 1
        self.colors = utils.GradualColoring(utils.RGB(0,0,1), utils.RGB(0,1,0))

        theme = vtk.vtkViewTheme.CreateOceanTheme()
        theme.SetLineWidth(2)
        theme.SetPointSize(20)
        
        theme.FastDelete()
        theme.SetPointLookupTable(self.lookup)
        self.view.ApplyViewTheme(theme)

        rep = self.view.GetRepresentation(0)
        link = rep.GetAnnotationLink()

        def selectionCallback(caller, event):
            sel = caller.GetCurrentSelection()
            node0 = sel.GetNode(0)
            field_type = node0.GetFieldType()
            if field_type == 3:
                sel_list0 = node0.GetSelectionList()
                # get the first delected vertex
                if sel_list0.GetNumberOfTuples() > 0:
                    vert_id = sel_list0.GetValue(0)
                    self.info(vert_id)
            else:
                self.text_actor.SetInput('')

        link.AddObserver("AnnotationChangedEvent", selectionCallback)

        self.view.GetRenderWindow().SetSize(600, 600)

        # Create the TextActor
        text_representation = vtk.vtkTextRepresentation()
        text_representation.GetPositionCoordinate().SetValue(0.6, 0.0)
        text_representation.GetPosition2Coordinate().SetValue(0.4, 1.0)
        # text_representation.SetTextActor(text_actor)

        self.text_widget.CreateDefaultRepresentation()
        self.text_widget.SetRepresentation(text_representation)
        self.text_widget.SetInteractor(self.view.GetInteractor())
        self.text_widget.SetTextActor(self.text_actor)
        self.text_widget.SelectableOff()
        self.text_widget.On()

        # keyboard event
        def Keypress(obj, event):
            print(type(obj))
            key = obj.GetKeySym()
            # step
            if key == 'space':
                self.step()
            # all
            if key == 'Return':
                self.step(False)
            if key == 'p':
                self.printColorData()
            print(key)
            print(self.view.GetVertexColorArrayName())

        # self.view.GetInteractor().AddObserver("KeyPressEvent", Keypress)
        # self.view.GetInteractor().AddObserver("KeyPressEvent", lambda obj,event: print(obj.GetKeySym()))
        self.view.GetInteractor().AddObserver(vtk.vtkCommand.KeyPressEvent, Keypress)

        pass

    def info(self, vertex):
        node_id = self.vert_node_map[vertex]
        self.text_actor.SetInput(parseNode(self.node_data[node_id]))

    def printColorData(self):
        print('ColorArray:', self.vertexColors.GetNumberOfTuples())
        for i in range(self.vertexColors.GetNumberOfTuples()):
            print('(',i,',', self.vertexColors.GetValue(i) ,')', end=';')
        print('\nColorTable:', self.lookup.GetNumberOfTableValues())
        for j in range(self.lookup.GetNumberOfTableValues()):
            print('(', j, self.lookup.GetTableValue(j), ')', end=';\n')
        print('\nvertexHeight:\n', self.vertexHeight)

    # process a single line, return True if a edge is added
    def step(self, flag=True):

        while True:
            line = self.file.readline()

            if not line:
                break

            try:
                data = json.loads(line)
                # print(data)
                if data['type'] == 'add_node':
                    id = data['node']['id']
                    self.node_data[id] = data['node']

                elif data['type'] == 'add_edge':
                    from_id = data['from_id']
                    to_id = data['to_id']

                    if from_id not in self.node_vert_map:
                        vert_id = self.graph.AddVertex()
                        self.vertexColors.InsertValue(vert_id,vert_id)
                        self.node_vert_map[from_id] = vert_id
                        self.vert_node_map[vert_id] = from_id
                    if to_id not in self.node_vert_map:
                        vert_id = self.graph.AddVertex()
                        self.vertexColors.InsertValue(vert_id,vert_id)
                        self.node_vert_map[to_id] = vert_id
                        self.vert_node_map[vert_id] = to_id

                    print ('added edge',from_id,'-->',to_id)

                    self.graph.AddEdge(self.node_vert_map[from_id], self.node_vert_map[to_id])

                    self.vertexHeight[self.node_vert_map[to_id]] = self.vertexHeight[self.node_vert_map[from_id]] + 1
                    if self.vertexHeight[self.node_vert_map[to_id]] + 1 > self.treeHeight:
                        self.treeHeight = self.vertexHeight[self.node_vert_map[to_id]] + 1

                    self.colors.insertColorOfVertex(self.lookup, self.node_vert_map[to_id], self.vertexHeight[self.node_vert_map[to_id]], self.treeHeight) 

                    

                            # add a pedigree array to vertex
                    self.vertIds = vtk.vtkIdTypeArray()
                    numVertices = self.graph.GetNumberOfVertices()
                    # print("number of vertices:", numVertices)
                    self.vertIds.SetNumberOfTuples(numVertices)

                    print('wtf',numVertices)
                    for i in range(0, numVertices):
                        self.vertIds.SetValue(i, i)

                    self.graph.GetVertexData().SetPedigreeIds(self.vertIds)

                    if flag:
                        #self.info(self.node_vert_map[to_id])
                        break

            except Exception as e:
                print('failed to parse line:', e)
                break

        self.tree.CheckedShallowCopy(self.graph)
        self.view.ResetCamera()
        self.view.Render()

    # load the json file
    def load(self, file):

        self.file = open(file, 'r')
        self.step()

    # show
    def show(self):
        camera = self.view.GetRenderer().GetActiveCamera()
        camera.SetPosition(0, 1, 0)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)

        self.view.ResetCamera()
        self.view.Render()
        self.view.GetInteractor().Start()


if __name__ == '__main__':
    vis = PTVisualizer()
    vis.load('graphs_json/test3.json')
    vis.show()



