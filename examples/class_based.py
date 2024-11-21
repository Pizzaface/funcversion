from funcversion import version


class MyClass:
    @version('1.0.0')
    def my_method(self):
        print("Version 1.0.0")

    @version('1.1.0')
    def my_method(self):
        print("Version 1.1.0")

    @version('2.0.0')
    def my_method(self):
        print("Version 2.0.0")

obj = MyClass()
obj.my_method()  # Should print "Version 2.0.0" (latest version)
obj.my_method(version='1.0.0')  # Should print "Version 1.0.0"
obj.my_method(version='1.1.0')  # Should print "Version 1.1.0"

