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
from printipy.exceptions import PrintiPyException, PrintiPyParseException, InvalidScopeException, InvalidRequestException, \
    PrintifyException


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
            List of `printipy.api.Shop` objects

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
            List of `printipy.api.Blueprint` objects

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
            Blueprint `printipy.api.Blueprint` object

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
            List of `printipy.api.PrintProvider` objects

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
            Variant `printipy.api.PrintProviderVariants` object

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
            >>> shipping_information = api.catalog.get_shipping_info(blueprint.id, print_providers[0].id)

        Returns:
            Shipping information `printipy.api.ShippingInfo` object

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
            List of `printipy.api.PrintProvider` objects

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
            Print Provider `printipy.api.PrintProvider` object

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
        """
        TODO
        """
        _ApiHandlingMixin.__init__(self, api_token=api_token)
        _ShopIdMixin.__init__(self, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def get_products(self, shop_id: Union[str, int], max_pages: int = 1) -> List[Product]:
        """
        TODO
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
        TODO
        """
        # GET / v1 / shops / {shop_id} / products / {product_id}.json
        product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._get(product_url)
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def create_product(self, create_product: CreateProduct, shop_id: Union[str, int]) -> Product:
        """
        TODO
        """
        shop_id_to_use = self._get_shop_id(shop_id)
        # POST / v1 / shops / {shop_id} / products.json
        create_product_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/products.json'
        product_information = self._post(create_product_url, data=create_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def update_product(self, product_id: str, update_product: UpdateProduct, shop_id: Union[str, int]) -> Product:
        """
        TODO
        """
        # PUT / v1 / shops / {shop_id} / products / {product_id}.json
        update_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._put(update_product_url, data=update_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def delete_product(self, product_id: str, shop_id: Union[str, int]) -> True:
        """
        Examples:
            By pass in data pulled from `printipy.api.PrintiPyShop.get_shops`
            >>> from printipy.api import PrintiPy
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> products = api.products.get_products()
            >>> api.delete_product(products[0])

            By passing in specific shop information
            >>> from printipy.api import PrintiPy
            >>> from printipy.data_objects import Shop
            >>> api = PrintiPy(api_token='...', shop_id='...')
            >>> api.delete_shop(shop)


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
        TODO
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publish.json
        publish_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publish.json'
        self._post(publish_product_url, data=publish.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_success(self, product_id: str, publishing_succeeded: PublishingSucceeded,
                                      shop_id: Union[str, int]) -> True:
        """
        TODO
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_succeeded.json
        publishing_succeeded_url = f'{self.api_url}/v1/shops/{shop_id}/products/' \
                                   f'{product_id}/publishing_succeeded.json'
        self._post(publishing_succeeded_url, data=publishing_succeeded.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_failed(self, product_id: str, reason: str, shop_id: Union[str, int]) -> True:
        """
        TODO
        """
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_failed.json
        publishing_failed_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publishing_failed.json'
        self._post(publishing_failed_url, data={"reason": reason})
        return True

    @_ShopIdMixin._require_shop_id
    def unpublish_product(self, product_id: str, shop_id: Union[str, int]) -> True:
        """
        TODO
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
        TODO
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
        TODO
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
        TODO
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_simple_image_positioning(self, create_order: CreateOrderByExistingProduct,
                                                   shop_id: Union[str, int]) -> str:
        """
        TODO
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_advanced_image_positioning(self, create_order: CreateOrderByAdvancedImageProcessing,
                                                     shop_id: Union[str, int]) -> str:
        """
        TODO
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_print_details(self, create_order: CreateOrderByPrintDetails, shop_id: Union[str, int]) -> str:
        """
        TODO
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_sku(self, create_order: CreateOrderBySku, shop_id: Union[str, int]) -> str:
        """
        TODO
        """
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def send_order_to_production(self, order_id: str, shop_id: Union[str, int]) -> Order:
        """
        TODO
        """
        # POST / v1 / shops / {shop_id} / orders / {order_id} / send_to_production.json
        send_order_to_production_url = f'{self.api_url}/v1/shops/{shop_id}/orders/{order_id}/send_to_production.json'
        order_information = self._post(send_order_to_production_url)
        return self._parse(Order, order_information)

    @_ShopIdMixin._require_shop_id
    def calc_shipping_for_order(self, create_shipping_cost_estimate: CreateShippingEstimate,
                                shop_id: Union[str, int]) -> ShippingCost:
        """
        TODO
        """
        # POST / v1 / shops / {shop_id} / orders / shipping.json
        shipping_estimate_url = f'{self.api_url}/v1/shops/{shop_id}/orders/shipping.json'
        shipping_information = self._post(shipping_estimate_url, data=create_shipping_cost_estimate.to_dict())
        return self._parse(ShippingCost, shipping_information)

    @_ShopIdMixin._require_shop_id
    def cancel_order(self, order_id: str, shop_id: Union[str, int]) -> Order:
        """
        TODO
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
        TODO
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
        TODO
        """
        # GET / v1 / uploads / {image_id}.json
        artwork_url = f'{self.api_url}/v1/uploads/{image_id}.json'
        artwork_information = self._get(artwork_url)
        return self._parse(Artwork, artwork_information)

    def upload_artwork(self, filename: Optional[str] = None, url: Optional[str] = None) -> Artwork:
        """
        TODO
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
        TODO
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
        """
        TODO
        """
        _ApiHandlingMixin.__init__(self, api_token=api_token)
        _ShopIdMixin.__init__(self, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def get_webhooks(self, shop_id: Union[str, int]) -> List[Webhook]:
        """
        TODO
        """
        # / v1 / shops / {shop_id} / webhooks.json
        webhooks_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhooks_information = self._get(webhooks_url)
        return self._parse(Webhook, webhooks_information)

    @_ShopIdMixin._require_shop_id
    def create_webhook(self, create_webhook: CreateWebhook, shop_id: Union[str, int]) -> Webhook:
        """
        TODO
        """
        # POST /v1/shops/{shop_id}/webhooks.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhook_information = self._post(create_webhook_url, data=create_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def update_webhook(self, webhook_id: str, update_webhook: UpdateWebhook, shop_id: Union[str, int]) -> Webhook:
        """
        TODO
        """
        # PUT /v1/shops/{shop_id}/webhooks/{webhook_id}.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks/{webhook_id}.json'
        webhook_information = self._put(create_webhook_url, data=update_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def delete_webhook(self, webhook_id: str, shop_id: Union[str, int]) -> True:
        """
        TODO
        Raises:
            InvalidScopeException: If the API keys isn't permitted to perform this operation
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
            api_token (str): Every instance of PrintiPy requires an API Token. Follow [these steps](https://help.printify.com/hc/en-us/articles/4483626447249-How-can-I-generate-an-API-token-) to generate a token
            shop_id (Optional[str]): The ID of a specific Printify shop. If none is given, some APIs will still work (as they do not require a Shop) while others will require a Shop ID to be passed upon a function call
        """
        self.shops = PrintiPyShop(api_token=api_token)
        self.catalog = PrintiPyCatalog(api_token=api_token)
        self.products = PrintiPyProducts(api_token=api_token, shop_id=shop_id)
        self.orders = PrintiPyOrders(api_token=api_token, shop_id=shop_id)
        self.artwork = PrintiPyArtwork(api_token=api_token)
        self.webhooks = PrintiPyWebhooks(api_token=api_token, shop_id=shop_id)
