import warnings

from funcversion import version

warnings.filterwarnings('always')


class MyClass:
    @version('1.0.0')
    def my_method(self):
        print('Version 1.0.0')

    @version('1.1.0')
    def my_method(self):
        print('Version 1.1.0')

    @version('2.0.0')
    def my_method(self):
        print('Version 2.0.0')


obj = MyClass()
print(obj.my_method.available_versions)  # Should print ['1.0.0', '1.1.0', '2.0.0']
print(obj.my_method.current_version)  # Should print '2.0.0'
print(obj.my_method.callables)  # Should print a dict mapping versions to the corresponding callable

obj.my_method()  # Should print "Version 2.0.0" (latest version)
obj.my_method(_version='1.0.0')  # Should print "Version 1.0.0"
obj.my_method(_version='1.1.0')  # Should print "Version 1.1.0"

# Deprecate a version
obj.my_method.deprecate_version('1.0.0')
obj.my_method(_version='1.0.0')
