
import abc
import graph

class Test:
    @abc.abstractmethod
    def test(self):
        print('class Test')

class TestSub1(Test):
    attri1 = 1
    def test(self):
        print('class TestSub1')

class TestSub2(Test):
    attri2 = '2'
    def test(self):
        print('class TestSub2')

if __name__ == '__main__':
    # test = TestSub1()
    # test.test()
    # print(test.attri1)

    # test = TestSub2()
    # test.test()
    # print(test.attri2)
    tree = graph.Tree([])
    tree.addNode(0,graph.Node())
    tree.addNode(1,graph.Node())
    tree.addNode(2,graph.Node())
    tree.addNode(3,graph.Node())
    tree.addNode(4,graph.Node())
    tree.addNode(5,graph.Node())
    tree.addNode(6,graph.Node())
    tree.addEdge(0,1)
    tree.addEdge(0,2)
    tree.addEdge(2,3)
    tree.addEdge(2,6)
    tree.addEdge(3,4)
    tree.addEdge(3,5)
    tree.printInfo()
    tree.removeNode(3)
    tree.printInfo()
    tree.setRoot(2)
    tree.printInfo()
    tree.setRoot(0)
    tree.printInfo()


# if __name__ == '__main__':
