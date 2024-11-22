# funcversion

### "When Version Control just **isn't** enough!"

`funcversion` is a Python library that enables you to manage multiple versions of functions seamlessly using decorators. It simplifies maintaining backward compatibility and managing feature rollouts by allowing multiple implementations of the same function under different version identifiers.

## Features

- **Versioning via Decorators**: Easily register multiple versions of a function using the `@version` decorator.
- **Invoke Specific Versions**: Call a specific version of a function when needed.
- **Default to Latest Version**: If no version is specified, the latest registered version is executed based on semantic versioning.
- **List Available Versions**: Retrieve all available versions of a function.
- **Deprecate Versions**: Mark specific versions as deprecated to discourage their use.
- **Remove Versions**: Remove specific versions of a function when they are no longer needed.
- **Support for Class and Static Methods**: Seamlessly version class methods and static methods.

## Installation

`python setup.py install`

## Quick Start

### Basic Function Versioning

```python
from funcversion import version

@version('1.0.0')
def greet(name):
    return f'Hello, {name}!'

@version('2.0.0')
def greet(name):
    return f'Hi, {name}!'

# Call the latest version (2.0.0)
print(greet('Alice'))  # Output: Hi, Alice!

# Call a specific version (1.0.0)
print(greet('Bob', version='1.0.0'))  # Output: Hello, Bob!

# List available versions
print(greet.available_versions)  # Output: ['1.0.0', '2.0.0']
```

### Deprecating a Version

```python
# Deprecate version 1.0.0
greet.deprecate_version('1.0.0')

# Calling a deprecated version will issue a warning
print(greet('Charlie', version='1.0.0'))  
# Output: Hello, Charlie!
# Warning: DeprecationWarning: Version '1.0.0' of function 'your_module.greet' is deprecated.
```

### Removing a Version

```python
# Remove version 1.0.0
greet.remove_version('1.0.0')

# Attempting to call the removed version will raise an error
print(greet('Dana', version='1.0.0'))  
# Raises VersionNotFoundError
```

## Advanced Usage

### Versioning Class Methods

```python
from funcversion import version

class Calculator:
    
    @version('1.0.0')
    @classmethod
    def add(cls, a, b):
        return a + b

    @version('2.0.0')
    @classmethod
    def add(cls, a, b):
        print("Adding numbers:")
        return a + b

# Call the latest version (2.0.0)
print(Calculator.add(5, 7))  
# Output:
# Adding numbers:
# 12

# Call a specific version (1.0.0)
print(Calculator.add(5, 7, version='1.0.0'))  # Output: 12
```

### Versioning Static Methods

```python
from funcversion import version

class Formatter:
    
    @version('1.0.0')
    @staticmethod
    def format_text(text):
        return text.lower()

    @version('2.0.0')
    @staticmethod
    def format_text(text):
        return text.upper()

# Call the latest version (2.0.0)
print(Formatter.format_text('Hello World'))  # Output: HELLO WORLD

# Call a specific version (1.0.0)
print(Formatter.format_text('Hello World', version='1.0.0'))  # Output: hello world
```

## API Reference

### `@version(version_id: str)`

Decorator to register a specific version of a function.

**Parameters:**

- `version_id` (str): The semantic version identifier (e.g., `"1.0.0"`).

**Usage:**

Apply the decorator to multiple implementations of the same function with different version identifiers.

### `VersionedFunction` Class

A callable wrapper that manages different versions of a function.

#### Methods:

- `__call__(*args, version=None, **kwargs)`: Executes the specified version of the function. If no version is specified, the latest version is called.
- `add_version(version_id: str, func: Callable)`: Adds a new version to the function.
- `current_version -> str`: Returns the version identifier of the currently executed function.
- `available_versions -> List[str]`: Returns a sorted list of available version identifiers.
- `deprecated_versions -> List[str]`: Returns a list of deprecated version identifiers.
- `callables -> Dict[str, Callable]`: Returns a dictionary mapping version identifiers to their respective callables.
- `deprecate_version(version_id: str)`: Marks a specific version as deprecated.
- `remove_version(version_id: str)`: Removes a specific version from the registry.

## Best Practices

- **Semantic Versioning**: Use semantic versioning (e.g., `1.0.0`, `2.1.3`) to clearly communicate changes.
- **Deprecate Before Removal**: Mark versions as deprecated before removing them to give users time to transition.
- **Consistent Function Signatures**: Ensure that different versions of a function have compatible signatures to avoid breaking changes.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/pizzaface/funcversion).

## License

This project is licensed under the [MIT License](LICENSE).
