from tests.support import unittest2
import sys

from eyam import isolate
from mock import Mock

import tests.isolationfixture
from tests.isolationfixture import (
    MyClass as OriginalMyClass,
    UnmockedClass as OriginalUnmockedClass,
    unmocked_instance as original_unmocked_instance)


class PatchModuleContextManagerTest(unittest2.TestCase):
    def testPatchEverythingInModule(self):
        import UserList
        with isolate(UserList):
            self.assertTrue(isinstance(UserList.UserList.append, Mock))

    def testRestoreEverythingInModule(self):
        import UserList
        OriginalUserList = UserList.UserList
        with isolate(UserList):
            pass
        self.assertEqual(UserList.UserList, OriginalUserList)
        self.assertFalse(isinstance(OriginalUserList, Mock))

    def testExcludeTopLevel(self):
        import UserList
        OriginalUserList = UserList.UserList
        with isolate(UserList, 'UserList'):
            self.assertEqual(UserList.UserList, OriginalUserList)
            self.assertFalse(isinstance(OriginalUserList, Mock))

    def testExcludeSecondLevel(self):
        import UserList
        original_append = UserList.UserList.append
        with isolate(UserList, 'UserList.append'):
            self.assertEqual(UserList.UserList.append.im_func,
                             original_append.im_func)
            self.assertFalse(isinstance(original_append, Mock))

    def testExcludeInstanceMethod(self):
        class MyClass(object):
            def my_method(self):
                return 'return value of my_method'
        class mymodule:
            my_instance = MyClass()
        original_method = mymodule.my_instance.my_method
        original_retval = original_method()
        with isolate(mymodule, 'my_instance.my_method'):
            self.assertTrue(isinstance(mymodule.my_instance, Mock))
            self.assertNotEqual(mymodule.my_instance.my_method, original_method)
            self.assertEqual(mymodule.my_instance.my_method(),
                             'return value of my_method')

    def testExcludeInstanceMethodInClass(self):
        mod = tests.isolationfixture
        original_method = mod.MyClass.unmocked_method
        with isolate(mod, 'MyClass.unmocked_method'):
            self.assertFalse(isinstance(mod.MyClass.unmocked_method, Mock))
            self.assertEqual(mod.MyClass.unmocked_method.im_func,
                             original_method.im_func)
            self.assertEqual(mod.MyClass().unmocked_method.im_func,
                             original_method.im_func)
            instance = mod.MyClass()
            retval = instance.unmocked_method()
            self.assertEqual(retval,
                             'return value of MyClass.unmocked_method')

    def testExcludeClassMethod(self):
        mod = tests.isolationfixture
        original_method = mod.MyClass.class_method
        with isolate(mod, 'MyClass.class_method'):
            self.assertFalse(isinstance(mod.MyClass.class_method, Mock))
            #self.assertEqual(mod.MyClass.class_method, original_method)

            # class_method() returns cls
            self.assertEqual(mod.MyClass.class_method(), mod.MyClass)
            instance = mod.MyClass()
            self.assertEqual(instance.class_method(), mod.MyClass)

    def testClassInstantiation(self):
        with isolate(tests.isolationfixture,
                     'MyClass.unmocked_method'):
            mod = tests.isolationfixture
            self.assertFalse(isinstance(mod.MyClass.unmocked_method, Mock))
            instance = mod.MyClass()
            #self.assertTrue(isinstance(instance, Mock))
            self.assertFalse(isinstance(instance.unmocked_method, Mock))

    def testConstructorIsolation(self):
        """Isolated __init__() is called correctly"""
        original_cls = tests.isolationfixture.MyClass
        original_init = original_cls.__init__
        with isolate(tests.isolationfixture, 'MyClass.__init__'):
            mod = tests.isolationfixture
            self.assertNotEqual(mod.MyClass, original_cls)
            self.assertEqual(mod.MyClass.__init__, original_init)
            self.assertFalse(isinstance(mod.MyClass.__init__, Mock))
            instance = mod.MyClass()
            self.assertEqual(instance.my_attribute,
                             'value of MyClass().my_attribute')

    def testConstructorWithSuper(self):
        """super() is called correctly inside an isolated __init__()"""
        with isolate(tests.isolationfixture,
                     'ClassWithSuperInConstructor.__init__'):
            mod = tests.isolationfixture
            self.assertFalse(
                isinstance(mod.ClassWithSuperInConstructor.__init__, Mock))
            instance = mod.ClassWithSuperInConstructor()
            self.assertEqual(
                instance.my_attribute,
                'value of ClassWithSuperInConstructor().my_attribute')
            self.assertEqual(
                instance.other_attribute,
                'value of ClassWithSuperInConstructor().other_attribute')


