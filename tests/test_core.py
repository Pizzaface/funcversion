import asyncio
import warnings

import pytest
from pytest_assert_utils import util

from funcversion import VersionedFunction, VersionNotFoundError, version
from funcversion.exceptions import (InvalidVersionError, NoVersionsFoundError,
                                    VersionExistsError)


def test_global_function_versions():
    @version('1.0.0')
    def greet():
        return 'Hello, version 1.0.0!'

    @version('2.0.0')
    def greet():
        return 'Hello, version 2.0.0!'

    assert greet() == 'Hello, version 2.0.0!'
    assert greet(_version='1.0.0') == 'Hello, version 1.0.0!'
    assert greet(_version='2.0.0') == 'Hello, version 2.0.0!'


def test_instance_method_versions():
    class Greeter:
        @version('1.0.0')
        def greet(self):
            return 'Hello from instance, version 1.0.0!'

        @version('2.0.0')
        def greet(self):
            return 'Hello from instance, version 2.0.0!'

    greeter = Greeter()
    assert greeter.greet() == 'Hello from instance, version 2.0.0!'
    assert greeter.greet(_version='1.0.0') == 'Hello from instance, version 1.0.0!'


def test_class_method_binding():
    class MyClass:
        @classmethod
        @version('1.0.0')
        def method(cls):
            return cls.__name__ + ' version 1.0.0'

        @classmethod
        @version('2.0.0')
        def method(cls):
            return cls.__name__ + ' version 2.0.0'

    assert MyClass.method() == 'MyClass version 2.0.0'
    assert MyClass.method(_version='1.0.0') == 'MyClass version 1.0.0'


def test_class_method_versions():
    class Greeter:
        @classmethod
        @version('1.0.0')
        def greet(cls):
            return f'Hello from {cls.__name__}, version 1.0.0!'

        @classmethod
        @version('2.0.0')
        def greet(cls):
            return f'Hello from {cls.__name__}, version 2.0.0!'

    assert Greeter.greet() == 'Hello from Greeter, version 2.0.0!'
    assert Greeter.greet(_version='1.0.0') == 'Hello from Greeter, version 1.0.0!'


def test_static_method_versions():
    class Greeter:
        @version('1.0.0')
        @staticmethod
        def greet():
            return 'Hello from static method, version 1.0.0!'

        @version('2.0.0')
        @staticmethod
        def greet():
            return 'Hello from static method, version 2.0.0!'

    assert Greeter.greet() == 'Hello from static method, version 2.0.0!'
    assert Greeter.greet(_version='1.0.0') == 'Hello from static method, version 1.0.0!'


def test_deprecation_warning():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    func.deprecate_version('1.0.0')

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        result = func(_version='1.0.0')
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert 'is deprecated' in str(w[0].message)
        assert result == 'Version 1.0.0'
        assert func.deprecated_versions == ['1.0.0']


def test_version_not_found_error():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    with pytest.raises(VersionNotFoundError):
        func(_version='2.0.0')


def test_remove_version():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    func.remove_version('2.0.0')

    assert func() == 'Version 1.0.0'
    with pytest.raises(VersionNotFoundError):
        func(_version='2.0.0')


def test_available_versions():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('1.1.0')
    def func():
        return 'Version 1.1.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    expected_versions = ['1.0.0', '1.1.0', '2.0.0']
    assert func.available_versions == expected_versions


def test_no_versions_registered():
    func = VersionedFunction('nonexistent_function')

    with pytest.raises(NoVersionsFoundError):
        func()

def test_remove_invalid_version():
    func = VersionedFunction('invalid_version')
    with pytest.raises(VersionNotFoundError):
        func.remove_version('1.0.0')


def test_deprecate_invalid_version():
    func = VersionedFunction('invalid_version')
    with pytest.raises(VersionNotFoundError):
        func.deprecate_version('1.0.0')

def test_callables():
    funcs = {}
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    funcs['1.0.0'] = func

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    funcs['2.0.0'] = func

    assert util.Dict.containing('1.0.0', '2.0.0') == func.callables

def test_repr():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    assert repr(func) == util.Str.containing('1.0.0', '2.0.0')


def test_invalid_version_identifier():
    with pytest.raises(InvalidVersionError):

        @version('invalid_version')
        def func():
            pass

def test_invalid_version_identifier_via_add_version():
    func = VersionedFunction('1.0.0')
    with pytest.raises(InvalidVersionError):
        func.add_version('invalid_version', lambda: None)

def test_duplicate_version_registration_via_add_version():
    func = VersionedFunction('1.0.0')
    func.add_version('1.0.0', lambda: None)
    with pytest.raises(VersionExistsError):
        func.add_version('1.0.0', lambda: None)

