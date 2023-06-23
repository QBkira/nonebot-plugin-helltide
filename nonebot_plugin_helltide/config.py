from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    url_api: str = "https://d4armory.io/api/events/recent"
    event_check_interval: int = 1 # minutes
