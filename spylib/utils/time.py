import pytz

from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)


def now_epoch() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def now_epoch_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def make_time_aware(dtime):
    return dtime.replace(tzinfo=pytz.utc)


def sh_to_dt_time(shtime):
    if ":" == shtime[-3:-2]:
        shtime = shtime[:-3] + shtime[-2:]
    try:
        result = datetime.strptime(shtime, "%Y-%m-%dT%H:%M:%S%z")
    except Exception:
        result = shtime
    return result
