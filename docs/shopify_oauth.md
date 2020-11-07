# Shopify Oauth

SPyLib provides a FastAPI router handling the [Shopify OAuth flow] used to authenticate Shopify
embedded apps in Shopify stores.

## API

All the elements and endpoints required for the Outh process are provided by a router initialized
by this function:

::: spylib.shopify.oauth.init_oauth_router
    :docstring:

The router has two endpoints:

* The installation initialization takes a query argument shop that corresponds to the Shopify store's
  domain such as `mystore.yshopify.com`. The default relative endpoint can be modified.
* The callback endpoint is directly called by Shopify during the OAuth process. The default relative
  endpoint can be modified. The full URL of this callback must be whitelisted in the app settings
  in the partners portal.

## Example

### OAuth router

```Python hl_lines="32 42"
{!./code/shopify_oauth.py!}
```

### Post installation processing

```Python hl_lines="11 37"
{!./code/shopify_oauth.py!}
```

    """Function processing and storing the offline token provided right after the app was installed
    on the Shopify store"""
    # Store the offline token in your database

    # Perform any post install processing here

### Post login processing
```Python hl_lines="23 38"
{!./code/shopify_oauth.py!}
```

    """Function processing and storing the online token provided right after a user started to use
    the app and is effectively logged in"""
    # Retrieve data of the store
    # Perform any post login processing here
    # Return the JWT used to authenticate calls from the frontend
