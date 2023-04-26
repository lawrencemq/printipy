# PrintiPy
The Printify API for Python

Tested with Python 3.8 - 3.11.


## Quickstart

Quickly connect to the Printify API via PrintiPy. Pass an API token for the Printify account and an optional Shop ID and start automating!

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...', shop_id='...')

for product in api.products.get_products():
    print(product)
```

## API

Table of Contents:
1. [Getting Started](#getting-started)
1. [Shop](#Shop)
   1. [get shops](#get shops)
   1. [delete shop](#delete shop)
1. [Catalog](#Catalog)
   1. [get_blueprints](#get_blueprints)
   1. [get_blueprint](#get_blueprint)
   1. [get_print_providers_for_blueprint](#get_print_providers_for_blueprint)
   1. [get_variants](#get_variants)
   1. [get_shipping_info](#get_shipping_info)
   1. [get_print_providers](#get_print_providers)
   1. [get_print_provider](#get_print_provider)
1. [Products](#Products)
   1. [get_products](#get_products)
   1. [get_product](#get_product)
   1. [create_product](#create_product)
   1. [update_product](#update_product)
   1. [delete_product](#delete_product)
   1. [publish_product](#publish_product)
   1. [set_product_published_success](#set_product_published_success)
   1. [set_product_published_failed](#set_product_published_failed)
   1. [unpublish_product](#unpublish_product)
1. [Orders](#Orders)
   1. [get_orders](#get_orders)
   1. [get_order](#get_order)
   1. [create order](#create order)
   1. [create_order_for_existing_product](#create_order_for_existing_product)
   1. [create_order_with_simple_image_positioning](#create_order_with_simple_image_positioning)
   1. [create_order_with_advanced_image_positioning](#create_order_with_advanced_image_positioning)
   1. [create_order_with_print_details](#create_order_with_print_details)
   1. [create_order_with_sku](#create_order_with_sku)
   1. [send_order_to_production](#send_order_to_production)
   1. [calc_shipping_for_order](#calc_shipping_for_order)
   1. [cancel_order](#cancel_order)
1. [Artwork](#Artwork)
   1. [get_artwork_uploads](#get_artwork_uploads)
   1. [get_artwork](#get_artwork)
   1. [upload_artwork](#upload_artwork)
   1. [archive_artwork](#archive_artwork)
1. [Webhooks](#Webhooks)
   1. [get_webhooks](#get_webhooks)
   1. [create_webhook](#create_webhook)
   1. [update_webhook](#update_webhook)
   1. [delete_webhook](#delete_webhook)

### Getting Started

Every instance of PrintiPy requires an API Token. Follow [these steps](https://help.printify.com/hc/en-us/articles/4483626447249-How-can-I-generate-an-API-token-) to generate your token.


Create an instance of Printipy:

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...')
```

Printify accounts can have multiple shops; each shop has its own ID.

`shop_id` may also be passed in. If present, the ID will be used for all PrintiPy function calls automatically unless overridden in the PrintiPy function calls (see examples below). Otherwise, it will be required on specific PrintyPy function calls as needed.

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...', shop_id='shop_1_ABC123')
```

### Shop

#### get_shops

Returns instances of 

```python
from printipy.api import PrintiPy

api = PrintiPy(api_token='...')

