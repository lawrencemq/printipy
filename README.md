# PrintiPy
The Printify API for Python

Printify's REST API gives your scripts or applications power to manage Printify shops. Create and update products, submit orders, build custom integrations, and so much more!

Tested with Python 3.9 - 3.11.

## Install

```shell
pipenv install printipy
```

## Example

Quickly connect to the Printify API via PrintiPy. Pass an API token for the Printify account and an optional Shop ID and start automating!

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...', shop_id='...')

for product in api.products.get_products():
    print(product)
```

## API

Read the docs [here](https://lawrencemq.github.io/printipy/)!

## Development

`pipenv install`

### Build

`python setup.py sdist bdist_wheel`

### Tests

`pipenv run pytest`

### Documentation

Build docs using `pipenv run mkdocs build`

Deploy docs using `mkdocs gh-deploy`. This pushes the generated `/site` to `gh-pages` branch on Github. 

### Releasing
Specific contributors are allowed to create a tag. Upon a tag's push, Actions will deploy to TestPypi and Pypi
