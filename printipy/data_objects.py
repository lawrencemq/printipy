from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any

from dataclasses_json import dataclass_json, config


def _exclude_if_none(value):
    return value is None


@dataclass_json
@dataclass
class Shop:
    """
    Shop object to store and validate shop data between Python and Printify
    """
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
