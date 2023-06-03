import base64
import json
import os
from copy import deepcopy
from json import JSONDecodeError
from typing import List, Optional, Dict, Union, Any

import requests
from requests import Response

from printipy.data_objects import Shop, Blueprint, PrintProvider, PrintProviderVariants, \
    ShippingInfo, ShippingCost, CreateShippingEstimate, Product, Publish, PublishingSucceeded, Order, \
    CreateOrderByExistingProduct, CreateOrderByAdvancedImageProcessing, \
    CreateOrderByPrintDetails, CreateOrderBySku, Artwork, Webhook, CreateWebhook, UpdateWebhook, \
    CreateProduct, UpdateProduct
from printipy.exceptions import PrintiPyException, PrintiPyParseException, InvalidScopeException, \
    InvalidRequestException, PrintifyException


class _ApiHandlingMixin:
    api_url = 'https://api.printify.com'

    def __init__(self, api_token: str):
        self.api_token = api_token

    @staticmethod
    def __check_status(resp: Response, url: str):
        if resp.status_code == 400:
            try:
                info = json.loads(resp.text)
                message = f'{info["message"]} {info["errors"]["reason"]}'
            except JSONDecodeError:
                message = f'Bad Request: {url}'
            raise PrintifyException(message)
        elif resp.status_code == 403:
            raise InvalidScopeException('This API key is not permitted to access this information.')
        elif resp.status_code == 500:
            raise InvalidRequestException(f'Bad request to {url}')
        data = resp.json()
        if 'error' in data:
            raise PrintifyException(data['error'])
        return data

    def _get(self, url):
        headers = {'Authorization': f'Bearer {self.api_token}'}
        resp = requests.get(url, headers=headers)
        data = self.__check_status(resp, url)
        return data

    def _post(self, url: str, data: Optional[Dict[str, Any]] = None):
        headers = {'Authorization': f'Bearer {self.api_token}', 'content-type': 'application/json'}
        resp = requests.post(url, headers=headers, json=data)
        data = self.__check_status(resp, url)
        return data

    def _put(self, url, data):
        headers = {'Authorization': f'Bearer {self.api_token}', 'content-type': 'application/json'}
        resp = requests.put(url, headers=headers, json=data)
        data = self.__check_status(resp, url)
        return data

    def _delete(self, url):
        headers = {'Authorization': f'Bearer {self.api_token}'}
        resp = requests.delete(url, headers=headers)
        data = self.__check_status(resp, url)
        return data

    @staticmethod
    def _parse(clazz, data: Union[List, Dict]):
        if type(data) == list:
            all_elements = []
            for item in data:
                all_elements.append(clazz.from_dict(item))
            return all_elements
        elif type(data) == dict:
            return clazz.from_dict(data)
        else:
            raise PrintiPyParseException('Unable to parse response: was not a list or object')

    @staticmethod
    def _get_next_page_url(initial_url: str, info: Dict) -> Optional[str]:
        next_page = info.get('next_page_url', None)
        if not next_page:
            return None
        return f'{initial_url}{next_page}'


class PrintiPyShop(_ApiHandlingMixin):
    """
    Used to access the [Printify Shops](https://developers.printify.com/#shops) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...')
        >>> shops = api.shops.get_shops()
    """

    def get_shops(self) -> List[Shop]:
        """
        Pulls a list of shops for a Printify account. Returns empty list if no shops exist for account.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> shops = api.shops.get_shops()

        Returns:
            List of `printipy.data_objects.Shop` objects

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        shops_url = f'{self.api_url}/v1/shops.json'
        shop_information = self._get(shops_url)
        return self._parse(Shop, shop_information)

    def delete_shop(self, shop: Shop) -> None:
        """
        Deletes a shop from a Printify account

        Examples:
            By pass in data pulled from `printipy.api.PrintiPyShop.get_shops`
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> shops = api.shops.get_shops()
            >>> api.shops.delete_shop(shops[0])

            By passing in specific shop information
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> api.shops.delete_shop(shop)

        Args:
            shop (Shop): A Shop to delete. Pull all shops using :func:`get_shops <printipy.api.PrintiPyShop.get_shops>`

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        delete_url = f'{self.api_url}/v1/shops/{shop.id}/connection.json'
        self._delete(delete_url)


