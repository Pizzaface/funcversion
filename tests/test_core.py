from functools import wraps

import pytest
import warnings
from funcversion.core import VersionNotFoundError, VersionedFunction
from funcversion import version


def test_global_function_versions():
    @version("1.0.0")
    def greet():
        return "Hello, version 1.0.0!"

    @version("2.0.0")
    def greet():
        return "Hello, version 2.0.0!"

    assert greet() == "Hello, version 2.0.0!"
    assert greet(version="1.0.0") == "Hello, version 1.0.0!"
    assert greet(version="2.0.0") == "Hello, version 2.0.0!"


def test_instance_method_versions():
    class Greeter:
        @version("1.0.0")
        def greet(self):
            return "Hello from instance, version 1.0.0!"

        @version("2.0.0")
        def greet(self):
            return "Hello from instance, version 2.0.0!"

    greeter = Greeter()
    assert greeter.greet() == "Hello from instance, version 2.0.0!"
    assert greeter.greet(version="1.0.0") == "Hello from instance, version 1.0.0!"


def test_class_method_binding():
    class MyClass:
        @classmethod
        @version("1.0.0")
        def method(cls):
            return cls.__name__ + " version 1.0.0"

        @classmethod
        @version("2.0.0")
        def method(cls):
            return cls.__name__ + " version 2.0.0"

    assert MyClass.method() == "MyClass version 2.0.0"
    assert MyClass.method(version="1.0.0") == "MyClass version 1.0.0"


def test_class_method_versions():
    class Greeter:
        @classmethod
        @version("1.0.0")
        def greet(cls):
            return f"Hello from {cls.__name__}, version 1.0.0!"

        @classmethod
        @version("2.0.0")
        def greet(cls):
            return f"Hello from {cls.__name__}, version 2.0.0!"

    assert Greeter.greet() == "Hello from Greeter, version 2.0.0!"
    assert Greeter.greet(version="1.0.0") == "Hello from Greeter, version 1.0.0!"


def test_static_method_versions():
    class Greeter:
        @version("1.0.0")
        @staticmethod
        def greet():
            return "Hello from static method, version 1.0.0!"

        @version("2.0.0")
        @staticmethod
        def greet():
            return "Hello from static method, version 2.0.0!"

    assert Greeter.greet() == "Hello from static method, version 2.0.0!"
    assert Greeter.greet(version="1.0.0") == "Hello from static method, version 1.0.0!"


