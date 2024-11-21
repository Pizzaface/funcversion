# funcversion

`funcversion` is a Python library that allows you to manage multiple versions of functions using decorators. It enables seamless versioning of function implementations, making it easier to maintain backward compatibility and manage feature rollouts.

## Features

- **Versioning via Decorators**: Easily register multiple versions of a function using the `@version` decorator.
- **Invoke Specific Versions**: Call a specific version of a function when needed.
- **Default to Latest Version**: If no version is specified, the latest registered version is executed.
- **List Available Versions**: Retrieve all available versions of a function.
- **Remove Versions**: Remove specific versions of a function when they are no longer needed.
- **Version Aliases**: Assign aliases to versions for easier reference.

## Usage
```python
from funcversion import version

@version('1.0.0')
def greet(name):
    return f'Hello, {name}!'

@version('2.0.0')
def greet(name):
    return f'Hi, {name}!'

# Call the latest version
print(greet('Alice'))  # Output: Hi, Alice!

# Call a specific version
print(greet('Bob', version='1.0.0'))  # Output: Hello, Bob!

# List available versions
print(greet.available_versions())  # Output: ['1.0.0', '2.0.0']
```