api.shops.get_shops()
```

#### delete_shop

### Catalog

#### get_blueprints

#### get_blueprint

#### get_print_providers_for_blueprint

#### get_variants

#### get_shipping_info

#### get_print_providers

#### get_print_provider


### Products

#### get_products

#### get_product

#### create_product

#### update_product

#### delete_product

#### publish_product

#### set_product_published_success

#### set_product_published_failed

#### unpublish_product


### Orders

#### get_orders

#### get_order

#### create order

##### create_order_for_existing_product

##### create_order_with_simple_image_positioning

##### create_order_with_advanced_image_positioning

##### create_order_with_print_details

##### create_order_with_sku

#### send_order_to_production

#### calc_shipping_for_order

#### cancel_order


### Artwork

#### get_artwork_uploads

#### get_artwork

#### upload_artwork

#### archive_artwork


### Webhooks

#### get_webhooks

#### create_webhook

#### update_webhook

#### delete_webhook




## create product

Example:
Even though the data below has more information than the API needs, the extraneous data will be filtered out automatically and the call will be sucessfully made.
```python
from printipy import PrintiPy, CreateProduct
new_product_data = {
        "title": "Testy McTestFace",
        "description": "suc test. wow!",
        "tags": [
            "Home & Living",
            "Paper",
            "Sustainable",
            "Greeting Card",
            "Postcard",
            "Card",
            "Post cards",
            "Postcards",
            "Made in USA"
        ],
        "blueprint_id": 1094,
        "print_provider_id": 228,
        "variants": [
            {
                "id": 81870,
                "price": 999,
                "is_enabled": True,
            },
            {
                "id": 81871,
                "price": 2499,
                "is_enabled": True,
            },
            {
                "id": 81872,
                "price": 4399,
                "is_enabled": True,
            },
            {
                "id": 81873,
                "price": 5599,
                "is_enabled": True,
            },
        ],
        "print_areas": [
            {
                "variant_ids": [
                    81810,
                    81811,
                    81812,
                    81813,
                    81822,
                    81823,
                    81824,
                    81825,
                    81814,
                    81815,
                    81816,
                    81817,
                    81818,
                    81819,
                    81820,
                    81821,
                    81874,
                    81875,
                    81876,
                    81877,
                    81886,
                    81887,
                    81888,
                    81889,
                    81878,
                    81879,
                    81880,
                    81881,
                    81882,
                    81883,
                    81884,
                    81885,
                    81890,
                    81891,
                    81892,
                    81893,
                    81902,
                    81903,
                    81904,
                    81905,
                    81894,
                    81895,
                    81896,
                    81897,
                    81898,
                    81899,
                    81900,
                    81901,
                    81906,
                    81907,
                    81908,
                    81909,
                    81918,
                    81919,
                    81920,
                    81921,
                    81910,
                    81911,
                    81912,
                    81913,
                    81914,
                    81915,
                    81916,
                    81917,
                    81962,
                    81963,
                    81964,
                    81965,
                    81974,
                    81975,
                    81976,
                    81977,
                    81966,
                    81967,
                    81968,
                    81969,
                    81970,
                    81971,
                    81972,
                    81973,
                    81826,
                    81827,
                    81828,
                    81829,
                    81838,
                    81839,
                    81840,
                    81841,
                    81830,
                    81831,
                    81832,
                    81833,
                    81834,
                    81835,
                    81836,
                    81837,
                    81842,
                    81843,
                    81844,
                    81845,
                    81854,
                    81855,
                    81856,
                    81857,
                    81846,
                    81847,
                    81848,
                    81849,
                    81850,
                    81851,
                    81852,
                    81853,
                    81858,
                    81859,
                    81860,
                    81861,
                    81870,
                    81871,
                    81872,
                    81873,
                    81862,
                    81863,
                    81864,
                    81865,
                    81866,
                    81867,
                    81868,
                    81869
                ],
                "placeholders": [
                    {
                        "position": "inside",
                        "images": [
                            {
                                "id": "63e7f5fbf08c3242e6859f58",
                                "name": "bday_0030_back.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.7440094762474443,
                                "y": 0.4906514988405507,
                                "scale": 0.49589968099975856,
                                "angle": 0
                            },
                            {
                                "id": "63e7f5fbf08c3242e6859f58",
                                "name": "bday_0030_back.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.24780487804878043,
                                "y": 0.4903646422579296,
                                "scale": 0.49560975609756086,
                                "angle": 0
                            }
                        ]
                    },
                    {
                        "position": "cover",
                        "images": [
                            {
                                "id": "63e7f5bb3ff59340bd57938f",
                                "name": "bday_0030_front.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.7390939252654081,
                                "y": 0.49405654771100854,
                                "scale": 0.48716923114741456,
                                "angle": 0
                            }
                        ]
                    }
                ],
            }
        ]
    }
    new_product = CreateProduct.from_dict(new_product_data)
    api = PrintiPy(api_token='...', shop_id='...')
    print(api.products.create_product(7370017, new_product))
```


## Development

TODO

### Build
TODO

### Tests

`pipenv run pytest`

### Releasing
Specific contributors are allowed to create a tag. Upon a tag's push, Actions will deploy to TestPypi and Pypi
