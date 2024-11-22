import warnings

from funcversion import version
import asyncio

warnings.filterwarnings("always")

class BaseCalculator:
    @version("1.0.0")
    def add(self, x: int, y: int) -> int:
        """Add two numbers - BaseCalculator v1.0.0"""
        return x + y

    @version("2.0.0")
    def add(self, x: int, y: int) -> int:
        """Add two numbers with logging - BaseCalculator v2.0.0"""
        print(f"Adding {x} and {y}")
        return x + y

    @version("1.0.0")
    async def async_add(self, x: int, y: int) -> int:
        """Asynchronously add two numbers - BaseCalculator v1.0.0"""
        await asyncio.sleep(1)
        return x + y

    @version("2.0.0")
    async def async_add(self, x: int, y: int) -> int:
        """Asynchronously add two numbers with logging - BaseCalculator v2.0.0"""
        print(f"Asynchronously adding {x} and {y}")
        await asyncio.sleep(1)
        return x + y

class AdvancedCalculator(BaseCalculator):
    @version("1.0.0")
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers - AdvancedCalculator v1.0.0"""
        return x * y

    @version("2.0.0")
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers with logging - AdvancedCalculator v2.0.0"""
        print(f"Multiplying {x} and {y}")
        return x * y

    # Overriding Base Class Method

    @version("1.0.0")
    def add(self, x: int, y: int) -> int:
        """Add two numbers differently - AdvancedCalculator v1.0.0"""
        return (x + y) * 2  # Example of different implementation

    @version("2.0.0")
    def add(self, x: int, y: int) -> int:
        """Add two numbers with advanced logging - AdvancedCalculator v2.0.0"""
        print(f"Advanced adding {x} and {y}")
        return (x + y) * 2


if __name__ == "__main__":
    calc = AdvancedCalculator()

    # Synchronous add - latest version (2.0.0)
    result_sync = calc.add(3, 4)
    print(f"Synchronous add (latest): {result_sync}")  # Outputs: Advanced adding 3 and 4 \n 14

    # Asynchronous add - latest version (2.0.0)
    result_async = asyncio.run(calc.async_add(5, 6))
    print(f"Asynchronous add (latest): {result_async}")  # Outputs: Asynchronously adding 5 and 6 \n 22

    # Multiply - latest version (2.0.0)
    result_multiply = calc.multiply(3, 4)
    print(f"Multiply (latest): {result_multiply}")  # Outputs: Multiplying 3 and 4 \n 12

    # Synchronous add - specific version (1.0.0)
    result_sync_v1 = calc.add(3, 4, _version="1.0.0")
    print(f"Synchronous add (v1.0.0): {result_sync_v1}")  # Outputs: 14

    # Asynchronous add - specific version (1.0.0)
    result_async_v1 = asyncio.run(calc.async_add(5, 6, _version="1.0.0"))
    print(f"Asynchronous add (v1.0.0): {result_async_v1}")  # Outputs: 11

    # Multiply - specific version (1.0.0)
    result_multiply_v1 = calc.multiply(3, 4, _version="1.0.0")
    print(f"Multiply (v1.0.0): {result_multiply_v1}")  # Outputs: 12

    # Deprecate a version
    calc.async_add.deprecate_version("1.0.0")
    result_sync_v1_deprecated = asyncio.run(calc.async_add(3, 4, _version="1.0.0"))
    print(f"Asynchronous add (v1.0.0 - deprecated): {result_sync_v1_deprecated}")  # Outputs: 7
