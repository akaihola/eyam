# mock_isolation.py
# Test tools for isolation with mocks.
# Copyright (C) 2010 Antti Kaihola
# E-mail: akaihol PLUS python AT ambitone DOT com

# mock_isolation 0.1
# http://github.com/akaihola/mock_isolation

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Comments, suggestions and bug reports welcome.


from inspect import getmodule, ismethod, isclass
from mock import _importer, class_types, DEFAULT, Mock, wraps
from types import MethodType


__all__ = 'isolate',


__version__ = '0.1'


class create_mock_class(Mock):
    def __call__(self, *args, **kw):
        instance = super(create_mock_class, self).__call__(*args, **kw)
        for key, value in self.__dict__.iteritems():
            if ismethod(value):
                if value.im_self:  # bound class method
                    setattr(instance, key, value)
                else:  # unbound instance method
                    setattr(instance, key,
                            MethodType(value.im_func, instance, create_mock_class))
        instance.__init__(*args, **kw)
        return instance


def _mock_module(module):
    old_module_dict = module.__dict__.copy()
    module_keys = set(module.__dict__.iterkeys())

    dunders = set(k for k in module_keys
                  if k.startswith('__') and k.endswith('__'))
    replaced_keys = module_keys - dunders
    for key in replaced_keys:
        old_value = old_module_dict[key]
        if isclass(old_value):
            module.__dict__[key] = create_mock_class()
        else:
            module.__dict__[key] = Mock()
    module.__dict__['__mocked_module_dict__'] = old_module_dict


def _copy_original_object(module, obj_path):
    components = obj_path.split('.')
    source = eval(obj_path, module.__dict__['__mocked_module_dict__'])
    target = module
    for index, comp in enumerate(components[:-1]):
        target = getattr(target, comp)
    if ismethod(source) and source.im_self is not None:
        #setattr(target, components[-1], lambda *args, **kw: (
        #    source.im_func(target, *args, **kw)))
        setattr(target, components[-1], MethodType(source.im_func, target, target))
        #setattr(target, components[-1], source)
    elif ismethod(source) and source.im_self is None:
        setattr(target, components[-1], source)
    else:
        setattr(target, components[-1], source)


def _restore_module(module):
    old_module_dict = module.__dict__['__mocked_module_dict__']
    module.__dict__.clear()
    module.__dict__.update(old_module_dict)


class _isolate_module(object):

    def __init__(self, module, exclude=None):
        self.module = module
        self.exclude = exclude or []

    def copy(self):
        return _isolate_module(self.module, self.exclude)

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
        _mock_module(self.module)
        for obj in self.exclude:
            _copy_original_object(self.module, obj)
        return self.module

    def __exit__(self, *_):
        _restore_module(self.module)


def isolate(module, *exclude):
    if isinstance(module, basestring):
        module = _importer(module)
    return _isolate_module(module, exclude)
