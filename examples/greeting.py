from funcversion import version, VersionedFunction

@version("1.0")
def greet(name):
    return f"Hello, {name}!"

@version("2.0")
def greet(name):
    return f"Good day, {name}!"

@version("3.0")
def greet(name):
    return f"Hi, {name}!"


print(greet("Alice"))  # Should print "Hi, Alice!" (latest version)
print(greet("Alice", version="1.0"))  # Should print "Hello, Alice!"
print(greet("Alice", version="2.0"))  # Should print "Good day, Alice!"
print(greet("Alice", version="3.0"))  # Should print "Hi, Alice!"
print(greet.available_versions())  # Should print ['1.0', '2.0', '3.0']