def test_deprecation_warning():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.deprecate_version("1.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = func(version="1.0.0")
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "is deprecated" in str(w[0].message)
        assert result == "Version 1.0.0"


def test_version_not_found_error():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    with pytest.raises(VersionNotFoundError):
        func(version="2.0.0")


def test_remove_version():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.remove_version("2.0.0")

    assert func() == "Version 1.0.0"
    with pytest.raises(VersionNotFoundError):
        func(version="2.0.0")


def test_available_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    expected_versions = ["1.0.0", "1.1.0", "2.0.0"]
    assert func.available_versions == expected_versions


def test_no_versions_registered():
    func = VersionedFunction("nonexistent_function")

    with pytest.raises(ValueError):
        func()


def test_invalid_version_identifier():
    with pytest.raises(ValueError):

        @version("invalid_version")
        def func():
            pass


def test_multiple_classes_same_method_name():
    class ClassA:
        @version("1.0.0")
        def method(self):
            return "ClassA method version 1.0.0"

    class ClassB:
        @version("1.0.0")
        def method(self):
            return "ClassB method version 1.0.0"

    a = ClassA()
    b = ClassB()

    assert a.method() == "ClassA method version 1.0.0"
    assert b.method() == "ClassB method version 1.0.0"


def test_function_with_arguments():
    @version("1.0.0")
    def add(a, b):
        return a + b

    @version("2.0.0")
    def add(a, b):
        return a - b

    assert add(3, 2) == 1  # Latest version subtracts
    assert add(3, 2, version="1.0.0") == 5  # Version 1.0.0 adds


def test_method_with_arguments():
    class Calculator:
        @version("1.0.0")
        def compute(self, a, b):
            return a + b

        @version("2.0.0")
        def compute(self, a, b):
            return a * b

    calc = Calculator()
    assert calc.compute(3, 2) == 6  # Latest version multiplies
    assert calc.compute(3, 2, version="1.0.0") == 5  # Version 1.0.0 adds


def test_version_ordering():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.0.1")
    def func():
        return "Version 1.0.1"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    expected_versions = ["1.0.0", "1.0.1", "1.1.0", "2.0.0"]
    assert func.available_versions == expected_versions
    assert func() == "Version 2.0.0"


def test_method_on_inherited_class():
    class BaseClass:
        @version("1.0.0")
        def method(self):
            return "BaseClass version 1.0.0"

    class SubClass(BaseClass):
        @version("2.0.0")
        def method(self):
            return "SubClass version 2.0.0"

    base = BaseClass()
    sub = SubClass()

    assert base.method() == "BaseClass version 1.0.0"
    assert sub.method() == "SubClass version 2.0.0"
    assert sub.method(version="1.0.0") == "BaseClass version 1.0.0"


def test_method_deprecation():
    class MyClass:
        @version("1.0.0")
        def method(self):
            return "Version 1.0.0"

        @version("2.0.0")
        def method(self):
            return "Version 2.0.0"

    obj = MyClass()
    obj.method.deprecate_version("1.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = obj.method(version="1.0.0")
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "is deprecated" in str(w[0].message)
        assert result == "Version 1.0.0"


def test_duplicate_version_registration():
    with pytest.raises(ValueError):

        @version("1.0.0")
        def func():
            pass

        @version("1.0.0")
        def func():
            pass


def test_invalid_semantic_version():
    with pytest.raises(ValueError):

        @version("invalid_version")  # This is an invalid version string
        def func():
            pass


def test_module_level_functions():
    @version("1.0.0")
    def module_func():
        return "Module function version 1.0.0"

    @version("2.0.0")
    def module_func():
        return "Module function version 2.0.0"

    assert module_func() == "Module function version 2.0.0"
    assert module_func(version="1.0.0") == "Module function version 1.0.0"


def test_nested_functions():
    def outer():
        @version("1.0.0")
        def inner():
            return "Inner function version 1.0.0"

        @version("2.0.0")
        def inner():
            return "Inner function version 2.0.0"

        return inner

    inner_func = outer()
    assert inner_func() == "Inner function version 2.0.0"
    assert inner_func(version="1.0.0") == "Inner function version 1.0.0"


def test_function_attributes():
    @version("1.0.0")
    def func():
        """Docstring for version 1.0.0"""
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        """Docstring for version 2.0.0"""
        return "Version 2.0.0"

    assert func.versions["1.0.0"].__doc__ == "Docstring for version 1.0.0"
    assert func.versions["2.0.0"].__doc__ == "Docstring for version 2.0.0"


def test_calling_function_with_no_arguments():
    @version("1.0.0")
    def func():
        return "No args"

    with pytest.raises(TypeError):
        func("unexpected_arg")


def test_function_with_kwargs():
    @version("1.0.0")
    def func(a, b=2):
        return a + b

    assert func(3) == 5
    assert func(3, b=4) == 7


def test_versioned_function_is_callable():
    @version("1.0.0")
    def func():
        return "Callable"

    assert callable(func)


def test_access_versions_directly():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    assert "1.0.0" in func.versions
    assert func.versions["1.0.0"]() == "Version 1.0.0"


def test_multiple_functions_same_name_different_modules():
    import sys

    module_name = "test_module_a"
    module_a = type(sys)(module_name)
    sys.modules[module_name] = module_a

    # Define func in main module
    def func():
        return "Function in main module"

    func.__module__ = __name__
    func = version("1.0.0")(func)

    # Assign func to module_a
    setattr(sys.modules[__name__], "func", func)

    # Define func in module_a
    def func():
        return "Function in test_module_a"

    func.__module__ = module_name
    func = version("1.0.0")(func)

    setattr(module_a, "func", func)

    # Test
    assert sys.modules[__name__].func() == "Function in main module"
    assert module_a.func() == "Function in test_module_a"

    del sys.modules[module_name]


def test_remove_all_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.remove_version("1.0.0")
    func.remove_version("2.0.0")

    with pytest.raises(ValueError) as exc_info:
        func()
    assert "No versions registered for function" in str(exc_info.value)

    with pytest.raises(VersionNotFoundError):
        func(version="1.0.0")


def test_deprecate_all_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.deprecate_version("1.0.0")
    func.deprecate_version("2.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert func(version="1.0.0") == "Version 1.0.0"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "is deprecated" in str(w[0].message)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert func(version="2.0.0") == "Version 2.0.0"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "is deprecated" in str(w[0].message)


def test_add_version_after_initial_definitions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    assert func() == "Version 1.0.0"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    assert func() == "Version 1.1.0"
    assert func(version="1.0.0") == "Version 1.0.0"
    assert func(version="1.1.0") == "Version 1.1.0"


def test_semantic_versioning_with_prerelease():
    @version("1.0.0-alpha")
    def func():
        return "Version 1.0.0-alpha"

    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.1.0-beta")
    def func():
        return "Version 1.1.0-beta"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    @version("2.0.0+build.1")
    def func():
        return "Version 2.0.0+build.1"

    assert func() == "Version 2.0.0+build.1"
    assert func(version="1.0.0-alpha") == "Version 1.0.0-alpha"
    assert func(version="1.0.0") == "Version 1.0.0"
    assert func(version="1.1.0-beta") == "Version 1.1.0-beta"
    assert func(version="1.1.0") == "Version 1.1.0"
    assert func(version="2.0.0+build.1") == "Version 2.0.0+build.1"


def test_invalid_version_identifier_types():
    with pytest.raises(ValueError):

        @version(1.0)  # Non-string version identifier
        def func():
            pass

    with pytest.raises(ValueError):

        @version(None)  # Non-string version identifier
        def func():
            pass

    with pytest.raises(ValueError):

        @version(["1.0.0"])  # Non-string version identifier
        def func():
            pass


def test_versions_dict_property():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    assert isinstance(func.versions_dict, dict)
    assert "1.0.0" in func.versions_dict
    assert "2.0.0" in func.versions_dict
    assert func.versions_dict["1.0.0"]() == "Version 1.0.0"
    assert func.versions_dict["2.0.0"]() == "Version 2.0.0"


def test_list_callables_method():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    callables = func.callables
    assert isinstance(callables, dict)
    assert "1.0.0" in callables
    assert "2.0.0" in callables
    assert callables["1.0.0"]() == "Version 1.0.0"
    assert callables["2.0.0"]() == "Version 2.0.0"


def test_deprecate_version_multiple_times():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    func.deprecate_version("1.0.0")
    # Deprecating again should not raise an error but should maintain the deprecated state
    func.deprecate_version("1.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert func(version="1.0.0") == "Version 1.0.0"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)


def test_remove_version_multiple_times():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    func.remove_version("1.0.0")

    with pytest.raises(VersionNotFoundError):
        func.remove_version("1.0.0")


def test_versions_after_removal():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.remove_version("2.0.0")
    assert func() == "Version 1.0.0"

    with pytest.raises(VersionNotFoundError):
        func(version="2.0.0")


def test_versions_after_deprecation():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.deprecate_version("1.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert func(version="1.0.0") == "Version 1.0.0"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    # Ensure that the latest version is still callable without warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert func() == "Version 2.0.0"
        assert len(w) == 0


def test_inheritance_with_multiple_levels():
    class Base:
        @version("1.0.0")
        def method(self):
            return "Base version 1.0.0"

    class Intermediate(Base):
        @version("1.1.0")
        def method(self):
            return "Intermediate version 1.1.0"

    class Derived(Intermediate):
        @version("2.0.0")
        def method(self):
            return "Derived version 2.0.0"

    derived = Derived()
    assert derived.method() == "Derived version 2.0.0"
    assert derived.method(version="1.1.0") == "Intermediate version 1.1.0"
    assert derived.method(version="1.0.0") == "Base version 1.0.0"

    # List available versions
    expected_versions = ["1.0.0", "1.1.0", "2.0.0"]
    assert derived.method.available_versions == expected_versions


def test_latest_version_with_complex_semantic_versions():
    @version("1.0.0-alpha")
    def func():
        return "Version 1.0.0-alpha"

    @version("1.0.0-beta")
    def func():
        return "Version 1.0.0-beta"

    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.0.1")
    def func():
        return "Version 1.0.1"

    @version("1.1.0-rc.1")
    def func():
        return "Version 1.1.0-rc.1"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    @version("2.0.0+build.123")
    def func():
        return "Version 2.0.0+build.123"

    assert func() == "Version 2.0.0+build.123"
    assert func(version="1.0.0-alpha") == "Version 1.0.0-alpha"
    assert func(version="1.0.0-beta") == "Version 1.0.0-beta"
    assert func(version="1.0.0") == "Version 1.0.0"
    assert func(version="1.0.1") == "Version 1.0.1"
    assert func(version="1.1.0-rc.1") == "Version 1.1.0-rc.1"
    assert func(version="1.1.0") == "Version 1.1.0"
    assert func(version="2.0.0+build.123") == "Version 2.0.0+build.123"


def test_access_versions_via_versions_property():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    assert "1.0.0" in func.versions
    assert "2.0.0" in func.versions
    assert func.versions["1.0.0"]() == "Version 1.0.0"
    assert func.versions["2.0.0"]() == "Version 2.0.0"


def test_versioned_function_callable_with_args_kwargs():
    @version("1.0.0")
    def func(a, b=10, *args, **kwargs):
        return a + b + sum(args) + sum(kwargs.values())

    @version("2.0.0")
    def func(a, b=20, *args, **kwargs):
        return a * b * sum(args) * sum(kwargs.values())

    # Test latest version
    assert func(1, 2, 3, x=4, y=5) == 1 * 2 * (3) * (4 + 5)  # 1*2*3*9=54

    # Test specific version
    assert func(1, 2, 3, x=4, y=5, version="1.0.0") == 1 + 2 + 3 + 4 + 5  # 15

    # Test defaults
    assert func(1) == 1 * 20 * 0 * 0  # 0
    assert func(1, version="1.0.0") == 1 + 10  # 11


def test_versions_after_multiple_operations():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    assert func() == "Version 1.1.0"
    func.deprecate_version("1.0.0")
    assert func(version="1.1.0") == "Version 1.1.0"
    assert func(version="1.0.0") == "Version 1.0.0"

    func.remove_version("1.1.0")
    assert func() == "Version 1.0.0"

    with pytest.raises(VersionNotFoundError):
        func(version="1.1.0")

    func.remove_version("1.0.0")
    with pytest.raises(ValueError):
        func()


def test_versions_with_same_major_minor_different_patch():
    @version("1.0.1")
    def func():
        return "Version 1.0.1"

    @version("1.0.2")
    def func():
        return "Version 1.0.2"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    expected_versions = ["1.0.1", "1.0.2", "1.1.0", "2.0.0"]
    assert func.available_versions == expected_versions
    assert func() == "Version 2.0.0"
    assert func(version="1.0.1") == "Version 1.0.1"
    assert func(version="1.0.2") == "Version 1.0.2"
    assert func(version="1.1.0") == "Version 1.1.0"


def test_versioned_function_repr():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    assert repr(func) == f"<VersionedFunction {func.name} versions: {func.available_versions}>"


def test_versions_after_adding_invalid_version():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    with pytest.raises(ValueError):

        @version("invalid")
        def func():
            return "Invalid version"

    # Ensure that the invalid version was not added
    expected_versions = ["1.0.0"]
    assert func.available_versions == expected_versions


def test_access_versions_via_versions_dict_property():
    @version("1.0.0")
    def func():
        """Docstring for version 1.0.0"""
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        """Docstring for version 2.0.0"""
        return "Version 2.0.0"

    versions_dict = func.versions_dict
    assert isinstance(versions_dict, dict)
    assert "1.0.0" in versions_dict
    assert "2.0.0" in versions_dict
    assert versions_dict["1.0.0"].__doc__ == "Docstring for version 1.0.0"
    assert versions_dict["2.0.0"].__doc__ == "Docstring for version 2.0.0"
    assert versions_dict["1.0.0"]() == "Version 1.0.0"
    assert versions_dict["2.0.0"]() == "Version 2.0.0"


def test_versioned_function_is_callable_with_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    assert callable(func)
    assert callable(func.versions_dict["1.0.0"])
    assert callable(func.versions_dict["2.0.0"])
    assert func() == "Version 2.0.0"
    assert func(version="1.0.0") == "Version 1.0.0"


def test_versioned_function_with_no_versions():
    func = VersionedFunction("nonexistent_function")

    with pytest.raises(ValueError):
        func()

    with pytest.raises(VersionNotFoundError):
        func(version="1.0.0")


def test_inherited_method_deprecation():
    class Base:
        @version("1.0.0")
        def method(self):
            return "Base version 1.0.0"

    class Derived(Base):
        @version("2.0.0")
        def method(self):
            return "Derived version 2.0.0"

    derived = Derived()
    derived.method.deprecate_version("1.0.0")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert derived.method(version="1.0.0") == "Base version 1.0.0"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "is deprecated" in str(w[0].message)


def test_versioned_function_with_various_call_signatures():
    @version("1.0.0")
    def func(a, b, c=3):
        return a + b + c

    @version("2.0.0")
    def func(a, b, c=3):
        return a * b * c

    assert func(1, 2) == 6  # 1 * 2 * 3
    assert func(1, 2, 4) == 8  # 1 * 2 * 4
    assert func(1, 2, c=5) == 10  # 1 * 2 * 5
    assert func(1, 2, 4, version="1.0.0") == 7  # 1 + 2 + 4


def test_multiple_decorators_with_version():
    def uppercase(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs).upper()

        return wrapper

    @version("1.0.0")
    @uppercase
    def func():
        return "version 1.0.0"

    @version("2.0.0")
    @uppercase
    def func():
        return "version 2.0.0"

    assert func() == "VERSION 2.0.0"
    assert func(version="1.0.0") == "VERSION 1.0.0"
    assert func(version="2.0.0") == "VERSION 2.0.0"


def test_thread_safety_of_version_registry():
    import threading

    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    def register_version():
        try:
            # Register '1.1.0' version using add_version method
            func.add_version("1.1.0", lambda: "Version 1.1.0")
        except ValueError:
            pass  # Expected if duplicate

    threads = [threading.Thread(target=register_version) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Only one version '1.1.0' should be registered
    assert func.available_versions == ["1.0.0", "1.1.0"]
    assert func() == "Version 1.1.0"


def test_versioned_function_with_partial_arguments():
    @version("1.0.0")
    def func(a, b, c=3):
        return a + b + c

    @version("1.1.0")
    def func(a, b, c=4):
        return a + b + c

    assert func(1, 2) == 7  # 1 + 2 + 4
    assert func(1, 2, version="1.0.0") == 6  # 1 + 2 + 3
    assert func(1, 2, c=5) == 8  # 1 + 2 + 5
    assert func(1, 2, c=5, version="1.0.0") == 8  # 1 + 2 + 5


def test_access_deprecated_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.deprecate_version("1.0.0")

    deprecated = func.deprecated_versions
    assert deprecated == ["1.0.0"]

    # Deprecate the latest version
    func.deprecate_version("2.0.0")
    deprecated = func.deprecated_versions
    assert deprecated == ["1.0.0", "2.0.0"]


def test_available_versions_after_adding_new_versions():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("1.1.0")
    def func():
        return "Version 1.1.0"

    expected_versions = ["1.0.0", "1.1.0"]
    assert func.available_versions == expected_versions

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    expected_versions = ["1.0.0", "1.1.0", "2.0.0"]
    assert func.available_versions == expected_versions


def test_list_callables_after_removal():
    @version("1.0.0")
    def func():
        return "Version 1.0.0"

    @version("2.0.0")
    def func():
        return "Version 2.0.0"

    func.remove_version("1.0.0")

    callables = func.callables
    assert "1.0.0" not in callables
    assert "2.0.0" in callables
    assert callables["2.0.0"]() == "Version 2.0.0"