import UserList
OriginalUserList = UserList.UserList

class PatchModuleDecorateCallableTest(unittest2.TestCase):
    @isolate(UserList)
    def testPatchEverythingInModule(self):
        self.assertTrue(isinstance(UserList.UserList.append, Mock))

    def testRestoreEverythingInModule(self):
        import UserList
        OriginalUserList = UserList.UserList
        @isolate(UserList)
        def _testRestoreEverythingInModule():
            pass
        _testRestoreEverythingInModule()
        self.assertEqual(UserList.UserList, OriginalUserList)
        self.assertFalse(isinstance(OriginalUserList, Mock))

    @isolate(UserList, 'UserList')
    def testExcludeTopLevel(self):
        self.assertEqual(UserList.UserList, OriginalUserList)
        self.assertFalse(isinstance(OriginalUserList, Mock))

    @isolate(UserList, 'UserList.append')
    def testExcludeSecondLevel(self):
        self.assertEqual(UserList.UserList.append, OriginalUserList.append)
        self.assertFalse(isinstance(OriginalUserList.append, Mock))

    def testExcludeInstanceMethod(self):
        class MyClass(object):
            def my_method(self):
                return self
        class mymodule:
            my_instance = MyClass()
        original_method = mymodule.my_instance.my_method
        original_retval = original_method()

        @isolate(mymodule, 'my_instance.my_method')
        def _testExcludeInstanceMethod():
            self.assertTrue(isinstance(mymodule.my_instance, Mock))
            self.assertNotEqual(mymodule.my_instance.my_method, original_method)
            self.assertEqual(mymodule.my_instance.my_method.im_func,
                             original_method.im_func)
            self.assertEqual(mymodule.my_instance.my_method(), mymodule.my_instance)

        _testExcludeInstanceMethod()


@isolate(tests.isolationfixture,
         'UnmockedClass', 'unmocked_instance',
         'MyClass.unmocked_method', 'my_instance.unmocked_method')
class PatchModuleDecorateClassTest(unittest2.TestCase):
    def testPatchObjectsInModule(self):
        mod = tests.isolationfixture
        self.assertFalse(isinstance(mod.MyClass, Mock))
        self.assertTrue('instance_method' in mod.MyClass.__dict__.keys())
        self.assertTrue(isinstance(mod.MyClass.instance_method, Mock), mod.MyClass.instance_method)
        self.assertTrue(isinstance(
            mod.ClassWithNestedInstances.nested_class_attribute, Mock))
        self.assertTrue(isinstance(mod.my_instance, Mock))
        self.assertTrue(isinstance(mod.my_instance_with_nested_instances, Mock))

    def testExcludeTopLevel(self):
        mod = tests.isolationfixture
        self.assertEqual(mod.UnmockedClass, OriginalUnmockedClass)
        self.assertFalse(isinstance(OriginalUnmockedClass, Mock))
        self.assertEqual(mod.unmocked_instance, original_unmocked_instance)
        self.assertFalse(isinstance(original_unmocked_instance, Mock))

    def testExcludeSecondLevel(self):
        mod = tests.isolationfixture
        self.assertEqual(mod.MyClass.unmocked_method,
                         OriginalMyClass.unmocked_method)
        self.assertFalse(isinstance(OriginalMyClass.unmocked_method, Mock))

    def testExcludeInstanceMethod(self):
        mod = tests.isolationfixture
        self.assertFalse(isinstance(mod.my_instance.unmocked_method, Mock))
        self.assertEqual(mod.my_instance.unmocked_method(),
                         'return value of MyClass.unmocked_method')
