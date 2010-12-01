eyam is a Python module that provides isolation of objects,
functions and methods by mocking most of the contents in a module with
Mock objects (from Michael Foord's Mock library). It removes the need
to individually mock all objects which the method under test depends
on. After performing an action, you can inspect calls made by the code
under test in the usual way with tools provided by the mock.py
library.

mock is tested on Python version 2.6.

* `eyam on GitHub (repository and issue tracker) <http://github.com/akaihola/eyam>`_

eyam is very easy to use and is designed for use with
Michael Foord's Mock library.

You can mock classes, instances, functions and methods. The syntax is
straightforward:

    >>> from eyam import isolate
    >>> import tests.isolationfixture as mod

    >>> def dump(expr):
    ...     print '%s == %r' % (expr, eval('mod.%s' % expr))

Whole classes can be isolated:

    >>> with isolate(mod, 'UnmockedClass'):  #doctest:+ELLIPSIS
    ...     dump('MyClass')
    ...     dump('UnmockedClass')
    MyClass == <mock.ClassMock object at 0x...>
    UnmockedClass == <class 'tests.isolationfixture.UnmockedClass'>

Instances of an isolated class work as normally. Instances of mocked
classes are Mock objects, so their methods return Mock objects:

    >>> with isolate(mod, 'UnmockedClass'):  #doctest:+ELLIPSIS
    ...     dump('MyClass().bogus()')
    ...     dump('UnmockedClass().instance_method()')
    MyClass().bogus() == <mock.Mock object at 0x...>
    UnmockedClass().instance_method() == 'return value of UnmockedClass.instance_method()'

Instances can be isolated as well:

    >>> with isolate(mod, 'unmocked_instance'):  #doctest:+ELLIPSIS
    ...     dump('my_instance')
    ...     dump('unmocked_instance')
    my_instance == <mock.Mock object at 0x...>
    unmocked_instance == <tests.isolationfixture.MyClass object at 0x...>

Individual methods of an instance can be isolated. The instance
becomes a Mock object, but the original method is re-bound to it:

    >>> with isolate(mod, 'my_instance.unmocked_method'):  #doctest:+ELLIPSIS
    ...     dump('my_instance')
    ...     dump('my_instance.unmocked_method')
    ...     dump('my_instance.unmocked_method()')
    my_instance == <mock.Mock object at 0x...>
    my_instance.unmocked_method == <bound method ?.unmocked_method of <mock.Mock object at 0x...>>
    my_instance.unmocked_method() == 'return value of MyClass.unmocked_method'

All other methods and attributes of the instance are mocked.

    >>> with isolate(mod, 'my_instance.unmocked_method'):  #doctest:+ELLIPSIS
    ...     dump('my_instance.instance_method')
    ...     dump('my_instance.instance_method()')
    my_instance.instance_method == <Mock name='mock.instance_method' id='...'>
    my_instance.instance_method() == <mock.Mock object at 0x...>

Non-isolated instances become Mock objects, and their methods return
Mock objects:

    >>> with isolate(mod, 'my_instance.unmocked_method'):  #doctest:+ELLIPSIS
    ...     dump('unmocked_instance.instance_method')
    ...     dump('unmocked_instance.instance_method()')
    unmocked_instance.instance_method == <Mock name='mock.instance_method' id='...>
    unmocked_instance.instance_method() == <mock.Mock object at 0x...>

Finally, module-level functions can be isolated:

    >>> with isolate(mod, 'unmocked_function'):  #doctest:+ELLIPSIS
    ...     dump('unmocked_function')
    ...     dump('unmocked_function()')
    unmocked_function == <function unmocked_function at 0x...>
    unmocked_function() == 'return value of unmocked_function'

Other functions are replaced with mock objects:

    >>> with isolate(mod, 'unmocked_function'):  #doctest:+ELLIPSIS
    ...     dump('my_function')
    ...     dump('my_function()')
    my_function == <mock.Mock object at 0x...>
    my_function() == <mock.Mock object at 0x...>

The distribution contains tests and documentation. The tests require
`unittest2 <http://pypi.python.org/pypi/unittest2>`_ to run.
