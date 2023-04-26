This site contains the project documentation for the
`calculator` project that is a toy module used in the
Real Python tutorial
[Build Your Python Project Documentation With MkDocs](
    https://realpython.com/python-project-documentation-with-mkdocs/).
Its aim is to give you a framework to build your
project documentation using Python, MkDocs,
mkdocstrings, and the Material for MkDocs theme.

## Table Of Contents

The documentation follows the best practice for
project documentation as described by Daniele Procida
in the [Diátaxis documentation framework](https://diataxis.fr/)
and consists of four separate parts:

1. [How-To Guides](how-to-guides.md)
2. [API Reference](reference.md)
3. [Explanation](explanation.md)

Quickly find what you're looking for depending on
your use case by looking at the different pages.

## Project Overview


### Install

```shell
pipenv install printipy
```

### Example

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

## Acknowledgements

I want to thank my house plants for providing me with
a negligible amount of oxygen each day. Also, I want
to thank the sun for providing more than half of their
nourishment free of charge.