PrintiPy: The Printify API for Python

This site contains the project documentation for the
`PrintiPy` project.

Its aim is to give you easy, Pythonic, programmatic access to Printify's API.

If you would like to contribute, please see the [GitHub page](https://github.com/lawrencemq/printipy).

## Table Of Contents

1. [API Reference](reference.md)
2. [Explanation](explanation.md)

## Project Overview

### Install

```shell
pipenv install printipy
```

### Quickstart Example

Quickly connect to the Printify API via PrintiPy. Pass an API token for the Printify account and an optional Shop ID and start automating!

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...', shop_id='...')

for product in api.products.get_products():
    print(product)
```

### References

- [Printipy API Documentation](./reference.md)
- [Printipy Data Object Documentation](./data-objects.md)
- [Printipy Exception Documentation](./exceptions.md)
