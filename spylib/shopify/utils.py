from re import search


def domain_to_storename(domain: str) -> str:
    result = search(r'(https:\/\/)?([^.]+)\.myshopify\.com[\/]?', domain)
    if result:
        return result.group(2)

    raise ValueError(f'{domain} is not a shopify domain')