class PrintiPyCatalog(_ApiHandlingMixin):
    """
    Used to access the [Printify Catalog](https://developers.printify.com/#catalog) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...')
        >>> print_providers = api.catalog.get_print_providers()
    """
    def get_blueprints(self) -> List[Blueprint]:
        """
        Pulls a list of all blueprints available from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> blueprints = api.catalog.get_blueprints()

        Returns:
            List of `printipy.data_objects.Blueprint` objects

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
        """
        blueprint_url = f'{self.api_url}/v1/catalog/blueprints.json'
        blueprint_information = self._get(blueprint_url)
        return self._parse(Blueprint, blueprint_information)

    def get_blueprint(self, blueprint_id: Union[str, int]) -> Blueprint:
        """
        Pulls a specific blueprint from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> blueprint = api.catalog.get_blueprint('...')

        Returns:
            Blueprint `printipy.data_objects.Blueprint` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Blueprint ID does not exist in Printify
        """
        # GET / v1 / catalog / blueprints / {blueprint_id}.json
        blueprint_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}.json'
        blueprint_information = self._get(blueprint_url)
        return self._parse(Blueprint, blueprint_information)

    def get_print_providers_for_blueprint(self, blueprint_id: Union[str, int]) -> List[PrintProvider]:
        """
        Pulls a list of print providers for a given blueprint from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> blueprint = api.catalog.get_blueprint('...')
            >>> print_providers = api.catalog.get_print_providers_for_blueprint(blueprint.id)

        Returns:
            List of `printipy.data_objects.PrintProvider` objects

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Blueprint ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers.json
        print_providers_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/print_providers.json'
        print_provider_information = self._get(print_providers_url)
        return self._parse(PrintProvider, print_provider_information)

    def get_variants(self, blueprint_id: Union[str, int], print_provider_id: Union[str, int]) -> PrintProviderVariants:
        """
        Pulls a list of variants for a given blueprint and print provider from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> blueprint = api.catalog.get_blueprint('...')
            >>> print_providers = api.catalog.get_print_providers_for_blueprint(blueprint.id)
            >>> variants = api.catalog.get_variants(blueprint.id, print_providers[0].id)

        Returns:
            Variant `printipy.data_objects.PrintProviderVariants` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Blueprint ID or Print Provider ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers / {print_provider_id} / variants.json
        variants_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/' \
                       f'print_providers/{print_provider_id}/variants.json'
        variant_information = self._get(variants_url)
        return self._parse(PrintProviderVariants, variant_information)

    def get_shipping_info(self, blueprint_id: Union[str, int], print_provider_id: Union[str, int]) -> ShippingInfo:
        """
        Pulls a shipping information a given blueprint and print provider from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> blueprint = api.catalog.get_blueprint('...')
            >>> print_providers = api.catalog.get_print_providers_for_blueprint(blueprint.id)
            >>> shipping_info = api.catalog.get_shipping_info(blueprint.id, print_providers[0].id)

        Returns:
            Shipping information `printipy.data_objects.ShippingInfo` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Blueprint ID or Print Provider ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers / {print_provider_id} / shipping.json
        shipping_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/' \
                       f'print_providers/{print_provider_id}/shipping.json'
        shipping_information = self._get(shipping_url)
        return self._parse(ShippingInfo, shipping_information)

    def get_print_providers(self) -> List[PrintProvider]:
        """
        Pulls a list of all print providers from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> print_providers = api.catalog.get_print_providers()

        Returns:
            List of `printipy.data_objects.PrintProvider` objects

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / catalog / print_providers.json
        print_providers_url = f'{self.api_url}/v1/catalog/print_providers.json'
        print_provider_information = self._get(print_providers_url)
        return self._parse(PrintProvider, print_provider_information)

    def get_print_provider(self, print_provider_id: Union[str, int]) -> PrintProvider:
        """
        Pulls a specific print provider from Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> print_provider = api.catalog.get_print_provider('...')

        Returns:
            Print Provider `printipy.data_objects.PrintProvider` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Print Provider ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / catalog / print_providers / {print_provider_id}.json
        print_provider_url = f'{self.api_url}/v1/catalog/print_providers/{print_provider_id}.json'
        print_provider_information = self._get(print_provider_url)
        return self._parse(PrintProvider, print_provider_information)


class _ShopIdMixin:
    def __init__(self, shop_id: Optional[Union[str, int]]):
        self.__shop_id = shop_id

    def _get_shop_id(self, shop_id: Optional[Union[str, int]]):
        shop_id_to_use = shop_id or self.__shop_id
        if not shop_id_to_use:
            raise PrintiPyException(
                "No shop_id was specified. Add it to the method call or the instantiation of the API.")
        return shop_id_to_use

    def _require_shop_id(func):
        def inner(ref, *args, **kwargs):
            given_shop_id = kwargs.pop('shop_id', None)
            shop_id = ref._get_shop_id(given_shop_id)
            return func(ref, *args, **kwargs, shop_id=shop_id)

        return inner


class PrintiPyProducts(_ApiHandlingMixin, _ShopIdMixin):
    """
    Used to access the [Printify Products](https://developers.printify.com/#products) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> shop_products = api.products.get_products()
    """
    def __init__(self, api_token: str, shop_id: Optional[Union[str, int]]):
        _ApiHandlingMixin.__init__(self, api_token=api_token)
        _ShopIdMixin.__init__(self, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def get_products(self, shop_id: Union[str, int], max_pages: int = 1) -> List[Product]:
        """
        Pulls products for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> products = api.products.get_products(shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time

            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> products = api.products.get_products()

        Args:
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull products.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
            max_pages: Printify's API is paginated for requests. This will set the maximum number of pages to ingest.
        Returns:
            List of products `printipy.data_objects.Product` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / shops / {shop_id} / products.json
        initial_url = f'{self.api_url}/v1/shops/{shop_id}/products.json'
        products_url = deepcopy(initial_url)
        all_products = []
        for _ in range(max_pages):
            if products_url is None:
                break
            products_information = self._get(products_url)
            all_products.extend(self._parse(Product, products_information['data']))
            products_url = self._get_next_page_url(initial_url, products_information)
        return all_products

    @_ShopIdMixin._require_shop_id
    def get_product(self, product_id: str, shop_id: Union[str, int]) -> Product:
        """
        Pull a specific product for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> product = api.products.get_product(product_id='...', shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time

            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product = api.products.get_product(product_id='...')

        Args:
            product_id: The ID of the specific product to pull
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull products.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Product `printipy.data_objects.Product` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID or Product ID do not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / shops / {shop_id} / products / {product_id}.json
        product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._get(product_url)
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def create_product(self, create_product: CreateProduct, shop_id: Union[str, int]) -> Product:
        """
        Create a product for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level and using CreateProduct.from_dict
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateProduct
            >>> api = PrintiPy(api_token='...')
            >>> product_info = {
            >>>     "title": '...',
            >>>     "description": '...',
            >>>     "blueprint_id": ...,
            >>>     "print_provider_id": ...,
            >>>     "variants": [...],
            >>>     "print_areas": [...],
            >>> }
            >>> product = api.products.create_product(
            >>>                create_product=CreateProduct.from_dict(product_info), shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time and using a CreateProduct object
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product_info = CreateProduct(
            >>>     title='...',
            >>>     description='...',
            >>>     blueprint_id=...,
            >>>     print_provider_id=...,
            >>>     variants=[...],
            >>>     print_areas=[...],
            >>> )
            >>> product = api.products.create_product(create_product=product_info)

        Args:
            create_product: Product metadata to pass to Printify
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Product `printipy.data_objects.Product` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        shop_id_to_use = self._get_shop_id(shop_id)
        # POST / v1 / shops / {shop_id} / products.json
        create_product_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/products.json'
        product_information = self._post(create_product_url, data=create_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def update_product(self, product_id: str, update_product: UpdateProduct, shop_id: Union[str, int]) -> Product:
        """
        Updates a specific product for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level and using UpdateProduct.from_dict
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...')
            >>> product_info = {
            >>>     "title": '...',
            >>>     "description": '...',
            >>>     "blueprint_id": ...,
            >>>     "print_provider_id": ...,
            >>>     "variants": [...],
            >>>     "print_areas": [...],
            >>> }
            >>> product = api.products.update_product(product_id='...',
            >>>             update_product=UpdateProduct.from_dict(product_info), shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time and using a UpdateProduct object
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product_info = UpdateProduct(
            >>>     title='...',
            >>>     description='...',
            >>>     blueprint_id=...,
            >>>     print_provider_id=...,
            >>>     variants=[...],
            >>>     print_areas=[...],
            >>> )
            >>> product = api.products.update_product(product_id='...', update_product=product_info)

        Args:
            product_id: ID of the product to update
            update_product: Product metadata to pass to Printify
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Product `printipy.data_objects.Product` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # PUT / v1 / shops / {shop_id} / products / {product_id}.json
        update_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._put(update_product_url, data=update_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def delete_product(self, product_id: str, shop_id: Union[str, int]) -> True:
        """
        Examples:
            By passing in data pulled from `printipy.api.PrintiPyShop.get_products`
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> products = api.products.get_products()
            >>> api.products.delete_product(product_id=products[0].id)

            By passing in specific shop information
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...')
            >>> products = api.products.get_products()
            >>> api.products.delete_product(product_id=products[0].id, shop_id='...')

        Args:
            product_id: ID of the product to publish
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # DELETE / v1 / shops / {shop_id} / products / {product_id}.json
        delete_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        self._delete(delete_product_url)
        return True

    @_ShopIdMixin._require_shop_id
    def publish_product(self, product_id: str, publish: Publish, shop_id: Union[str, int]) -> True:
        """
        Publishes changes for a specific product for a given store in Printify

        Examples:
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product = api.products.create_product(...)
            >>> api.products.publish_product(product.id, Publish())

        Args:
            product_id: ID of the product to publish
            publish: Publish settings for the product
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            True when a product has been marked for publishing

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publish.json
        publish_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publish.json'
        self._post(publish_product_url, data=publish.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_success(self, product_id: str, publishing_succeeded: PublishingSucceeded,
                                      shop_id: Union[str, int]) -> True:
        """
        Marks a product as published for a given store in Printify. Useful when managing a custom site,
        not a linked store supportd by Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product = api.products.create_product(...)
            >>> api.products.publish_product(product.id, Publish())
            >>> api.products.set_product_published_success(product.id, PublishingSucceeded(...))

        Args:
            product_id: ID of the product
            publishing_succeeded: Publishing details for the external store
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            True when a product has been marked as published

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_succeeded.json
        publishing_succeeded_url = f'{self.api_url}/v1/shops/{shop_id}/products/' \
                                   f'{product_id}/publishing_succeeded.json'
        self._post(publishing_succeeded_url, data=publishing_succeeded.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_failed(self, product_id: str, reason: str, shop_id: Union[str, int]) -> True:
        """
        Marks a product as not published for a given store in Printify. Useful when managing a custom site,
        not a linked store supportd by Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product = api.products.create_product(...)
            >>> api.products.publish_product(product.id, Publish())
            >>> api.products.set_product_published_failed(product.id, reason='...')

        Args:
            product_id: ID of the product
            reason: Explination of a publishing failure - useful for tacking
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            True when a product has been marked as not published

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_failed.json
        publishing_failed_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publishing_failed.json'
        self._post(publishing_failed_url, data={"reason": reason})
        return True

    @_ShopIdMixin._require_shop_id
    def unpublish_product(self, product_id: str, shop_id: Union[str, int]) -> True:
        """
        Removes a published product from the storefront a given store in Printify

        Examples:
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateProduct
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> product_id = '...'
            >>> api.products.unpublish_product(product_id)

        Args:
            product_id: ID of the product to unpublish
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            True when a product has been marked as unpublished

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / unpublish.json
        unpublish_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/unpublish.json'
        self._post(unpublish_product_url)
        return True


class PrintiPyOrders(_ApiHandlingMixin, _ShopIdMixin):
    """
    Used to access the [Printify Orders](https://developers.printify.com/#orders) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> shop_orders = api.orders.get_orders()
    """
    def __init__(self, api_token: str, shop_id: Optional[Union[str, int]]):
        _ApiHandlingMixin.__init__(self, api_token=api_token)
        _ShopIdMixin.__init__(self, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def get_orders(self, max_pages: int = 1, shop_id: Optional[Union[str, int]] = None) -> List[Order]:
        """
        Pulls orders for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> orders = api.orders.get_orders(shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time

            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> orders = api.orders.get_orders()

        Args:
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
            max_pages: Printify's API is paginated for requests. This will set the maximum number of pages to ingest.
        Returns:
            List of orders `printipy.data_objects.Order` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        shop_id_to_use = self._get_shop_id(shop_id)
        # GET / v1 / shops / {shop_id} / orders.json
        initial_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/orders.json'
        orders_url = deepcopy(initial_url)
        all_orders = []
        for _ in range(max_pages):
            if orders_url is None:
                break
            orders_information = self._get(orders_url)
            all_orders.extend(self._parse(Order, orders_information['data']))
            orders_url = self._get_next_page_url(initial_url, orders_information)
        return all_orders

    @_ShopIdMixin._require_shop_id
    def get_order(self, order_id: str, shop_id: Optional[Union[str, int]] = None) -> Order:
        """
        Pulls a specific order for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> order = api.orders.get_order(order_id='...', shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time

            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> order = api.orders.get_order(order_id='...')

        Args:
            order_id: ID of the order to pull for a specific shop in Printify.
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Orders `printipy.data_objects.Order` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID or Order ID do not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        shop_id_to_use = self._get_shop_id(shop_id)
        # GET / v1 / shops / {shop_id} / orders / {order_id}.json
        order_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/orders/{order_id}.json'
        order_information = self._get(order_url)
        return self._parse(Order, order_information)

    def __create_order(self, create_order: Union[CreateOrderByPrintDetails, CreateOrderBySku,
                       CreateOrderByExistingProduct, CreateOrderByAdvancedImageProcessing],
                       shop_id: Union[str, int]) -> str:
        # POST / v1 / shops / {shop_id} / orders.json
        create_order_url = f'{self.api_url}/v1/shops/{shop_id}/orders.json'
        order_information = self._post(create_order_url, data=create_order.to_dict())
        return order_information['id']

    @_ShopIdMixin._require_shop_id
    def create_order_for_existing_product(self, create_order: CreateOrderByExistingProduct,
                                          shop_id: Union[str, int]) -> str:
        """
        Create an order for an existing project for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> new_order_props = CreateOrderByExistingProduct.from_dict({
            >>>   "external_id": "2750e210-39bb-11e9-a503-452618153e4a",
            >>>   "label": "00012",
            >>>   "line_items": [
            >>>     {
            >>>       "product_id": "5bfd0b66a342bcc9b5563216",
            >>>       "variant_id": 17887,
            >>>       "quantity": 1
            >>>     }
            >>>   ],
            >>>   "shipping_method": 1,
            >>>   "send_shipping_notification": False,
            >>>   "address_to": {
            >>>     "first_name": "John",
            >>>     "last_name": "Smith",
            >>>     "email": "example@msn.com",
            >>>     "phone": "0574 69 21 90",
            >>>     "country": "BE",
            >>>     "region": "",
            >>>     "address1": "ExampleBaan 121",
            >>>     "address2": "45",
            >>>     "city": "Retie",
            >>>     "zip": "2470"
            >>> })
            >>> order_number = api.orders.create_order_for_existing_product(new_order_props)


        Args:
            create_order: Order information
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order reference number

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_simple_image_positioning(self, create_order: CreateOrderByExistingProduct,
                                                   shop_id: Union[str, int]) -> str:
        """
        Create an order for a new product using simple image positioning.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> new_order_props = CreateOrderByExistingProduct.from_dict({
            >>>    "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            >>>    "label": "00012",
            >>>    "line_items": [
            >>>      {
            >>>        "print_provider_id": 5,
            >>>        "blueprint_id": 9,
            >>>        "variant_id": 17887,
            >>>        "print_areas": {
            >>>          "front": "https://images.example.com/image.png"
            >>>        },
            >>>        "quantity": 1
            >>>      }
            >>>    ],
            >>>    "shipping_method": 1,
            >>>    "send_shipping_notification": False,
            >>>    "address_to": {
            >>>      "first_name": "John",
            >>>      "last_name": "Smith",
            >>>      "email": "example@msn.com",
            >>>      "phone": "0574 69 21 90",
            >>>      "country": "BE",
            >>>      "region": "",
            >>>      "address1": "ExampleBaan 121",
            >>>      "address2": "45",
            >>>      "city": "Retie",
            >>>      "zip": "2470"
            >>>    }
            >>> })
            >>> order_number = api.orders.create_order_with_simple_image_positioning(new_order_props)


        Args:
            create_order: Order information
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order reference number

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_advanced_image_positioning(self, create_order: CreateOrderByAdvancedImageProcessing,
                                                     shop_id: Union[str, int]) -> str:
        """
        Create an order for a new product using advanced image positioning.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> new_order_props = CreateOrderByAdvancedImageProcessing.from_dict({
            >>>    "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            >>>    "label": "00012",
            >>>    "line_items": [
            >>>      {
            >>>        "print_provider_id": 5,
            >>>        "blueprint_id": 9,
            >>>        "variant_id": 17887,
            >>>        "print_areas": {
            >>>          "front": [
            >>>            {
            >>>                "src": "https://images.example.com/image.png",
            >>>                "scale": 0.15,
            >>>                "x": 0.80,
            >>>                "y": 0.34,
            >>>                "angle": 0.34
            >>>            },
            >>>            {
            >>>                "src": "https://images.example.com/image.png",
            >>>                "scale": 1,
            >>>                "x": 0.5,
            >>>                "y": 0.5,
            >>>                "angle": 1
            >>>            }
            >>>          ]
            >>>        },
            >>>        "quantity": 1
            >>>      }
            >>>    ],
            >>>    "shipping_method": 1,
            >>>    "send_shipping_notification": False,
            >>>    "address_to": {
            >>>      "first_name": "John",
            >>>      "last_name": "Smith",
            >>>      "email": "example@msn.com",
            >>>      "phone": "0574 69 21 90",
            >>>      "country": "BE",
            >>>      "region": "",
            >>>      "address1": "ExampleBaan 121",
            >>>      "address2": "45",
            >>>      "city": "Retie",
            >>>      "zip": "2470"
            >>>    }
            >>> })
            >>> order_number = api.orders.create_order_with_advanced_image_positioning(new_order_props)

        Args:
            create_order: Order information
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order reference number

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_print_details(self, create_order: CreateOrderByPrintDetails, shop_id: Union[str, int]) -> str:
        """
        Create an order for a new product using print deatils.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> new_order_props = CreateOrderByPrintDetails.from_dict({
            >>>        "external_id": "2750e210-39bb-11e9-a503-452618153e5a",
            >>>        "label": "00012",
            >>>        "line_items": [
            >>>          {
            >>>            "print_provider_id": 5,
            >>>            "blueprint_id": 9,
            >>>            "variant_id": 17887,
            >>>            "print_areas": {
            >>>              "front": "https://images.example.com/image.png"
            >>>            },
            >>>            "print_details": {
            >>>                "print_on_side": "mirror"
            >>>            },
            >>>            "quantity": 1
            >>>          }
            >>>        ],
            >>>        "shipping_method": 1,
            >>>        "send_shipping_notification": False,
            >>>        "address_to": {
            >>>          "first_name": "John",
            >>>          "last_name": "Smith",
            >>>          "email": "example@msn.com",
            >>>          "phone": "0574 69 21 90",
            >>>          "country": "BE",
            >>>          "region": "",
            >>>          "address1": "ExampleBaan 121",
            >>>          "address2": "45",
            >>>          "city": "Retie",
            >>>          "zip": "2470"
            >>>    }
            >>> })
            >>> order_number = api.orders.create_order_with_print_details(new_order_props)

        Args:
            create_order: Order information
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order reference number

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_sku(self, create_order: CreateOrderBySku, shop_id: Union[str, int]) -> str:
        """
        Create an order for a product based on its SKU.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> new_order_props = CreateOrderBySku.from_dict({
            >>>    "external_id": "2750e210-39bb-11e9-a503-452618153e6a",
            >>>    "label": "00012",
            >>>    "line_items": [
            >>>      {
            >>>        "sku": "MY-SKU",
            >>>        "quantity": 1
            >>>      }
            >>>    ],
            >>>    "shipping_method": 1,
            >>>    "send_shipping_notification": False,
            >>>    "address_to": {
            >>>      "first_name": "John",
            >>>      "last_name": "Smith",
            >>>      "email": "example@msn.com",
            >>>      "phone": "0574 69 21 90",
            >>>      "country": "BE",
            >>>      "region": "",
            >>>      "address1": "ExampleBaan 121",
            >>>      "address2": "45",
            >>>      "city": "Retie",
            >>>      "zip": "2470"
            >>>    }
            >>> })
            >>> order_number = api.orders.create_order_with_sku(new_order_props)

        Args:
            create_order: Order information
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order reference number

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def send_order_to_production(self, order_id: str, shop_id: Union[str, int]) -> Order:
        """
        Sends an open order to production in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> order_number = api.orders.create_order_with_sku(...)
            >>> order = api.orders.send_order_to_production(order_number)

        Args:
            order_id: Order ID
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to create orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            Order `printipy.data_objects.Order` information

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If either the Shop ID or Order Number does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / orders / {order_id} / send_to_production.json
        send_order_to_production_url = f'{self.api_url}/v1/shops/{shop_id}/orders/{order_id}/send_to_production.json'
        order_information = self._post(send_order_to_production_url)
        return self._parse(Order, order_information)

    @_ShopIdMixin._require_shop_id
    def calc_shipping_for_order(self, create_shipping_cost_estimate: CreateShippingEstimate,
                                shop_id: Union[str, int]) -> ShippingCost:
        """
        Calculate shipping cost for an order for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level and using CreateShippingEstimate.from_dict
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateShippingEstimate
            >>> api = PrintiPy(api_token='...')
            >>> estimate_info = {
            >>>     "line_items": [...],
            >>>     "address_to": {...},
            >>> }
            >>> shipping_cost = api.orders.calc_shipping_for_order(
            >>>                   create_shipping_cost_estimate=CreateShippingEstimate.from_dict(estimate_info),
            >>>                   shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time and using a CreateShippingEstimate object
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateShippingEstimate
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> estimate_info = CreateShippingEstimate(
            >>>     line_items=[...],
            >>>     address_to=...,
            >>> )
            >>> shipping_cost = api.orders.calc_shipping_for_order(create_shipping_cost_estimate=estimate_info)

        Args:
            create_shipping_cost_estimate: Order adn shipping information to pass to Printify
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Shipping cost `printipy.data_objects.ShippingCost` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST / v1 / shops / {shop_id} / orders / shipping.json
        shipping_estimate_url = f'{self.api_url}/v1/shops/{shop_id}/orders/shipping.json'
        shipping_information = self._post(shipping_estimate_url, data=create_shipping_cost_estimate.to_dict())
        return self._parse(ShippingCost, shipping_information)

    @_ShopIdMixin._require_shop_id
    def cancel_order(self, order_id: str, shop_id: Union[str, int]) -> Order:
        """
        Canceles a specific order for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> order = api.orders.cancel_order(order_id='...', shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> order = api.orders.cancel_order(order_id='...')

        Args:
            order_id: ID of the order to cancel
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Order `printipy.data_objects.Order` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed
             input or why the order cannot be canceled
        """
        # POST / v1 / shops / {shop_id} / orders / {order_id} / cancel.json
        cancel_order_url = f'{self.api_url}/v1/shops/{shop_id}/orders/{order_id}/cancel.json'
        order_information = self._post(cancel_order_url)
        return self._parse(Order, order_information)


class PrintiPyArtwork(_ApiHandlingMixin):
    """
    Used to access the [Printify Uploads](https://developers.printify.com/#uploads) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...')
        >>> artwork = api.artwork.upload_artwork(filename='...')
    """
    def get_artwork_uploads(self, max_pages: int = 1) -> List[Artwork]:
        """
        Pulls artwork/image information for an account in Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> artworks = api.artwork.get_artwork_uploads()

        Args:
            max_pages: Printify's API is paginated for requests. This will set the maximum number of pages to ingest.
        Returns:
            List of artwork `printipy.data_objects.Artwork` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Artwork ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # GET / v1 / uploads.json
        initial_url = f'{self.api_url}/v1/uploads.json'
        artwork_url = deepcopy(initial_url)
        all_artworks = []
        for _ in range(max_pages):
            if artwork_url is None:
                break
            artwork_information = self._get(artwork_url)
            all_artworks.extend(self._parse(Artwork, artwork_information['data']))
            artwork_url = self._get_next_page_url(initial_url, artwork_information)
        return all_artworks

    def get_artwork(self, image_id: str) -> Artwork:
        """
        Pulls information for a speciic artwork/image for an account in Printify.

        Examples:
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> artwork = api.artwork.get_artwork(image_id='...')

        Args:
            image_id: The ID of the specific artwork for an account in Printify.
        Returns:
            Artwork `printipy.data_objects.Artwork` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
        """
        # GET / v1 / uploads / {image_id}.json
        artwork_url = f'{self.api_url}/v1/uploads/{image_id}.json'
        artwork_information = self._get(artwork_url)
        return self._parse(Artwork, artwork_information)

    def upload_artwork(self, filename: Optional[str] = None, url: Optional[str] = None) -> Artwork:
        """
        Uploads a new image/artwork to an account in Printify

        Examples:
            Using a local file
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...')
            >>> filename = '...'
            >>> artwork = api.artwork.upload_artwork(filename=filename)

            Using a URL
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...')
            >>> url = '...'
            >>> artwork = api.artwork.upload_artwork(url=url)

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the artwork isn't transmissible to Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
            PrintiPyException: If neither or both filename and url are presented. Only one must be given.
        """
        if filename and url:
            raise PrintiPyException("Must provide a local filename or url for upload, not both.")

        # POST / v1 / uploads / images.json
        upload_artwork_url = f'{self.api_url}/v1/uploads/images.json'
        if url:
            artwork_data = {
                "file_name": url.split('/')[-1],
                "url": url,
            }
        elif filename:
            with open(filename, 'rb') as f:
                b64data = base64.b64encode(f.read())
            artwork_data = {
                "file_name": os.path.basename(filename),
                "contents": b64data.decode('utf-8'),
            }
        else:
            raise PrintiPyException("Must provide at least a local filename or url for upload.")

        artwork_information = self._post(upload_artwork_url, data=artwork_data)
        return self._parse(Artwork, artwork_information)

    def archive_artwork(self, image_id: str) -> True:
        """
        Archives a specific artwork/image for an account in Printify

        Examples:
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...')
            >>> artworks = api.artwork.get_artwork_uploads()
            >>> api.artwork.archive_artwork(artworks[0].id)

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Artwork ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # post / v1 / uploads / {image_id} / archive.json
        archive_artwork_url = f'{self.api_url}/v1/uploads/{image_id}/archive.json'
        self._post(archive_artwork_url)
        return True


class PrintiPyWebhooks(_ApiHandlingMixin, _ShopIdMixin):
    """
    Used to access the [Printify Webhooks](https://developers.printify.com/#webhooks) APIs

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> webhooks = api.webhooks.get_webhooks()
    """
    def __init__(self, api_token: str, shop_id: Optional[Union[str, int]]):
        _ApiHandlingMixin.__init__(self, api_token=api_token)
        _ShopIdMixin.__init__(self, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def get_webhooks(self, shop_id: Union[str, int]) -> List[Webhook]:
        """
        Pulls webhooks for specific shop in Printify.

        Examples:
            With specifying the shop_id at the function level
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...')
            >>> webhooks = api.webhooks.get_webhooks(shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time

            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> webhooks = api.webhooks.get_webhooks()

        Args:
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.
        Returns:
            List of webhooks `printipy.data_objects.Webhook` object

        Raises:
            ParseException: If unable to parse Printify's response
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Shop ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # / v1 / shops / {shop_id} / webhooks.json
        webhooks_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhooks_information = self._get(webhooks_url)
        return self._parse(Webhook, webhooks_information)

    @_ShopIdMixin._require_shop_id
    def create_webhook(self, create_webhook: CreateWebhook, shop_id: Union[str, int]) -> Webhook:
        """
        Create a webhook for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level and using CreateWebhook.from_dict
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateWebhook
            >>> api = PrintiPy(api_token='...')
            >>> webhook_info = {
            >>>    "topic": "order:created",
            >>>    "url": "https://example.com/webhooks/order/created"
            >>> }
            >>> webhook = api.webhooks.create_webhook(
            >>>               create_webhook=CreateWebhook.from_dict(webhook_info), shop_id='...')

            Or, with specifying the shop_id at PrintiPy-creation time and using a CreateWebhook object
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import CreateWebhook
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> webhook_info = CreateWebhook(
            >>>     topic="order:created",
            >>>     url="https://example.com/webhooks/order/created"
            >>> )
            >>> webhook = api.webhooks.create_webhook(create_webhook=webhook_info)

        Args:
            create_webhook: Webhook metadata to pass to Printify
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Webhooks `printipy.data_objects.Webhook` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # POST /v1/shops/{shop_id}/webhooks.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhook_information = self._post(create_webhook_url, data=create_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def update_webhook(self, webhook_id: str, update_webhook: UpdateWebhook, shop_id: Union[str, int]) -> Webhook:
        """
        Updates a specific webhook for a given shop in Printify

        Examples:
            With specifying the shop_id at the function level and using UpdateWebhook.from_dict
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateWebhook
            >>> api = PrintiPy(api_token='...')
            >>> webhook_info = {
            >>>     "topic": "order:created",
            >>>     "url": "https://example.com/webhooks/order/created"
            >>> }
            >>> webhook = api.webhooks.update_webhook(
            >>>     webhook_id='...',
            >>>     update_webhook=UpdateWebhook.from_dict(webhook_info), shop_id='...'
            >>> )

            Or, with specifying the shop_id at PrintiPy-creation time and using a CreateWebhook object
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import UpdateWebhook
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> webhook_info = UpdateWebhook(
            >>>     topic="order:created",
            >>>     url="https://example.com/webhooks/order/created"
            >>> )
            >>> webhook = api.webhooks.update_webhook(update_webhook=webhook_info)

        Args:
            webhook_id: ID of the webhook to update in Printify
            update_webhook: Webhook metadata to pass to Printify
            shop_id (Optional[Union[str, int]]): Specific shop ID in Printify from which to pull orders.
            This may be set at every call to speicy different shops, or this may be set when initiating PrintiPy.

        Returns:
            Webhooks `printipy.data_objects.Webhook` object

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # PUT /v1/shops/{shop_id}/webhooks/{webhook_id}.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks/{webhook_id}.json'
        webhook_information = self._put(create_webhook_url, data=update_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def delete_webhook(self, webhook_id: str, shop_id: Union[str, int]) -> True:
        """
        Deletes a specific webhook for a specific shop in Printify

        Examples:
            By passing in data pulled from `printipy.api.PrintiPyWebhook.get_shops`
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> webhooks = api.webhooks.get_webhooks()
            >>> api.webhooks.delete_webhook(webhook_id=webhooks[0].id)

            By passing in specific shop information
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...')
            >>> webhooks = api.webhooks.get_webhooks()
            >>> api.webhooks.delete_webhook(webhook_id=webhooks[0].id, shop_id='...')

        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
            InvalidRequestException: If the Webhook ID does not exist in Printify
            PrintifyException: If Printify returned an error - usually contains information regarding malformed input
        """
        # DELETE /v1/shops/{shop_id}/webhooks/{webhook_id}.json
        delete_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks/{webhook_id}.json'
        self._delete(delete_webhook_url)
        return True


class PrintiPy:
    """
    Used to access all [Printify APIs](https://developers.printify.com/)

    Examples:
        To use the same Shop ID for each call
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> artwork = api.artwork.upload_artwork(filename='...')

        To use a differnt Shop ID for each call
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...')
        >>> shop123_products = api.products.get_products(shop_id='shop123')
        >>> shop456_products = api.products.get_products(shop_id='shop456')
    """

    def __init__(self, api_token: str, shop_id: Optional[Union[str, int]] = None):
        """
        Entrypoint needed to access all [Printify APIs](https://developers.printify.com/)

        Args:
            api_token (str): Every instance of PrintiPy requires an API Token. Follow
            [these steps](https://help.printify.com/hc/en-us/articles/4483626447249-How-can-I-generate-an-API-token-)
            to generate a token
            shop_id (Optional[str]): The ID of a specific Printify shop. If none is given, some APIs will still
            work (as they do not require a Shop) while others will require a Shop ID to be passed upon a function call
        """
        self.shops = PrintiPyShop(api_token=api_token)
        self.catalog = PrintiPyCatalog(api_token=api_token)
        self.products = PrintiPyProducts(api_token=api_token, shop_id=shop_id)
        self.orders = PrintiPyOrders(api_token=api_token, shop_id=shop_id)
        self.artwork = PrintiPyArtwork(api_token=api_token)
        self.webhooks = PrintiPyWebhooks(api_token=api_token, shop_id=shop_id)
