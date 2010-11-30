class MyClass(object):
    def __init__(self):
        self.my_attribute = 'value of %s().my_attribute' % (
            self.__class__.__name__)

    def instance_method(self):
        return self

    def unmocked_method(self):
        return 'return value of MyClass.unmocked_method'

    @classmethod
    def class_method(cls):
        return cls

    @staticmethod
    def static_method():
        return True


class UnmockedClass(object):
    def instance_method(self):
        return 'return value of UnmockedClass.instance_method()'


class ClassWithNestedInstances(object):
    nested_class_attribute = MyClass()

    def __init__(self):
        self.nested_instance_attribute = MyClass()


class ClassWithSuperInConstructor(MyClass):
    def __init__(self):
        #import ipdb;ipdb.set_trace()  # FIRE DEBUGGER
        print 'ClassWithSuperInConstructor.__init__, mro = %r' % list(self.__class__.__mro__)
        super(ClassWithSuperInConstructor, self).__init__()
        self.other_attribute = 'value of %s().other_attribute' % (
            self.__class__.__name__)


my_instance = MyClass()

my_instance_with_nested_instances = ClassWithNestedInstances()

unmocked_instance = MyClass()


def my_function():
    return 'return value of my_function'


def unmocked_function():
    return 'return value of unmocked_function'
