# eyam.py
# Test tools for isolation with mocks.
# Copyright (C) 2010 Antti Kaihola
# E-mail: akaihol PLUS python AT ambitone DOT com

# eyam 0.1
# http://github.com/akaihola/eyam

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Comments, suggestions and bug reports welcome.


from inspect import getmodule, ismethod, isclass
from mock import _importer, DEFAULT, Mock, wraps
try:
    from mock import class_types  # mock <0.8
except:
    from mock import ClassTypes as class_types  # mock >=0.8
from types import MethodType


__all__ = 'isolate',


def _clone_class(cls, exclude):
    clone_attrs = {}
    local_exclude = set(ex[0] for ex in exclude if ex)
    local_exclude.add('__module__')
    for key, value in cls.__dict__.iteritems():
        if key == '__dict__':
            continue
        elif key in local_exclude:
            clone_attrs[key] = value
        else:
            clone_attrs[key] = Mock()
            if key == '__init__':
                clone_attrs[key].return_value = None
    clone = type(cls.__name__, cls.__bases__, clone_attrs)
    return clone


def _copy_attribute(source_obj, path, target):
    source = eval('obj.%s' % '.'.join(path), {'obj': source_obj})
    for comp in path[:-1]:
        target = getattr(target, comp)
    if ismethod(source) and source.im_self is not None:
        setattr(target, path[-1], MethodType(source.im_func, target, target))
    elif ismethod(source) and source.im_self is None:
        setattr(target, path[-1], source)
    else:
        setattr(target, path[-1], source)


def _clone_object(old_obj, exclude):
    obj = Mock()
    for attpath in exclude:
        _copy_attribute(old_obj, attpath, obj)
    return obj


def _clone(obj, exclude):
    if isclass(obj) and exclude:
        # If anything inside the class is to be excluded, clone the class and
        # mock its attributes and methods.  Otherwise just replace the whole
        # class with a mock object.
        return _clone_class(obj, exclude)
    return _clone_object(obj, exclude)


def _mock_module(module, exclude):
    old_module_dict = module.__dict__.copy()
    module_keys = set(module.__dict__.iterkeys())

    dunders = set(k for k in module_keys
                  if k.startswith('__') and k.endswith('__'))
    excl = set(x[0] for x in exclude if x and len(x) == 1)
    replaced_keys = module_keys - dunders - excl
    for key in replaced_keys:
        old_value = old_module_dict[key]
        local_exclude = set(x[1:] for x in exclude
                            if x and x[0] == key and len(x) > 1)
        module.__dict__[key] = _clone(old_value, local_exclude)
    module.__dict__['__mocked_module_dict__'] = old_module_dict


def _restore_module(module):
    old_module_dict = module.__dict__['__mocked_module_dict__']
    module.__dict__.clear()
    module.__dict__.update(old_module_dict)


class _isolate_module(object):

    def __init__(self, module, *exclude):
        self.module = module
        self.exclude = exclude

    def copy(self):
        return _isolate_module(self.module, *self.exclude)

    def __call__(self, func):
        if isinstance(func, class_types):
            return self.decorate_class(func)
        else:
            return self.decorate_callable(func)

    def decorate_class(self, klass):
        for attr in dir(klass):
            attr_value = getattr(klass, attr)
            if attr.startswith("test") and hasattr(attr_value, "__call__"):
                setattr(klass, attr, self.copy()(attr_value))
        return klass

    def decorate_callable(self, func):
        if hasattr(func, 'patchings'):
            func.patchings.append(self)
            return func

        @wraps(func)
        def patched(*args, **keywargs):
            # don't use a with here (backwards compatability with 2.5)
            for patching in patched.patchings:
                patching.__enter__()
            try:
                return func(*args, **keywargs)
            finally:
                for patching in reversed(getattr(patched, 'patchings', [])):
                    patching.__exit__()

        patched.patchings = [self]
        if hasattr(func, 'func_code'):
            # not in Python 3
            patched.compat_co_firstlineno = getattr(
                func, "compat_co_firstlineno", func.func_code.co_firstlineno)
        return patched

    def __enter__(self):
        _mock_module(self.module, self.exclude)
        return self.module

    def __exit__(self, *_):
        _restore_module(self.module)


def isolate(module, *exclude):
    if isinstance(module, basestring):
        module = _importer(module)
    exclude_tuples = set(tuple(x.split('.')) for x in exclude)
    return _isolate_module(module, *exclude_tuples)
