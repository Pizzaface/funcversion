from funcversion import version


@version('1.0')
def greet(name):
    return f'Hello, {name}!'


@version('2.0')
def greet(name):
    return f'Good day, {name}!'


@version('3.0')
def greet(name):
    return f'Hi, {name}!'


# Usage
print(greet.current_version)  # Should print "3.0"
print(greet.available_versions)  # Should print ['1.0', '2.0', '3.0']
print(greet.callables)  # Should print ['greet']
print(greet('Alice'))  # Should print "Hi, Alice!" (latest version)

# Specify a version
print(greet('Alice', _version='1.0'))  # Should print "Hello, Alice!"
print(greet('Alice', _version='2.0'))  # Should print "Good day, Alice!"
print(greet('Alice', _version='3.0'))  # Should print "Hi, Alice!"