def test_grab_function_self():
    class MyClass:
        @version('1.0.0')
        def method(self):
            return self

    obj = MyClass()
    assert obj is obj.method()

def test_multiple_classes_same_method_name():
    class ClassA:
        @version('1.0.0')
        def method(self):
            return 'ClassA method version 1.0.0'

    class ClassB:
        @version('1.0.0')
        def method(self):
            return 'ClassB method version 1.0.0'

    a = ClassA()
    b = ClassB()

    assert a.method() == 'ClassA method version 1.0.0'
    assert b.method() == 'ClassB method version 1.0.0'


def test_function_with_arguments():
    @version('1.0.0')
    def add(a, b):
        return a + b

    @version('2.0.0')
    def add(a, b):
        return a - b

    assert add(3, 2) == 1  # Latest version subtracts
    assert add(3, 2, _version='1.0.0') == 5  # Version 1.0.0 adds


def test_method_with_arguments():
    class Calculator:
        @version('1.0.0')
        def compute(self, a, b):
            return a + b

        @version('2.0.0')
        def compute(self, a, b):
            return a * b

    calc = Calculator()
    assert calc.compute(3, 2) == 6  # Latest version multiplies
    assert calc.compute(3, 2, _version='1.0.0') == 5  # Version 1.0.0 adds


def test_version_ordering():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('1.0.1')
    def func():
        return 'Version 1.0.1'

    @version('1.1.0')
    def func():
        return 'Version 1.1.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    expected_versions = ['1.0.0', '1.0.1', '1.1.0', '2.0.0']
    assert func.available_versions == expected_versions
    assert func() == 'Version 2.0.0'


def test_method_on_inherited_class():
    class BaseClass:
        @version('1.0.0')
        def method(self):
            return 'BaseClass version 1.0.0'

    class SubClass(BaseClass):
        @version('2.0.0')
        def method(self):
            return 'SubClass version 2.0.0'

    base = BaseClass()
    sub = SubClass()

    assert base.method() == 'BaseClass version 1.0.0'
    assert sub.method() == 'SubClass version 2.0.0'
    assert sub.method(_version='1.0.0') == 'BaseClass version 1.0.0'


def test_multiple_inheritance_levels():
    class GrandBase:
        @version('1.0.0')
        def method(self):
            return 'GrandBase version 1.0.0'

    class BaseClass(GrandBase):
        @version('1.0.0')
        def method(self):
            return 'BaseClass version 1.0.0'

    class SubClass(BaseClass):
        @version('1.0.0')
        def method(self):
            return 'SubClass version 1.0.0'

    grand_base = GrandBase()
    base = BaseClass()
    sub = SubClass()

    assert grand_base.method() == 'GrandBase version 1.0.0'
    assert base.method() == 'BaseClass version 1.0.0'
    assert sub.method() == 'SubClass version 1.0.0'

def test_method_on_inherited_class_overriding():
    class BaseClass:
        @version('1.0.0')
        def method(self):
            return 'BaseClass version 1.0.0'

    class SubClass(BaseClass):
        @version('1.0.0')
        def method(self):
            return 'SubClass version 1.0.0'

    base = BaseClass()
    sub = SubClass()
    assert base.method() == 'BaseClass version 1.0.0'
    assert sub.method() == 'SubClass version 1.0.0'

def test_method_deprecation():
    class MyClass:
        @version('1.0.0')
        def method(self):
            return 'Version 1.0.0'

        @version('2.0.0')
        def method(self):
            return 'Version 2.0.0'

    obj = MyClass()
    obj.method.deprecate_version('1.0.0')

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        result = obj.method(_version='1.0.0')
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert 'is deprecated' in str(w[0].message)
        assert result == 'Version 1.0.0'


def test_duplicate_version_registration():
    with pytest.raises(VersionExistsError):

        @version('1.0.0')
        def func():
            pass

        @version('1.0.0')
        def func():
            pass


def test_invalid_semantic_version():
    with pytest.raises(InvalidVersionError):

        @version('invalid_version')  # This is an invalid version string
        def func():
            pass


def test_module_level_functions():
    @version('1.0.0')
    def module_func():
        return 'Module function version 1.0.0'

    @version('2.0.0')
    def module_func():
        return 'Module function version 2.0.0'

    assert module_func() == 'Module function version 2.0.0'
    assert module_func(_version='1.0.0') == 'Module function version 1.0.0'


def test_nested_functions():
    def outer():
        @version('1.0.0')
        def inner():
            return 'Inner function version 1.0.0'

        @version('2.0.0')
        def inner():
            return 'Inner function version 2.0.0'

        return inner

    inner_func = outer()
    assert inner_func() == 'Inner function version 2.0.0'
    assert inner_func(_version='1.0.0') == 'Inner function version 1.0.0'


