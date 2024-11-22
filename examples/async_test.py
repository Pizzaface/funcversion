import warnings

from funcversion import version
import asyncio

warnings.filterwarnings('always')


class Calculator:
    @version('1.0.0')
    def add(self, x, y):
        """Synchronous add version 1.0.0"""
        return x + y

    @version('2.0.0')
    def add(self, x, y):
        """Synchronous add version 2.0.0 with logging"""
        print(f'Adding {x} and {y}')
        return x + y

    @version('1.0.0')
    async def async_add(self, x, y):
        """Asynchronous add version 1.0.0"""
        await asyncio.sleep(1)
        return x + y

    @version('2.0.0')
    async def async_add(self, x, y):
        """Asynchronous add version 2.0.0 with logging"""
        print(f'Adding asynchronously {x} and {y}')
        await asyncio.sleep(1)
        return x + y


# Usage
async def main():
    calc = Calculator()

    # Synchronous add - latest version (2.0.0)
    result_sync = calc.add(3, 4)
    print(f'Synchronous add (latest): {result_sync}')  # Outputs: Adding 3 and 4 \n 7

    # Synchronous add - specific version (1.0.0)
    result_sync_v1 = calc.add(3, 4, version='1.0.0')
    print(f'Synchronous add (v1.0.0): {result_sync_v1}')  # Outputs: 7

    # Asynchronous add - latest version (2.0.0)
    result_async = await calc.async_add(5, 6)
    print(f'Asynchronous add (latest): {result_async}')  # Outputs: Adding asynchronously 5 and 6 \n 11

    # Asynchronous add - specific version (1.0.0)
    result_async_v1 = await calc.async_add(5, 6, version='1.0.0')
    print(f'Asynchronous add (v1.0.0): {result_async_v1}')  # Outputs: 11

    # Deprecate a version
    calc.async_add.deprecate_version('1.0.0')
    result_sync_v1_deprecated = await calc.async_add(3, 4, version='1.0.0')
    print(f'Asynchronous add (v1.0.0 - deprecated): {result_sync_v1_deprecated}')  # Outputs: 7


# Run the example
asyncio.run(main())
