import base64
import json
import os
from copy import deepcopy
from json import JSONDecodeError
from typing import List, Optional, Dict, Union, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config

import requests
from requests import Response


def _exclude_if_none(value):
    return value is None


@dataclass_json
@dataclass
class Shop:
    id: str
    title: str
    sales_channel: str


@dataclass_json
@dataclass
class Blueprint:
    id: int
    title: str
    description: str
    brand: str
    model: str
    images: List[str]


@dataclass_json
@dataclass
class Location:
    address1: str
    city: str
    country: str
    region: str
    zip: str
    address2: Optional[str] = field(default=None)


@dataclass_json
@dataclass
class Address:
    first_name: str
    last_name: str
    address1: str
    city: str
    country: str
    region: str
    zip: str
    address2: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    phone: Optional[str] = field(default=None)
    company: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


@dataclass_json
@dataclass
class PrintProvider:
    id: int
    title: str
    location: Optional[Location] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


@dataclass_json
@dataclass
class VariantOption:
    color: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    size: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    paper: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    quantity: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


@dataclass_json
@dataclass
class VariantPlaceholder:
    position: str
    height: int
    width: int


@dataclass_json
@dataclass
class Variant:
    id: int
    title: str
    options: VariantOption
    placeholders: List[VariantPlaceholder]


@dataclass_json
@dataclass
class PrintProviderVariants:
    id: int
    title: str
    variants: List[Variant]

    def get_variant_ids(self):
        return [x.id for x in self.variants]


@dataclass_json
@dataclass
class ShippingInfoHandlingTime:
    value: int
    unit: str


@dataclass_json
@dataclass
class ShippingInfoProfileCost:
    cost: int
    currency: str


@dataclass_json
@dataclass
class ShippingInfoProfile:
    variant_ids: List[int]
    first_item: ShippingInfoProfileCost
    additional_items: ShippingInfoProfileCost
    countries: List[str]


@dataclass_json
@dataclass
class ShippingInfo:
    handling_time: ShippingInfoHandlingTime
    profiles: List[ShippingInfoProfile]


@dataclass_json
@dataclass
class ShippingCost:
    standard: int
    express: int


@dataclass_json
@dataclass
class ShippingEstimateLineItemByProduct:
    product_id: str
    variant_id: int
    quantity: int


@dataclass_json
@dataclass
class ShippingEstimateLineItemByVariant:
    print_provider_id: int
    blueprint_id: int
    variant_id: int
    quantity: int


@dataclass_json
@dataclass
class ShippingEstimateLineItemBySku:
    sku: str
    quantity: int


@dataclass_json
@dataclass
class CreateShippingEstimate:
    line_items: List[
        Union[ShippingEstimateLineItemByProduct, ShippingEstimateLineItemByVariant, ShippingEstimateLineItemBySku]]
    address_to: Address


@dataclass_json
@dataclass
class ProductOptionValue:
    id: str
    title: str


@dataclass_json
@dataclass
class ProductOption:
    name: str
    type: str
    values: List[ProductOptionValue]


@dataclass_json
@dataclass
class ProductVariant:
    id: int
    price: int
    is_enabled: bool
    sku: Optional[str] = None
    cost: Optional[int] = None
    title: Optional[str] = None
    grams: Optional[int] = None
    is_default: Optional[bool] = None
    is_available: Optional[bool] = None
    options: Optional[List[int]] = None
    quantity: Optional[int] = None


@dataclass_json
@dataclass
class ProductImage:
    src: str
    variant_ids: List[int]
    position: str
    is_default: bool
    is_selected_for_publishing: Optional[bool] = None


@dataclass_json
@dataclass
class PrintAreaInfo:
    x: float
    y: float
    scale: float
    angle: float


@dataclass_json
@dataclass
class PlaceholderImage(PrintAreaInfo):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


@dataclass_json
@dataclass
class ProductPlaceholder:
    position: str
    images: List[PlaceholderImage]


