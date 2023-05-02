class PrintiPyException(Exception):
    """
    When a request doesn't meet the minimum needs to send/receive information with Printify. AKA, user error.

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> try:
        >>>   api.artwork.upload_artwork(...)
        >>> except PrintiPyException e:
        >>>   print(e)
    """
    pass


class PrintiPyParseException(PrintiPyException):
    """
    When unable to parse Printify's response into a PrintiPy. Please report these errors to the developer.

    Examples:
        >>> from printipy.api import PrintiPy
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> try:
        >>>   api.products.get_products()
        >>> except PrintiPyParseException e:
        >>>   print(e)
    """
    pass


class InvalidScopeException(Exception):
    """
    When the given API key isn't permitted to perform the operation.
    Use a different API key from Printify or update the permissions of the given key.

    Examples:
        >>> from printipy.api import PrintiPy
        >>> from printipy.data_objects import CreateProduct
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> new_product = CreateProduct(...)
        >>> try:
        >>>   created_product = api.products.create_product()
        >>> except InvalidScopeException e:
        >>>   print(e)
    """
    pass


class InvalidRequestException(Exception):
    """
    When Printify raised a 500 Server Error. Typically happens when the request contains incorrect data.

    Examples:
        >>> from printipy.api import PrintiPy
        >>> from printipy.data_objects import CreateProduct
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> new_product = CreateProduct(...)
        >>> try:
        >>>   created_product = api.products.create_product()
        >>> except InvalidRequestException e:
        >>>   print(e)
    """
    pass


class PrintifyException(Exception):
    """
    When Printify returns an error - usually contains information regarding malformed input

    Examples:
        >>> from printipy.api import PrintiPy
        >>> from printipy.data_objects import CreateProduct
        >>> api = PrintiPy(api_token='...', shop_id='...')
        >>> new_product = CreateProduct(...)
        >>> try:
        >>>   created_product = api.products.create_product()
        >>> except PrintifyException e:
        >>>   print(e)
    """
    pass
