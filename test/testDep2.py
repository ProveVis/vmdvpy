import testDep1

class Clazz2:
    def test(self, obj1):
        obj1.test(self)


if __name__ == '__main__':
    obj1 = testDep1.Clazz1()
    obj2 = Clazz2()
    obj2.test(obj1)