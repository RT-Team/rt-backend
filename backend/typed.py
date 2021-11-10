# RT.Backend - Typed

from typing import (
    TYPE_CHECKING, TypedDict, Callable, Coroutine, Union, Any, Dict, List
)
from types import SimpleNamespace

from sanic import Sanic, Blueprint, response
from discord.ext import commands
from jinja2 import Environment

from aiomysql import Pool

if TYPE_CHECKING:
    from .oauth import DiscordOAuth


class Datas(TypedDict):
    ShortURL: Dict[str, str]


class TypedContext(SimpleNamespace):
    pool: Pool
    bot: "TypedBot"
    env: Environment
    secret: dict
    datas: Datas
    tasks: List[Callable]
    oauth: "DiscordOAuth"

    def template(
        self, path: str, keys: dict = {}, **kwargs
    ) -> response.BaseHTTPResponse:
        ...


class TypedSanic(Sanic):
    ctx: TypedContext


class TypedBot(commands.Bot):
    app: TypedSanic
    pool: Pool


class TypedBlueprint(Blueprint):
    app: TypedSanic
    oauth: "DiscordOAuth"


PacketData = Union[dict, str]


class Packet(TypedDict):
    event_type: str
    data: PacketData


class Self(SimpleNamespace):
    app: TypedSanic
    bp: TypedBlueprint
    pool: Pool


CoroutineFunction = Callable[..., Coroutine[Any, Any, Any]]