@dataclass_json
@dataclass
class ProductPrintArea:
    variant_ids: List[int]
    placeholders: List[ProductPlaceholder]
    background: Optional[str] = None


@dataclass_json
@dataclass
class ProductExternal:
    id: str
    handle: str
    shipping_template_id: Optional[str] = None
    channel: Optional[str] = None


@dataclass_json
@dataclass
class Product:
    id: str
    title: str
    description: str
    tags: List[str]
    options: List[ProductOption]
    variants: List[ProductVariant]
    images: List[ProductImage]
    created_at: str
    updated_at: str
    visible: bool
    is_locked: bool
    blueprint_id: int
    user_id: int
    shop_id: int
    print_provider_id: int
    print_areas: List[ProductPrintArea]
    # sales_channel_properties: List
    # print_details: List
    twodaydelivery_enabled: Optional[bool] = None
    external: Optional[ProductExternal] = None


@dataclass_json
@dataclass
class Publish:
    title: bool = True
    description: bool = True
    images: bool = True
    variants: bool = True
    tags: bool = True
    keyFeatures: bool = True
    shipping_template: bool = True


@dataclass_json
@dataclass
class PublishingSucceededExternal:
    id: str
    handle: str


@dataclass_json
@dataclass
class PublishingSucceeded:
    external: PublishingSucceededExternal


@dataclass_json
@dataclass
class LineItem:
    product_id: str
    quantity: int
    variant_id: int
    print_provider_id: int
    cost: int
    shipping_cost: int
    status: str
    metadata: Dict
    sent_to_production_at: Optional[str] = None
    fulfilled_at: Optional[str] = None


@dataclass_json
@dataclass
class Shipment:
    carrier: str
    number: str
    url: str
    delivered_at: str


@dataclass_json
@dataclass
class Order:
    id: str
    address_to: Address
    line_items: List[LineItem]
    metadata: Dict
    total_price: int
    total_shipping: int
    total_tax: int
    status: str
    shipping_method: int
    created_at: str
    sent_to_production_at: Optional[str] = None
    shipments: Optional[List[Shipment]] = None
    fulfilled_at: Optional[str] = None
    fulfilment_type: Optional[str] = None


@dataclass_json
@dataclass
class __CreateOrderLineItemBase:
    variant_id: int
    quantity: int


@dataclass_json
@dataclass
class CreateOrderLineItem(__CreateOrderLineItemBase):
    product_id: str


@dataclass_json
@dataclass
class _CreateOrder:
    pass


@dataclass_json
@dataclass
class CreateOrderExistingProduct(_CreateOrder):
    external_id: str
    label: str
    line_items: List[CreateOrderLineItem]
    shipping_method: int
    send_shipping_notification: bool
    address_to: Address


@dataclass_json
@dataclass
class CreateOrderLineItemSimpleProcessing(__CreateOrderLineItemBase):
    print_provider_id: int
    blueprint_id: int
    print_areas: Dict[str, Any]


@dataclass_json
@dataclass
class CreateOrderSimpleImageProcessing(CreateOrderExistingProduct):
    external_id: str
    label: str
    line_items: List[CreateOrderLineItemSimpleProcessing]
    shipping_method: int
    send_shipping_notification: bool
    address_to: Address


@dataclass_json
@dataclass
class CreateOrderLineItemAdvancedProcessingPrintAreaInfo(PrintAreaInfo):
    src: str


@dataclass_json
@dataclass
class CreateOrderLineItemAdvancedProcessing(__CreateOrderLineItemBase):
    blueprint_id: int
    print_provider_id: int
    print_areas: Dict[str, List[PrintAreaInfo]]


@dataclass_json
@dataclass
class CreateOrderAdvancedImageProcessing(_CreateOrder):
    external_id: str
    label: str
    line_items: List[CreateOrderLineItemAdvancedProcessing]
    shipping_method: int
    send_shipping_notification: bool
    address_to: Address


@dataclass_json
@dataclass
class CreateOrderLineItemPrintDetails(CreateOrderLineItemSimpleProcessing):
    print_details: Dict[str, Any]


