from shortuuid import ShortUUID


def get_unique_id() -> str:
    return ShortUUID().random(length=10)
