import os
from typing import Union, Optional, Dict, List
from unittest import TestCase

import responses
from responses import matchers

from printipy.api import PrintiPy, Shop, Blueprint, PrintProvider, PrintProviderVariants, ShippingInfo, Product, \
    UpdateProduct, CreateProduct, Publish, PublishingSucceeded, Order, CreateOrderExistingProduct, \
    CreateShippingEstimate, \
    ShippingCost, Artwork, PrintiPyException, Webhook, CreateWebhook, UpdateWebhook, CreateOrderPrintDetails, \
    CreateOrderAdvancedImageProcessing, CreateOrderSimpleImageProcessing, CreateOrderSku


class TestPrintiPyApiV1(TestCase):
    test_api_token = 'test_1234567890'
    api = PrintiPy(api_token=test_api_token)
    default_headers = {'Authorization': f'Bearer {test_api_token}'}

    def __prepare_response(self, http_type: Union[responses.GET, responses.POST, responses.DELETE, responses.PUT],
                           url: str, data: Optional[Union[Dict, List]] = None):
        if data is None:
            data = {}
        headers = self.default_headers
        if http_type in {'post', 'put'}:
            headers = headers.update({'content-type': 'application/json'})
        responses.add(
            http_type,
            match=[matchers.header_matcher(headers)],
            url=url,
            json=data,
        )

    @responses.activate
    def test_get_shops(self):
        data_returned_from_url = [
            {
                "id": 5432,
                "title": "My new store",
                "sales_channel": "My Sales Channel"
            },
            {
                "id": 9876,
                "title": "My other new store",
                "sales_channel": "disconnected"
            }
        ]

        self.__prepare_response(
            responses.GET,
            url='https://api.printify.com/v1/shops.json',
            data=data_returned_from_url
        )

        shops = self.api.get_shops()
        self.assertEqual(len(shops), 2)
        self.assertEqual(shops, [Shop.from_dict(x) for x in data_returned_from_url])
        for shop in shops:
            self.assertIsNotNone(shop.id)
            self.assertIsNotNone(shop.title)
            self.assertIsNotNone(shop.sales_channel)

    @responses.activate
    def test_delete_shop(self):
        shop = Shop.from_dict(
            {
                "id": 5432,
                "title": "My new store",
                "sales_channel": "My Sales Channel"
            },
        )

        self.__prepare_response(
            responses.DELETE,
            url='https://api.printify.com/v1/shops/5432/connection.json',
            data={}
        )

        resp = self.api.delete_shop(shop)
        self.assertIsNone(resp)

    @responses.activate
    def test_get_blueprints(self):
        data_returned_from_url = [
            {
                "id": 3,
                "title": "Kids Regular Fit Tee",
                "description": "Description goes here",
                "brand": "Delta",
                "model": "11736",
                "images": [
                    "https://images.printify.com/5853fe7dce46f30f8327f5cd",
                    "https://images.printify.com/5c487ee2a342bc9b8b2fc4d2"
                ]
            },
            {
                "id": 5,
                "title": "Men's Cotton Crew Tee",
                "description": "Description goes here",
                "brand": "Next Level",
                "model": "3600",
                "images": [
                    "https://images.printify.com/5a2ffc81b8e7e3656268fb44",
                    "https://images.printify.com/5cdc0126b97b6a00091b58f7"
                ]
            },
            {
                "id": 6,
                "title": "Unisex Heavy Cotton Tee",
                "description": "Description goes here",
                "brand": "Gildan",
                "model": "5000",
                "images": [
                    "https://images.printify.com/5a2fd7d9b8e7e36658795dc0",
                    "https://images.printify.com/5c595436a342bc1670049902",
                    "https://images.printify.com/5c595427a342bc166b6d3002",
                    "https://images.printify.com/5a2fd022b8e7e3666c70623a"
                ]
            },
            {
                "id": 9,
                "title": "Women's Favorite Tee",
                "description": "Description goes here",
                "brand": "Bella+Canvas",
                "model": "6004",
                "images": [
                    "https://images.printify.com/5a2ffeeab8e7e364d660836f",
                    "https://images.printify.com/59e362cab8e7e30a5b0a55bd",
                    "https://images.printify.com/59e362d2b8e7e30b9f576691",
                    "https://images.printify.com/59e362ddb8e7e3174f3196ee",
                    "https://images.printify.com/59e362eab8e7e3593e2ac98d"
                ]
            },
            {
                "id": 10,
                "title": "Women's Flowy Racerback Tank",
                "description": "Description goes here",
                "brand": "Bella+Canvas",
                "model": "8800",
                "images": [
                    "https://images.printify.com/5a27eb68b8e7e364d6608322",
                    "https://images.printify.com/5c485236a342bc521c2a0beb",
                    "https://images.printify.com/5c485217a342bc686053da46",
                    "https://images.printify.com/5c485225a342bc52fe5fee83"
                ]
            },
            {
                "id": 11,
                "title": "Women's Jersey Short Sleeve Deep V-Neck Tee",
                "description": "Description goes here",
                "brand": "Bella+Canvas",
                "model": "6035",
                "images": [
                    "https://images.printify.com/5a27f20fb8e7e316f403a3b1",
                    "https://images.printify.com/5c472ff0a342bcad97372d72",
                    "https://images.printify.com/5c472ff8a342bcad9964d115"
                ]
            },
            {
                "id": 12,
                "title": "Unisex Jersey Short Sleeve Tee",
                "description": "Description goes here",
                "brand": "Bella+Canvas",
                "model": "3001",
                "images": [
                    "https://images.printify.com/5a2ff5b0b8e7e36669068406",
                    "https://images.printify.com/59e35414b8e7e30aa625995c",
                    "https://images.printify.com/5cd579548c3769000f274cac",
                    "https://images.printify.com/5cd579558c37690008453286",
                    "https://images.printify.com/59e3541bb8e7e30a60795f9c",
                    "https://images.printify.com/59e35428b8e7e30a1a4de812",
                    "https://images.printify.com/59e3552db8e7e3174714887a",
                    "https://images.printify.com/5a8beec5b8e7e304614eb59c"
                ]
            }
        ]

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/blueprints.json',
            data=data_returned_from_url
        )

        blueprints = self.api.get_blueprints()
        self.assertEqual(len(blueprints), 7)
        self.assertEqual(blueprints, [Blueprint.from_dict(x) for x in data_returned_from_url])
        for blueprint in blueprints:
            for key in [
                "id",
                "title",
                "description",
                "brand",
                "model",
            ]:
                self.assertIsNotNone(blueprint.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_blueprint(self):
        data_returned_from_url = {
            "id": 3,
            "title": "Kids Regular Fit Tee",
            "description": "Description goes here",
            "brand": "Delta",
            "model": "11736",
            "images": [
                "https://images.printify.com/5853fe7dce46f30f8327f5cd",
                "https://images.printify.com/5c487ee2a342bc9b8b2fc4d2"
            ]
        }

        self.__prepare_response(
            responses.GET,
            url='https://api.printify.com/v1/catalog/blueprints/3.json',
            data=data_returned_from_url
        )

        blueprint = self.api.get_blueprint(3)
        self.assertEqual(blueprint, Blueprint.from_dict(data_returned_from_url))
        for key in ["id", "title", "description", "brand", "model"]:
            self.assertIsNotNone(blueprint.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_print_providers_for_blueprint(self):
        data_returned_from_url = [
            {
                "id": 3,
                "title": "DJ"
            },
            {
                "id": 8,
                "title": "Fifth Sun"
            },
            {
                "id": 16,
                "title": "MyLocker"
            },
            {
                "id": 24,
                "title": "Inklocker",
                "location": {
                    "address1": "123 Main Street",
                    "address2": "",
                    "city": "EveryCity",
                    "country": "USA",
                    "region": "Earth",
                    "zip": "10101"
                }
            }
        ]

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/blueprints/12345/print_providers.json',
            data=data_returned_from_url
        )

        providers = self.api.get_print_providers_for_blueprint(12345)
        self.assertEqual(len(providers), 4)
        self.assertEqual(providers, [PrintProvider.from_dict(x) for x in data_returned_from_url])
        for provider in providers:
            for key in ["id", "title"]:
                self.assertIsNotNone(provider.__getattribute__(key), f'{key} should not be None')

        self.assertIsNotNone(next(filter(lambda p: p.id == 24, providers)).location)

    @responses.activate
    def test_get_variants(self):
        data_returned_from_url = {
            "id": 3,
            "title": "DJ",
            "variants": [
                {
                    "id": 17390,
                    "title": "Heather Grey / XS",
                    "options": {
                        "color": "Heather Grey",
                        "size": "XS"
                    },
                    "placeholders": [
                        {
                            "position": "back",
                            "height": 3995,
                            "width": 3153
                        },
                        {
                            "position": "front",
                            "height": 3995,
                            "width": 3153
                        }
                    ]
                },
                {
                    "id": 17426,
                    "title": "Solid Black / XS",
                    "options": {
                        "color": "Solid Black",
                        "size": "XS"
                    },
                    "placeholders": [
                        {
                            "position": "back",
                            "height": 3995,
                            "width": 3153
                        },
                        {
                            "position": "front",
                            "height": 3995,
                            "width": 3153
                        }
                    ]
                },
            ]
        }

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/blueprints/12345/print_providers/5/variants.json',
            data=data_returned_from_url
        )

        variant_info = self.api.get_variants(12345, 5)
        self.assertEqual(variant_info.id, 3)
        self.assertEqual(variant_info.title, "DJ")
        self.assertEqual(len(variant_info.variants), 2)
        self.assertEqual(variant_info, PrintProviderVariants.from_dict(data_returned_from_url))
        for variant in variant_info.variants:
            for key in ['id', 'title', 'options']:
                self.assertIsNotNone(variant.__getattribute__(key), f'{key} should not be None')

            option = variant.options
            for key in ['color', 'size']:
                self.assertIsNotNone(option.__getattribute__(key), f'{key} should not be None')

            self.assertEqual(len(variant.placeholders), 2)
            for placeholder in variant.placeholders:
                for key in ['position', 'height', 'width']:
                    self.assertIsNotNone(placeholder.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_shipping_info(self):
        data_returned_from_url = {
            "handling_time": {
                "value": 30,
                "unit": "day"
            },
            "profiles": [
                {
                    "variant_ids": [
                        42716,
                        42717,
                        42718,
                        42719,
                        42720,
                        12144,
                        12143,
                        12124,
                        12127,
                        12128
                    ],
                    "first_item": {
                        "cost": 450,
                        "currency": "USD"
                    },
                    "additional_items": {
                        "cost": 0,
                        "currency": "USD"
                    },
                    "countries": [
                        "US"
                    ]
                },
                {
                    "variant_ids": [
                        12127,
                        12128
                    ],
                    "first_item": {
                        "cost": 650,
                        "currency": "USD"
                    },
                    "additional_items": {
                        "cost": 0,
                        "currency": "USD"
                    },
                    "countries": [
                        "CA",
                        "GI",
                        "AX"
                    ]
                },
                {
                    "variant_ids": [
                        42716,
                        42717,
                        42718,
                        42719,
                        42720,
                        12126,
                        12125,
                        12124,
                        12127,
                        12128
                    ],
                    "first_item": {
                        "cost": 1100,
                        "currency": "USD"
                    },
                    "additional_items": {
                        "cost": 0,
                        "currency": "USD"
                    },
                    "countries": [
                        "REST_OF_THE_WORLD"
                    ]
                }
            ]
        }

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/blueprints/12345/print_providers/5/shipping.json',
            data=data_returned_from_url
        )

        shipping_info = self.api.get_shipping_info(12345, 5)
        self.assertEqual(len(shipping_info.profiles), 3)
        self.assertEqual(shipping_info, ShippingInfo.from_dict(data_returned_from_url))
        self.assertEqual(shipping_info.handling_time.to_dict(), {"value": 30, "unit": "day"})
        for profile in shipping_info.profiles:
            for key in ['variant_ids', 'first_item', 'additional_items', 'countries']:
                self.assertIsNotNone(profile.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_print_providers(self):
        data_returned_from_url = [
            {
                "id": 1,
                "title": "SPOKE Custom Products",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 2,
                "title": "CG Pro prints",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 3,
                "title": "The Dream Junction ",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": "",
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 5,
                "title": "ArtGun",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": "",
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 6,
                "title": "T shirt and Sons",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 7,
                "title": "Prodigi",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 8,
                "title": "Fifth Sun",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 9,
                "title": "WPaPS",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 10,
                "title": "MWW On Demand",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 14,
                "title": "ArtsAdd",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 16,
                "title": "MyLocker",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 20,
                "title": "Troupe Jewelry",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": None,
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 23,
                "title": "WOYC",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": "",
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 24,
                "title": "Inklocker",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": "",
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            },
            {
                "id": 25,
                "title": "DTG2Go",
                "location": {
                    "address1": "89 Weirfield St",
                    "address2": "",
                    "city": "Brooklyn",
                    "country": "US",
                    "region": "NY",
                    "zip": "11221-5120"
                }
            }
        ]

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/print_providers.json',
            data=data_returned_from_url
        )

        print_provider_info = self.api.get_print_providers()
        self.assertEqual(len(print_provider_info), 15)
        self.assertEqual(print_provider_info, [PrintProvider.from_dict(x) for x in data_returned_from_url])

        for provider in print_provider_info:
            for key in ['id', 'title', 'location']:
                self.assertIsNotNone(provider.__getattribute__(key), f'{key} should not be None')

            for key in ["address1", "city", "country", "region", "zip"]:
                self.assertIsNotNone(provider.location.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_print_provider(self):
        data_returned_from_url = {
            "id": 1,
            "title": "SPOKE Custom Products",
            "location": {
                "address1": "89 Weirfield St",
                "address2": None,
                "city": "Brooklyn",
                "country": "US",
                "region": "NY",
                "zip": "11221-5120"
            }
        }

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/catalog/print_providers/1.json',
            data=data_returned_from_url
        )

        print_provider_info = self.api.get_print_provider(1)
        self.assertEqual(print_provider_info, PrintProvider.from_dict(data_returned_from_url))

    @responses.activate
    def test_get_products(self):
        pass

    @responses.activate
    def test_get_product(self):
        data_returned_from_url = {
            "id": "5d39b159e7c48c000728c89f",
            "title": "Mug 11oz",
            "description": """Perfect for coffee, tea and hot chocolate, this classic shape white, durable
            ceramic mug in the most popular size.High quality sublimation printing makes it an
                appreciated gift to every True hot beverage lover.Perfect
        for coffee, tea and hot
        chocolate, this classic shape white, durable ceramic mug in the most popular size.
        High quality sublimation printing makes it an appreciated gift to every True hot beverage lover.
        .: White
        ceramic
        .: 11
        oz(0.33
        l)
        .: Rounded
        corners
        .: C - Handle
        """,
            "tags": [
                "Home & Living",
                "Mugs",
                "11 oz",
                "White base",
                "Sublimation"
            ],
            "options": [
                {
                    "name": "Sizes",
                    "type": "size",
                    "values": [
                        {
                            "id": 1189,
                            "title": "11oz"
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": 33719,
                    "sku": "866366009",
                    "cost": 516,
                    "price": 860,
                    "title": "11oz",
                    "grams": 460,
                    "is_enabled": True,
                    "is_default": True,
                    "is_available": True,
                    "options": [
                        1189
                    ]
                }
            ],
            "images": [
                {
                    "src": "https://images.printify.com/mockup/5d39b159e7c48c000728c89f/33719/145/mug-11oz.jpg",
                    "variant_ids": [
                        33719
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b159e7c48c000728c89f/33719/146/mug-11oz.jpg",
                    "variant_ids": [
                        33719
                    ],
                    "position": "other",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b159e7c48c000728c89f/33719/147/mug-11oz.jpg",
                    "variant_ids": [
                        33719
                    ],
                    "position": "other",
                    "is_default": True
                }
            ],
            "created_at": "2019-07-25 13:40:41+00:00",
            "updated_at": "2019-07-25 13:40:59+00:00",
            "visible": True,
            "is_locked": False,
            "blueprint_id": 68,
            "user_id": 1337,
            "shop_id": 1337,
            "print_provider_id": 9,
            "print_areas": [
                {
                    "variant_ids": [
                        33719
                    ],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": "5c7665205342af161e1cb26e",
                                    "name": "Test.png",
                                    "type": "image/png",
                                    "height": 5850,
                                    "width": 4350,
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1.01,
                                    "angle": 0
                                }
                            ]
                        }
                    ],
                    "background": "#ffffff"
                }
            ],
            "sales_channel_properties": []
        }
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/shops/shop_123/products/121.json',
            data=data_returned_from_url
        )

        product_info = self.api.get_product("shop_123", '121')
        self.assertEqual(product_info, Product.from_dict(data_returned_from_url))

        for key in ['id', 'title', 'description', 'created_at', 'updated_at', 'visible', 'is_locked', 'blueprint_id',
                    'user_id', 'shop_id', 'print_provider_id', 'print_areas', 'images', 'variants', 'options', 'tags']:
            self.assertIsNotNone(product_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_create_product(self):
        data_for_url = {
            "title": "Product",
            "description": "Good product",
            "blueprint_id": 384,
            "print_provider_id": 1,
            "variants": [
                {
                    "id": 45740,
                    "price": 400,
                    "is_enabled": True
                },
                {
                    "id": 45742,
                    "price": 400,
                    "is_enabled": True
                },
                {
                    "id": 45744,
                    "price": 400,
                    "is_enabled": False
                },
                {
                    "id": 45746,
                    "price": 400,
                    "is_enabled": False
                }
            ],
            "print_areas": [
                {
                    "variant_ids": [45740, 45742, 45744, 45746],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": "5d15ca551163cde90d7b2203",
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1,
                                    "angle": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        data_returned_from_url = {
            "id": "5d39b411749d0a000f30e0f4",
            "title": "Product",
            "description": "Good product",
            "tags": [
                "Home & Living",
                "Stickers"
            ],
            "options": [
                {
                    "name": "Size",
                    "type": "size",
                    "values": [
                        {
                            "id": 2017,
                            "title": "2x2\""
                        },
                        {
                            "id": 2018,
                            "title": "3x3\""
                        },
                        {
                            "id": 2019,
                            "title": "4x4\""
                        },
                        {
                            "id": 2020,
                            "title": "6x6\""
                        }
                    ]
                },
                {
                    "name": "Type",
                    "type": "surface",
                    "values": [
                        {
                            "id": 2114,
                            "title": "White"
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": 45740,
                    "sku": "866375988",
                    "cost": 134,
                    "price": 400,
                    "title": "2x2\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": True,
                    "is_available": True,
                    "options": [
                        2017,
                        2114
                    ]
                },
                {
                    "id": 45742,
                    "sku": "866375989",
                    "cost": 149,
                    "price": 400,
                    "title": "3x3\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": False,
                    "is_available": True,
                    "options": [
                        2018,
                        2114
                    ]
                },
                {
                    "id": 45744,
                    "sku": "866375990",
                    "cost": 187,
                    "price": 400,
                    "title": "4x4\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": False,
                    "is_available": True,
                    "options": [
                        2019,
                        2114
                    ]
                },
                {
                    "id": 45746,
                    "sku": "866375991",
                    "cost": 216,
                    "price": 400,
                    "title": "6x6\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": False,
                    "is_available": True,
                    "options": [
                        2020,
                        2114
                    ]
                }
            ],
            "images": [
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2187/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": True
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2188/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2189/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2190/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2191/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2192/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2193/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2194/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2195/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2196/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2197/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2198/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2199/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2200/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2201/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2202/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2187/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2188/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2189/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": True
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2190/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2191/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2192/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2193/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2194/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2195/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2196/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2197/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2198/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2199/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2200/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2201/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45742/2202/product.jpg",
                    "variant_ids": [
                        45742
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2187/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2188/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2189/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2190/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": True
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2191/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2192/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2193/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2194/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2195/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2196/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2197/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2198/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2199/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2200/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2201/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45744/2202/product.jpg",
                    "variant_ids": [
                        45744
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2187/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2188/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2189/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2190/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2191/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": True
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2192/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2193/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2194/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2195/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2196/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2197/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2198/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2199/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2200/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2201/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45746/2202/product.jpg",
                    "variant_ids": [
                        45746
                    ],
                    "position": "front",
                    "is_default": False
                }
            ],
            "created_at": "2019-07-25 13:52:17+00:00",
            "updated_at": "2019-07-25 13:52:18+00:00",
            "visible": True,
            "is_locked": False,
            "blueprint_id": 384,
            "user_id": 1337,
            "shop_id": 1337,
            "print_provider_id": 1,
            "print_areas": [
                {
                    "variant_ids": [
                        45740,
                        45742,
                        45744,
                        45746
                    ],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": "5d15ca551163cde90d7b2203",
                                    "name": "Asset 65@3x.png",
                                    "type": "image/png",
                                    "height": 1200,
                                    "width": 1200,
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1,
                                    "angle": 0
                                }
                            ]
                        }
                    ],
                    "background": "#ffffff"
                }
            ],
            "sales_channel_properties": []
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/products.json',
            data=data_returned_from_url
        )

        product_info = self.api.create_product('shop_123', CreateProduct.from_dict(data_for_url))

        self.assertEqual(product_info, Product.from_dict(data_returned_from_url))

        for key in ['id', 'title', 'description', 'created_at', 'updated_at', 'visible', 'is_locked', 'blueprint_id',
                    'user_id', 'shop_id', 'print_provider_id', 'print_areas', 'images', 'variants', 'options', 'tags']:
            self.assertIsNotNone(product_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_update_product(self):
        data_for_url = {
            "title": "Product"
        }
        data_returned_from_url = {
            "id": "5d39b411749d0a000f30e0f4",
            "title": "Product",
            "description": "Good product",
            "tags": [
                "Home & Living",
                "Stickers"
            ],
            "options": [
                {
                    "name": "Size",
                    "type": "size",
                    "values": [
                        {
                            "id": 2017,
                            "title": "2x2\""
                        },
                        {
                            "id": 2018,
                            "title": "3x3\""
                        },
                    ]
                },
                {
                    "name": "Type",
                    "type": "surface",
                    "values": [
                        {
                            "id": 2114,
                            "title": "White"
                        }
                    ]
                }
            ],
            "variants": [
                {
                    "id": 45740,
                    "sku": "866375988",
                    "cost": 134,
                    "price": 400,
                    "title": "2x2\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": True,
                    "is_available": True,
                    "options": [
                        2017,
                        2114
                    ]
                },
                {
                    "id": 45742,
                    "sku": "866375989",
                    "cost": 149,
                    "price": 400,
                    "title": "3x3\" / White",
                    "grams": 10,
                    "is_enabled": True,
                    "is_default": False,
                    "is_available": True,
                    "options": [
                        2018,
                        2114
                    ]
                },
            ],
            "images": [
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2187/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": True
                },
                {
                    "src": "https://images.printify.com/mockup/5d39b411749d0a000f30e0f4/45740/2188/product.jpg",
                    "variant_ids": [
                        45740
                    ],
                    "position": "front",
                    "is_default": False
                },
            ],
            "created_at": "2019-07-25 13:52:17+00:00",
            "updated_at": "2019-07-25 13:52:18+00:00",
            "visible": True,
            "is_locked": False,
            "blueprint_id": 384,
            "user_id": 1337,
            "shop_id": 1337,
            "print_provider_id": 1,
            "print_areas": [
                {
                    "variant_ids": [
                        45740,
                        45742,
                        45744,
                        45746
                    ],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": "5d15ca551163cde90d7b2203",
                                    "name": "Asset 65@3x.png",
                                    "type": "image/png",
                                    "height": 1200,
                                    "width": 1200,
                                    "x": 0.5,
                                    "y": 0.5,
                                    "scale": 1,
                                    "angle": 0
                                }
                            ]
                        }
                    ],
                    "background": "#ffffff"
                }
            ],
            "sales_channel_properties": []
        }
        self.__prepare_response(
            responses.PUT,
            'https://api.printify.com/v1/shops/shop_123/products/121.json',
            data=data_returned_from_url
        )

        product_info = self.api.update_product('shop_123', '121', UpdateProduct.from_dict(data_for_url))

        self.assertEqual(product_info, Product.from_dict(data_returned_from_url))

        for key in ['id', 'title', 'description', 'created_at', 'updated_at', 'visible', 'is_locked', 'blueprint_id',
                    'user_id', 'shop_id', 'print_provider_id', 'print_areas', 'images', 'variants', 'options', 'tags']:
            self.assertIsNotNone(product_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_delete_product(self):
        self.__prepare_response(
            responses.DELETE,
            url='https://api.printify.com/v1/shops/12345/products/54321.json',
        )
        self.assertTrue(self.api.delete_product('12345', '54321'))

    @responses.activate
    def test_publish_product(self):
        data_for_url = {
            "title": True,
            "description": True,
            "images": True,
            "variants": True,
            "tags": True,
            "keyFeatures": True,
            "shipping_template": True,
        }

        self.__prepare_response(
            responses.POST,
            url='https://api.printify.com/v1/shops/12345/products/54321/publish.json',
        )

        self.assertTrue(self.api.publish_product('12345', '54321', Publish.from_dict(data_for_url)))

    @responses.activate
    def test_publish_product_with_default_publish_all(self):

        self.__prepare_response(
            responses.POST,
            url='https://api.printify.com/v1/shops/12345/products/54321/publish.json',
        )

        self.assertTrue(self.api.publish_product('12345', '54321'))

    @responses.activate
    def test_set_product_published_success(self):
        data_for_url = {
            "external": {
                "id": "5941187eb8e7e37b3f0e62e5",
                "handle": "https://example.com/path/to/product"
            }
        }

        self.__prepare_response(
            responses.POST,
            url='https://api.printify.com/v1/shops/12345/products/54321/publishing_succeeded.json',
        )

        self.assertTrue(
            self.api.set_product_published_success('12345', '54321', PublishingSucceeded.from_dict(data_for_url)))

    @responses.activate
    def test_set_product_published_failed(self):
        self.__prepare_response(
            responses.POST,
            url='https://api.printify.com/v1/shops/12345/products/54321/publishing_failed.json',
        )

        self.assertTrue(self.api.set_product_published_failed('12345', '54321', "just because"))

    @responses.activate
    def test_unpublish_product(self):
        self.__prepare_response(
            responses.POST,
            url='https://api.printify.com/v1/shops/12345/products/54321/unpublish.json',
        )

        self.assertTrue(self.api.unpublish_product('12345', '54321'))

    @responses.activate
    def test_get_orders(self):
        first_data_returned_from_url = {
            "current_page": 1,
            "data": [
                {
                    "id": "5a96f649b2439217d070f507",
                    "address_to": {
                        "first_name": "John",
                        "last_name": "Smith",
                        "region": "",
                        "address1": "ExampleBaan 121",
                        "city": "Retie",
                        "zip": "2470",
                        "email": "example@msn.com",
                        "phone": "0574 69 21 90",
                        "country": "BE",
                        "company": "MSN"
                    },
                    "line_items": [
                        {
                            "product_id": "5b05842f3921c9547531758d",
                            "quantity": 1,
                            "variant_id": 17887,
                            "print_provider_id": 5,
                            "cost": 1050,
                            "shipping_cost": 400,
                            "status": "fulfilled",
                            "metadata": {
                                "title": "18K gold plated Necklace",
                                "price": 2200,
                                "variant_label": "Golden indigocoin",
                                "sku": "168699843",
                                "country": "United States"
                            },
                            "sent_to_production_at": "2017-04-18 13:24:28+00:00",
                            "fulfilled_at": "2017-04-18 13:24:28+00:00"
                        }
                    ],
                    "metadata": {
                        "order_type": "external",
                        "shop_order_id": 1370762297,
                        "shop_order_label": "1370762297",
                        "shop_fulfilled_at": "2017-04-18 13:24:28+00:00"
                    },
                    "total_price": 2200,
                    "total_shipping": 400,
                    "total_tax": 0,
                    "status": "fulfilled",
                    "shipping_method": 1,
                    "shipments": [
                        {
                            "carrier": "usps",
                            "number": "94001116990045395649372",
                            "url": "http://example.com/94001116990045395649372",
                            "delivered_at": "2017-04-18 13:24:28+00:00"
                        }
                    ],
                    "created_at": "2017-04-18 13:24:28+00:00",
                    "sent_to_production_at": "2017-04-18 13:24:28+00:00",
                    "fulfilled_at": "2017-04-18 13:24:28+00:00"
                }
            ],
            "next_page_url": "?page=2"
        }

        second_data_returned_from_url = {
            "current_page": 2,
            "data": [
                {
                    "id": "5a96f649b2439217d070f508",
                    "address_to": {
                        "first_name": "John",
                        "last_name": "Smith",
                        "region": "",
                        "address1": "ExampleBaan 121",
                        "city": "Retie",
                        "zip": "2470",
                        "email": "example@msn.com",
                        "phone": "0574 69 21 90",
                        "country": "BE",
                        "company": "MSN"
                    },
                    "line_items": [
                        {
                            "product_id": "5b05842f3921c9547531758d",
                            "quantity": 1,
                            "variant_id": 17887,
                            "print_provider_id": 5,
                            "cost": 1050,
                            "shipping_cost": 400,
                            "status": "fulfilled",
                            "metadata": {
                                "title": "18K gold plated Necklace",
                                "price": 2200,
                                "variant_label": "Golden indigocoin",
                                "sku": "168699843",
                                "country": "United States"
                            },
                            "sent_to_production_at": "2017-04-18 13:24:28+00:00",
                            "fulfilled_at": "2017-04-18 13:24:28+00:00"
                        }
                    ],
                    "metadata": {
                        "order_type": "external",
                        "shop_order_id": 1370762297,
                        "shop_order_label": "1370762297",
                        "shop_fulfilled_at": "2017-04-18 13:24:28+00:00"
                    },
                    "total_price": 2200,
                    "total_shipping": 400,
                    "total_tax": 0,
                    "status": "fulfilled",
                    "shipping_method": 1,
                    "shipments": [
                        {
                            "carrier": "usps",
                            "number": "94001116990045395649372",
                            "url": "http://example.com/94001116990045395649372",
                            "delivered_at": "2017-04-18 13:24:28+00:00"
                        }
                    ],
                    "created_at": "2017-04-18 13:24:28+00:00",
                    "sent_to_production_at": "2017-04-18 13:24:28+00:00",
                    "fulfilled_at": "2017-04-18 13:24:28+00:00",
                }
            ]
        }

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=first_data_returned_from_url
        )
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/shops/shop_123/orders.json?page=2',
            data=second_data_returned_from_url
        )

        orders_info = self.api.get_orders('shop_123', max_pages=3)

        self.assertEqual(orders_info, [Order.from_dict(first_data_returned_from_url['data'][0]),
                                       Order.from_dict(second_data_returned_from_url['data'][0])])

        for order in orders_info:
            for key in ['id', 'address_to', 'line_items', 'metadata', 'total_price', 'total_shipping', 'total_tax',
                        'status', 'shipping_method', 'created_at']:
                self.assertIsNotNone(order.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_order(self):
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507",
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "region": "",
                "address1": "ExampleBaan 121",
                "city": "Retie",
                "zip": "2470",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "company": "MSN"
            },
            "line_items": [
                {
                    "product_id": "5b05842f3921c9547531758d",
                    "quantity": 1,
                    "variant_id": 17887,
                    "print_provider_id": 5,
                    "cost": 1050,
                    "shipping_cost": 400,
                    "status": "fulfilled",
                    "metadata": {
                        "title": "18K gold plated Necklace",
                        "price": 2200,
                        "variant_label": "Golden indigocoin",
                        "sku": "168699843",
                        "country": "United States"
                    },
                    "sent_to_production_at": "2017-04-18 13:24:28+00:00",
                    "fulfilled_at": "2017-04-18 13:24:28+00:00"
                }
            ],
            "metadata": {
                "order_type": "external",
                "shop_order_id": 1370762297,
                "shop_order_label": "1370762297",
                "shop_fulfilled_at": "2017-04-18 13:24:28+00:00"
            },
            "total_price": 2200,
            "total_shipping": 400,
            "total_tax": 0,
            "status": "fulfilled",
            "shipping_method": 1,
            "shipments": [
                {
                    "carrier": "usps",
                    "number": "94001116990045395649372",
                    "url": "http://example.com/94001116990045395649372",
                    "delivered_at": "2017-04-18 13:24:28+00:00"
                }
            ],
            "created_at": "2017-04-18 13:24:28+00:00",
            "sent_to_production_at": "2017-04-18 13:24:28+00:00",
            "fulfilled_at": "2017-04-18 13:24:28+00:00"
        }
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/shops/shop_123/orders/5a96f649b2439217d070f507.json',
            data=data_returned_from_url
        )

        order_info = self.api.get_order('shop_123', "5a96f649b2439217d070f507")

        self.assertEqual(order_info, Order.from_dict(data_returned_from_url))

        for key in ['id', 'address_to', 'line_items', 'metadata', 'total_price', 'total_shipping', 'total_tax',
                    'status', 'shipping_method', 'created_at']:
            self.assertIsNotNone(order_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_create_order_for_existing_product(self):
        data_for_url = {
            "external_id": "2750e210-39bb-11e9-a503-452618153e4a",
            "label": "00012",
            "line_items": [
                {
                    "product_id": "5bfd0b66a342bcc9b5563216",
                    "variant_id": 17887,
                    "quantity": 1
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": False,
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=data_returned_from_url
        )

        order_id = self.api.create_order_for_existing_product('shop_123',
                                                              CreateOrderExistingProduct.from_dict(data_for_url))

        self.assertEqual(order_id, data_returned_from_url['id'])

    @responses.activate
    def test_create_order_with_simple_image_positioning(self):
        data_for_url = {
            "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            "label": "00012",
            "line_items": [
                {
                    "print_provider_id": 5,
                    "blueprint_id": 9,
                    "variant_id": 17887,
                    "print_areas": {
                        "front": "https://images.example.com/image.png"
                    },
                    "quantity": 1
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": False,
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=data_returned_from_url
        )

        order_id = self.api.create_order_with_simple_image_positioning('shop_123',
                                                                       CreateOrderSimpleImageProcessing.from_dict(
                                                                           data_for_url))

        self.assertEqual(order_id, data_returned_from_url['id'])

    @responses.activate
    def test_create_order_with_advanced_image_positioning(self):
        data_for_url = {
            "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            "label": "00012",
            "line_items": [
                {
                    "print_provider_id": 5,
                    "blueprint_id": 9,
                    "variant_id": 17887,
                    "print_areas": {
                        "front": [
                            {
                                "src": "https://images.example.com/image.png",
                                "scale": 0.15,
                                "x": 0.80,
                                "y": 0.34,
                                "angle": 0.34
                            },
                            {
                                "src": "https://images.example.com/image.png",
                                "scale": 1,
                                "x": 0.5,
                                "y": 0.5,
                                "angle": 1
                            }
                        ]
                    },
                    "quantity": 1
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": False,
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=data_returned_from_url
        )

        order_id = self.api.create_order_with_advanced_image_positioning('shop_123',
                                                                         CreateOrderAdvancedImageProcessing.from_dict(
                                                                             data_for_url))

        self.assertEqual(order_id, data_returned_from_url['id'])

    @responses.activate
    def test_create_order_with_print_details(self):
        data_for_url = {
            "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            "label": "00012",
            "line_items": [
                {
                    "print_provider_id": 5,
                    "blueprint_id": 9,
                    "variant_id": 17887,
                    "print_areas": {
                        "front": "https://images.example.com/image.png"
                    },
                    "print_details": {
                        "print_on_side": "mirror"
                    },
                    "quantity": 1
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": False,
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=data_returned_from_url
        )

        order_id = self.api.create_order_with_print_details('shop_123', CreateOrderPrintDetails.from_dict(data_for_url))

        self.assertEqual(order_id, data_returned_from_url['id'])

    @responses.activate
    def test_create_order_with_sku(self):
        data_for_url = {
            "external_id": "2750e210-39bb-11e9-a503-452618153e6a",
            "label": "00012",
            "line_items": [
                {
                    "sku": "MY-SKU",
                    "quantity": 1
                }
            ],
            "shipping_method": 1,
            "send_shipping_notification": False,
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "id": "5a96f649b2439217d070f507"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders.json',
            data=data_returned_from_url
        )

        order_id = self.api.create_order_with_sku('shop_123', CreateOrderSku.from_dict(data_for_url))

        self.assertEqual(order_id, data_returned_from_url['id'])

    @responses.activate
    def test_send_order_to_production(self):
        data_returned_from_url = {
            "id": "5d65c6ac01b403000a5d24d3",
            "address_to": {
                "first_name": "John  ",
                "last_name": "Doe",
                "phone": "0000000",
                "country": "United States",
                "region": "AL",
                "address1": "Happy St 1",
                "city": "Sun City",
                "zip": "00000"
            },
            "line_items": [
                {
                    "quantity": 1,
                    "product_id": "5d6549359105f6000a0c17f7",
                    "variant_id": 43424,
                    "print_provider_id": 16,
                    "shipping_cost": 400,
                    "cost": 1149,
                    "status": "on-hold",
                    "metadata": {
                        "title": "POD Water Bottle 2",
                        "price": 1915,
                        "variant_label": "14oz",
                        "sku": "901426000",
                        "country": "United States"
                    }
                }
            ],
            "metadata": {
                "order_type": "manual",
                "shop_fulfilled_at": "1970-01-01 00:00:00+00:00"
            },
            "total_price": 1149,
            "total_shipping": 400,
            "total_tax": 0,
            "status": "on-hold",
            "shipping_method": 1,
            "created_at": "2019-08-28 00:11:24+00:00"
        }
        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders/5d65c6ac01b403000a5d24d3/send_to_production.json',
            data=data_returned_from_url
        )

        order_info = self.api.send_order_to_production('shop_123', "5d65c6ac01b403000a5d24d3")

        self.assertEqual(order_info, Order.from_dict(data_returned_from_url))

        for key in ['id', 'address_to', 'line_items', 'metadata', 'total_price', 'total_shipping', 'total_tax',
                    'status', 'shipping_method', 'created_at']:
            self.assertIsNotNone(order_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_calc_shipping_for_order(self):
        data_for_url = {
            "line_items": [{
                "product_id": "5bfd0b66a342bcc9b5563216",
                "variant_id": 17887,
                "quantity": 1
            }, {
                "print_provider_id": 5,
                "blueprint_id": 9,
                "variant_id": 17887,
                "quantity": 1
            }, {
                "sku": "MY-SKU",
                "quantity": 1
            }],
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "phone": "0574 69 21 90",
                "country": "BE",
                "region": "",
                "address1": "ExampleBaan 121",
                "address2": "45",
                "city": "Retie",
                "zip": "2470"
            }
        }
        data_returned_from_url = {
            "standard": 1000,
            "express": 5000
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders/shipping.json',
            data=data_returned_from_url
        )

        shipping_info = self.api.calc_shipping_for_order('shop_123', CreateShippingEstimate.from_dict(data_for_url))

        self.assertEqual(shipping_info, ShippingCost.from_dict(data_returned_from_url))

        for key in ['standard', 'express']:
            self.assertIsNotNone(shipping_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_cancel_order(self):
        data_returned_from_url = {
            "id": "5dee261dc400914833007902",
            "address_to": {
                "first_name": "John",
                "last_name": "Smith",
                "email": "example@msn.com",
                "country": "United States",
                "region": "CA",
                "address1": "31677 Virginia Way",
                "city": "Laguna Beach",
                "zip": "92653"
            },
            "line_items": [
                {
                    "quantity": 1,
                    "product_id": "5de6593ebff03b5313567d22",
                    "variant_id": 34509,
                    "print_provider_id": 6,
                    "shipping_cost": 450,
                    "cost": 0,
                    "status": "canceled",
                    "metadata": {
                        "title": "Men's Organic Tee - Product 1",
                        "variant_label": "S / Red",
                        "sku": "3640",
                        "country": "United Kingdom"
                    }
                }
            ],
            "metadata": {
                "order_type": "api",
                "shop_order_id": "2750e210-39bb-11e9-a503-452618153e4a",
                "shop_order_label": "2750e210-39bb-11e9-a503-452618153e4a",
                "shop_fulfilled_at": "1970-01-01 00:00:00+00:00"
            },
            "total_price": 0,
            "total_shipping": 0,
            "total_tax": 0,
            "status": "canceled",
            "shipping_method": 1,
            "created_at": "2019-12-09 10:46:53+00:00"
        }

        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/orders/5dee261dc400914833007902/cancel.json',
            data=data_returned_from_url
        )

        order_info = self.api.cancel_order('shop_123', '5dee261dc400914833007902')

        self.assertEqual(order_info, Order.from_dict(data_returned_from_url))
        self.assertEqual(order_info.status, 'canceled')

    @responses.activate
    def test_get_artwork_uploads(self):
        first_data_returned_from_url = {
            "current_page": 1,
            "data": [
                {
                    "id": "5e16d66791287a0006e522b1",
                    "file_name": "png-images-logo-1.jpg",
                    "height": 5979,
                    "width": 17045,
                    "size": 1138575,
                    "mime_type": "image/png",
                    "preview_url": "https://example.com/image-storage/uuid1",
                    "upload_time": "2020-01-09 07:29:43"
                },
                {
                    "id": "5de50bf612c348000892b366",
                    "file_name": "png-images-logo-2.jpg",
                    "height": 360,
                    "width": 360,
                    "size": 19589,
                    "mime_type": "image/jpeg",
                    "preview_url": "https://example.com/image-storage/uuid2",
                    "upload_time": "2019-12-02 13:04:54"
                }
            ],
            "first_page_url": "/?page=1",
            "from": 1,
            "last_page": 1,
            "last_page_url": "/?page=2",
            "path": "/",
            "per_page": 10,
            "prev_page_url": None,
            "to": 2,
            "total": 2,
            "next_page_url": '?page=2'
        }
        second_data_returned_from_url = {
            "current_page": 1,
            "data": [
                {
                    "id": "5e16d66791287a0006e522b2",
                    "file_name": "png-images-logo-1.jpg",
                    "height": 5979,
                    "width": 17045,
                    "size": 1138575,
                    "mime_type": "image/png",
                    "preview_url": "https://example.com/image-storage/uuid1",
                    "upload_time": "2020-01-09 07:29:43"
                },
                {
                    "id": "5de50bf612c348000892b366",
                    "file_name": "png-images-logo-2.jpg",
                    "height": 360,
                    "width": 360,
                    "size": 19589,
                    "mime_type": "image/jpeg",
                    "preview_url": "https://example.com/image-storage/uuid2",
                    "upload_time": "2019-12-02 13:04:54"
                }
            ],
            "first_page_url": "/?page=1",
            "from": 1,
            "last_page": 1,
            "last_page_url": "/?page=2",
            "next_page_url": None,
            "path": "/",
            "per_page": 10,
            "prev_page_url": '/',
            "to": 2,
            "total": 2
        }

        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/uploads.json',
            data=first_data_returned_from_url
        )
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/uploads.json?page=2',
            data=second_data_returned_from_url
        )

        artwork_info = self.api.get_artwork_uploads(max_pages=3)

        self.assertEqual(artwork_info,
                         [Artwork.from_dict(x) for x in first_data_returned_from_url['data']] +
                         [Artwork.from_dict(x) for x in second_data_returned_from_url['data']])

        for artwork in artwork_info:
            for key in ['id', 'file_name', 'height', 'width', 'size', 'mime_type', 'preview_url', 'upload_time']:
                self.assertIsNotNone(artwork.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_get_artwork(self):
        data_returned_from_url = {
            "id": "5e16d66791287a0006e522b2",
            "file_name": "png-images-logo-1.jpg",
            "height": 5979,
            "width": 17045,
            "size": 1138575,
            "mime_type": "image/png",
            "preview_url": "https://example.com/image-storage/uuid1",
            "upload_time": "2020-01-09 07:29:43"
        }
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/uploads/5e16d66791287a0006e522b2.json',
            data=data_returned_from_url
        )

        artwork_info = self.api.get_artwork("5e16d66791287a0006e522b2")

        self.assertEqual(artwork_info, Artwork.from_dict(data_returned_from_url))

    @responses.activate
    def test_upload_artwork_with_filename(self):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = f'{current_dir_path}/tiny.jpg'

        data_returned_from_url = {
            "id": "5941187eb8e7e37b3f0e62e5",
            "file_name": "image.png",
            "height": 200,
            "width": 400,
            "size": 1021,
            "mime_type": "image/png",
            "preview_url": "https://example.com/image-storage/uuid3",
            "upload_time": "2020-01-09 07:29:43"
        }
        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/uploads/images.json',
            data=data_returned_from_url
        )

        artwork_info = self.api.upload_artwork(filename=filename)

        self.assertEqual(artwork_info, Artwork.from_dict(data_returned_from_url))
        for key in ['id', 'file_name', 'height', 'width', 'size', 'mime_type', 'preview_url', 'upload_time']:
            self.assertIsNotNone(artwork_info.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_upload_artwork_with_url(self):
        data_returned_from_url = {
            "id": "5941187eb8e7e37b3f0e62e5",
            "file_name": "image.png",
            "height": 200,
            "width": 400,
            "size": 1021,
            "mime_type": "image/png",
            "preview_url": "https://example.com/image-storage/uuid3",
            "upload_time": "2020-01-09 07:29:43"
        }
        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/uploads/images.json',
            data=data_returned_from_url
        )

        artwork_info = self.api.upload_artwork(url='http://somekindofimage.com/image.png')

        self.assertEqual(artwork_info, Artwork.from_dict(data_returned_from_url))
        for key in ['id', 'file_name', 'height', 'width', 'size', 'mime_type', 'preview_url', 'upload_time']:
            self.assertIsNotNone(artwork_info.__getattribute__(key), f'{key} should not be None')

    def test_upload_artwork_raises_with_bad_request(self):
        with self.assertRaises(PrintiPyException):
            self.api.upload_artwork()
        with self.assertRaises(PrintiPyException):
            self.api.upload_artwork(filename='something', url='something_else')

    @responses.activate
    def test_archive_artwork(self):
        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/uploads/img_123/archive.json',
            data={}
        )
        self.assertTrue(self.api.archive_artwork('img_123'))

    @responses.activate
    def test_get_shop_webhooks(self):
        data_returned_from_url = [
            {
                "topic": "order:created",
                "url": "https://example.com/webhooks/order/created",
                "shop_id": "1",
                "id": "5cb87a8cd490a2ccb256cec4"
            },
            {
                "topic": "order:updated",
                "url": "https://example.com/webhooks/order/updated",
                "shop_id": "1",
                "id": "5cb87a8cd490a2ccb256cec5"
            }
        ]
        self.__prepare_response(
            responses.GET,
            'https://api.printify.com/v1/shops/shop_123/webhooks.json',
            data=data_returned_from_url
        )

        webhooks_info = self.api.get_shop_webhooks('shop_123')

        self.assertEqual(webhooks_info, [Webhook.from_dict(x) for x in data_returned_from_url])
        for webhook in webhooks_info:
            for key in ['topic', 'url', 'shop_id', 'id']:
                self.assertIsNotNone(webhook.__getattribute__(key), f'{key} should not be None')

    @responses.activate
    def test_create_webhook(self):
        data_for_url = {
            "topic": "order:created",
            "url": "https://example.com/webhooks/order/created"
        }
        data_returned_from_url = {
            "topic": "order:created",
            "url": "https://example.com/webhooks/order/created",
            "shop_id": "1",
            "id": "5cb87a8cd490a2ccb256cec4"
        }
        self.__prepare_response(
            responses.POST,
            'https://api.printify.com/v1/shops/shop_123/webhooks.json',
            data=data_returned_from_url
        )

        webhooks_info = self.api.create_webhook('shop_123', CreateWebhook.from_dict(data_for_url))

        self.assertEqual(webhooks_info, Webhook.from_dict(data_returned_from_url))

    @responses.activate
    def test_update_webhook(self):
        data_for_url = {
            "url": "https://example.com/callback/order/created"
        }
        data_returned_from_url = {
            "topic": "order:created",
            "url": "https://example.com/callback/order/created",
            "shop_id": "1",
            "id": "5cb87a8cd490a2ccb256cec4"
        }
        self.__prepare_response(
            responses.PUT,
            'https://api.printify.com/v1/shops/shop_123/webhooks/5cb87a8cd490a2ccb256cec4.json',
            data=data_returned_from_url
        )

        webhooks_info = self.api.update_webhook('shop_123', '5cb87a8cd490a2ccb256cec4',
                                                UpdateWebhook.from_dict(data_for_url))

        self.assertEqual(webhooks_info, Webhook.from_dict(data_returned_from_url))

    @responses.activate
    def test_delete_webhook(self):
        self.__prepare_response(
            responses.DELETE,
            url='https://api.printify.com/v1/shops/12345/webhooks/54321.json',
        )
        self.assertTrue(self.api.delete_webhook('12345', '54321'))
