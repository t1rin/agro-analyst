from datetime import datetime


def seconds_to_str(seconds: int, format: str = "%-d %B %H:%M") -> str:
    date_time = datetime.fromtimestamp(seconds)
    return date_time.strftime(format)