def test_function_attributes():
    @version('1.0.0')
    def func():
        """Docstring for version 1.0.0"""
        return 'Version 1.0.0'

    @version('2.0.0')
    def func():
        """Docstring for version 2.0.0"""
        return 'Version 2.0.0'

    assert func.versions['1.0.0'].__doc__ == 'Docstring for version 1.0.0'
    assert func.versions['2.0.0'].__doc__ == 'Docstring for version 2.0.0'


def test_calling_function_with_no_arguments():
    @version('1.0.0')
    def func():
        return 'No args'

    with pytest.raises(TypeError):
        func('unexpected_arg')


def test_function_with_kwargs():
    @version('1.0.0')
    def func(a, b=2):
        return a + b

    assert func(3) == 5
    assert func(3, b=4) == 7


def test_versioned_function_is_callable():
    @version('1.0.0')
    def func():
        return 'Callable'

    assert callable(func)


def test_access_versions_directly():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    assert '1.0.0' in func.versions
    assert func.versions['1.0.0']() == 'Version 1.0.0'


def test_multiple_functions_same_name_different_modules():
    import sys

    module_name = 'test_module_a'
    module_a = type(sys)(module_name)
    sys.modules[module_name] = module_a

    # Define func in main module
    def func():
        return 'Function in main module'

    func.__module__ = __name__
    func = version('1.0.0')(func)

    # Assign func to module_a
    setattr(sys.modules[__name__], 'func', func)

    # Define func in module_a
    def func():
        return 'Function in test_module_a'

    func.__module__ = module_name
    func = version('1.0.0')(func)

    setattr(module_a, 'func', func)

    # Test
    assert sys.modules[__name__].func() == 'Function in main module'
    assert module_a.func() == 'Function in test_module_a'

    del sys.modules[module_name]

def test_add_version_to_existing_function():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    func.add_version('2.0.0', lambda: 'Version 2.0.0')

    assert func() == 'Version 2.0.0'
    assert func(_version='1.0.0') == 'Version 1.0.0'

def test_remove_version_from_existing_function():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    func.remove_version('1.0.0')

    with pytest.raises(NoVersionsFoundError):
        func()

def test_get_current_version():
    @version('1.0.0')
    def func():
        return 'Version 1.0.0'

    @version('2.0.0')
    def func():
        return 'Version 2.0.0'

    assert func.current_version == '2.0.0'

def test_get_current_version_no_versions():
    func = VersionedFunction('no_versions')
    with pytest.raises(NoVersionsFoundError):
        func.current_version

@pytest.mark.asyncio
def test_async_functions():
    import asyncio

    @version('1.0.0')
    async def async_func():
        await asyncio.sleep(1)
        return 'Async version 1.0.0'

    @version('2.0.0')
    async def async_func():
        await asyncio.sleep(1)
        return 'Async version 2.0.0'

    async def main():
        assert await async_func() == 'Async version 2.0.0'
        assert await async_func(_version='1.0.0') == 'Async version 1.0.0'

    asyncio.run(main())


def test_async_method():
    class MyClass:
        @version('1.0.0')
        async def async_method(self):
            await asyncio.sleep(1)
            return 'Async method version 1.0.0'

        @version('2.0.0')
        async def async_method(self):
            await asyncio.sleep(1)
            return 'Async method version 2.0.0'

    obj = MyClass()

    async def main():
        assert await obj.async_method() == 'Async method version 2.0.0'
        assert await obj.async_method(_version='1.0.0') == 'Async method version 1.0.0'

    asyncio.run(main())


@pytest.mark.asyncio
def test_async_class_method():
    class MyClass:
        @classmethod
        @version('1.0.0')
        async def async_method(cls):
            await asyncio.sleep(1)
            return 'Async class method version 1.0.0'

        @classmethod
        @version('2.0.0')
        async def async_method(cls):
            await asyncio.sleep(1)
            return 'Async class method version 2.0.0'

    async def main():
        assert await MyClass.async_method() == 'Async class method version 2.0.0'
        assert await MyClass.async_method(_version='1.0.0') == 'Async class method version 1.0.0'

    asyncio.run(main())


@pytest.mark.asyncio
def test_async_static_method():
    class MyClass:
        @staticmethod
        @version('1.0.0')
        async def async_method():
            await asyncio.sleep(1)
            return 'Async static method version 1.0.0'

        @staticmethod
        @version('2.0.0')
        async def async_method():
            await asyncio.sleep(1)
            return 'Async static method version 2.0.0'

    async def main():
        assert await MyClass.async_method() == 'Async static method version 2.0.0'
        assert await MyClass.async_method(_version='1.0.0') == 'Async static method version 1.0.0'

    asyncio.run(main())