@dataclass_json
@dataclass
class CreateOrderPrintDetails(_CreateOrder):
    external_id: str
    label: str
    line_items = List[CreateOrderLineItemPrintDetails]
    shipping_method: int
    send_shipping_notification: bool
    address_to: Address


@dataclass_json
@dataclass
class CreateOrderLineItemSku:
    sku: str
    quantity: int


@dataclass_json
@dataclass
class CreateOrderSku(_CreateOrder):
    external_id: str
    label: str
    line_items = List[CreateOrderLineItemSku]
    shipping_method: int
    send_shipping_notification: bool
    address_to: Address


@dataclass_json
@dataclass
class Artwork:
    id: str
    file_name: str
    height: int
    width: int
    size: int
    mime_type: str
    preview_url: str
    upload_time: str


@dataclass_json
@dataclass
class Webhook:
    id: str
    shop_id: str
    url: str
    topic: str


@dataclass_json
@dataclass
class CreateWebhook:
    url: str
    topic: str


@dataclass_json
@dataclass
class UpdateWebhook:
    url: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    topic: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


@dataclass_json
@dataclass
class CreateProductPrintAreaPlaceholderImage(PrintAreaInfo):
    id: str


@dataclass_json
@dataclass
class CreateProductPrintAreaPlaceholder:
    position: str
    images: List[CreateProductPrintAreaPlaceholderImage]


@dataclass_json
@dataclass
class CreateProductPrintArea:
    variant_ids: List[int]
    placeholders: List[CreateProductPrintAreaPlaceholder]


@dataclass_json
@dataclass
class CreateProductVariant:
    id: int
    price: int
    is_enabled: bool


@dataclass_json
@dataclass
class CreateProduct:
    title: str
    description: str
    blueprint_id: int
    print_provider_id: int
    variants: List[CreateProductVariant]
    print_areas: List[CreateProductPrintArea]

    def add_variant(self, variant: CreateProductVariant):
        self.variants.append(variant)

    def add_print_area(self, print_area: CreateProductPrintArea):
        self.print_areas.append(print_area)


@dataclass_json
@dataclass
class UpdateProductExternal:
    id: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    handle: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    shipping_template_id: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


@dataclass_json
@dataclass
class UpdateProduct:
    title: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    description: Optional[str] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    blueprint_id: Optional[int] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    print_provider_id: Optional[int] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    variants: Optional[List[CreateProductVariant]] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    print_areas: Optional[List[CreateProductPrintArea]] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )
    external: Optional[UpdateProductExternal] = field(
        default=None, metadata=config(exclude=_exclude_if_none)
    )


class PrintiPyException(Exception):
    pass


class ParseException(PrintiPyException):
    pass


class InvalidScopeException(Exception):
    pass


class InvalidRequestException(Exception):
    pass


class PrintifyException(Exception):
    pass


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
            raise PrintiPyException(message)
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
            raise ParseException('Unable to parse response: was not a list or object')

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
            >>> api.get_shops()

        Returns:
            List of `printipy.api.Shop` objects

        Raises:
            ParseException: If unable to parse Printify's response
            PrintiPyException: If the request failed to validate with Printify's schema - usually contains information regarding malformed input
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
            >>> shops = api.get_shops()
            >>> api.delete_shop(shops[0])

            By passing in specific shop information
            >>> from printipy.api import Shop
            >>> shop = Shop(id='...', title='...', sales_channel='...')
            >>> api.delete_shop(shop)

        Args:
            shop (Shop): A Shop to delete. Pull all shops using :func:`get_shops <printipy.api.PrintiPyShop.get_shops>`
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
        blueprint_url = f'{self.api_url}/v1/catalog/blueprints.json'
        blueprint_information = self._get(blueprint_url)
        return self._parse(Blueprint, blueprint_information)

    def get_blueprint(self, blueprint_id: Union[str, int]) -> Optional[Blueprint]:
        # GET / v1 / catalog / blueprints / {blueprint_id}.json
        blueprint_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}.json'
        blueprint_information = self._get(blueprint_url)
        return self._parse(Blueprint, blueprint_information)

    def get_print_providers_for_blueprint(self, blueprint_id: Union[str, int]) -> List[PrintProvider]:
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers.json
        print_providers_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/print_providers.json'
        print_provider_information = self._get(print_providers_url)
        return self._parse(PrintProvider, print_provider_information)

    def get_variants(self, blueprint_id: Union[str, int], print_provider_id: Union[str, int]) -> PrintProviderVariants:
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers / {print_provider_id} / variants.json
        variants_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/' \
                       f'print_providers/{print_provider_id}/variants.json'
        variant_information = self._get(variants_url)
        return self._parse(PrintProviderVariants, variant_information)

    def get_shipping_info(self, blueprint_id: Union[str, int], print_provider_id: Union[str, int]) -> ShippingInfo:
        # GET / v1 / catalog / blueprints / {blueprint_id} / print_providers / {print_provider_id} / shipping.json
        shipping_url = f'{self.api_url}/v1/catalog/blueprints/{blueprint_id}/' \
                       f'print_providers/{print_provider_id}/shipping.json'
        shipping_information = self._get(shipping_url)
        return self._parse(ShippingInfo, shipping_information)

    def get_print_providers(self) -> List[PrintProvider]:
        # GET / v1 / catalog / print_providers.json
        print_providers_url = f'{self.api_url}/v1/catalog/print_providers.json'
        print_provider_information = self._get(print_providers_url)
        return self._parse(PrintProvider, print_provider_information)

    def get_print_provider(self, print_provider_id: Union[str, int]) -> Optional[PrintProvider]:
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
    def get_product(self, product_id: str, shop_id: Union[str, int]) -> Optional[Product]:
        # GET / v1 / shops / {shop_id} / products / {product_id}.json
        product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._get(product_url)
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def create_product(self, create_product: CreateProduct, shop_id: Union[str, int]) -> Product:
        shop_id_to_use = self._get_shop_id(shop_id)
        # POST / v1 / shops / {shop_id} / products.json
        create_product_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/products.json'
        product_information = self._post(create_product_url, data=create_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def update_product(self, product_id: str, update_product: UpdateProduct, shop_id: Union[str, int]) -> Product:
        # PUT / v1 / shops / {shop_id} / products / {product_id}.json
        update_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        product_information = self._put(update_product_url, data=update_product.to_dict())
        return self._parse(Product, product_information)

    @_ShopIdMixin._require_shop_id
    def delete_product(self, product_id: str, shop_id: Union[str, int]) -> True:
        # DELETE / v1 / shops / {shop_id} / products / {product_id}.json
        delete_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}.json'
        self._delete(delete_product_url)
        return True

    @_ShopIdMixin._require_shop_id
    def publish_product(self, product_id: str, publish: Publish, shop_id: Union[str, int]) -> True:
        # POST / v1 / shops / {shop_id} / products / {product_id} / publish.json
        publish_product_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publish.json'
        self._post(publish_product_url, data=publish.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_success(self, product_id: str, publishing_succeeded: PublishingSucceeded,
                                      shop_id: Union[str, int]) -> True:
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_succeeded.json
        publishing_succeeded_url = f'{self.api_url}/v1/shops/{shop_id}/products/' \
                                   f'{product_id}/publishing_succeeded.json'
        self._post(publishing_succeeded_url, data=publishing_succeeded.to_dict())
        return True

    @_ShopIdMixin._require_shop_id
    def set_product_published_failed(self, product_id: str, reason: str, shop_id: Union[str, int]) -> True:
        # POST / v1 / shops / {shop_id} / products / {product_id} / publishing_failed.json
        publishing_failed_url = f'{self.api_url}/v1/shops/{shop_id}/products/{product_id}/publishing_failed.json'
        self._post(publishing_failed_url, data={"reason": reason})
        return True

    @_ShopIdMixin._require_shop_id
    def unpublish_product(self, product_id: str, shop_id: Union[str, int]) -> True:
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
        shop_id_to_use = self._get_shop_id(shop_id)
        # GET / v1 / shops / {shop_id} / orders / {order_id}.json
        order_url = f'{self.api_url}/v1/shops/{shop_id_to_use}/orders/{order_id}.json'
        order_information = self._get(order_url)
        return self._parse(Order, order_information)

    def __create_order(self, create_order: _CreateOrder, shop_id: Union[str, int]) -> str:
        # POST / v1 / shops / {shop_id} / orders.json
        create_order_url = f'{self.api_url}/v1/shops/{shop_id}/orders.json'
        order_information = self._post(create_order_url, data=create_order.to_dict())
        return order_information['id']

    @_ShopIdMixin._require_shop_id
    def create_order_for_existing_product(self, create_order: CreateOrderExistingProduct,
                                          shop_id: Union[str, int]) -> str:
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_simple_image_positioning(self, create_order: CreateOrderExistingProduct,
                                                   shop_id: Union[str, int]) -> str:
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_advanced_image_positioning(self, create_order: CreateOrderAdvancedImageProcessing,
                                                     shop_id: Union[str, int]) -> str:
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_print_details(self, create_order: CreateOrderPrintDetails, shop_id: Union[str, int]) -> str:
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def create_order_with_sku(self, create_order: CreateOrderSku, shop_id: Union[str, int]) -> str:
        return self.__create_order(create_order, shop_id=shop_id)

    @_ShopIdMixin._require_shop_id
    def send_order_to_production(self, order_id: str, shop_id: Union[str, int]) -> Order:
        # POST / v1 / shops / {shop_id} / orders / {order_id} / send_to_production.json
        send_order_to_production_url = f'{self.api_url}/v1/shops/{shop_id}/orders/{order_id}/send_to_production.json'
        order_information = self._post(send_order_to_production_url)
        return self._parse(Order, order_information)

    @_ShopIdMixin._require_shop_id
    def calc_shipping_for_order(self, create_shipping_cost_estimate: CreateShippingEstimate,
                                shop_id: Union[str, int]) -> ShippingCost:
        # POST / v1 / shops / {shop_id} / orders / shipping.json
        shipping_estimate_url = f'{self.api_url}/v1/shops/{shop_id}/orders/shipping.json'
        shipping_information = self._post(shipping_estimate_url, data=create_shipping_cost_estimate.to_dict())
        return self._parse(ShippingCost, shipping_information)

    @_ShopIdMixin._require_shop_id
    def cancel_order(self, order_id: str, shop_id: Union[str, int]) -> Order:
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
        # GET / v1 / uploads / {image_id}.json
        artwork_url = f'{self.api_url}/v1/uploads/{image_id}.json'
        artwork_information = self._get(artwork_url)
        return self._parse(Artwork, artwork_information)

    def upload_artwork(self, filename: Optional[str] = None, url: Optional[str] = None) -> Artwork:
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
        # / v1 / shops / {shop_id} / webhooks.json
        webhooks_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhooks_information = self._get(webhooks_url)
        return self._parse(Webhook, webhooks_information)

    @_ShopIdMixin._require_shop_id
    def create_webhook(self, create_webhook: CreateWebhook, shop_id: Union[str, int]) -> Webhook:
        # POST /v1/shops/{shop_id}/webhooks.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks.json'
        webhook_information = self._post(create_webhook_url, data=create_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def update_webhook(self, webhook_id: str, update_webhook: UpdateWebhook, shop_id: Union[str, int]) -> Webhook:
        # PUT /v1/shops/{shop_id}/webhooks/{webhook_id}.json
        create_webhook_url = f'{self.api_url}/v1/shops/{shop_id}/webhooks/{webhook_id}.json'
        webhook_information = self._put(create_webhook_url, data=update_webhook.to_dict())
        return self._parse(Webhook, webhook_information)

    @_ShopIdMixin._require_shop_id
    def delete_webhook(self, webhook_id: str, shop_id: Union[str, int]) -> True:
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
