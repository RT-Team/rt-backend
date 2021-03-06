# RT.Backend - Typed

from typing import (
    TYPE_CHECKING, TypedDict, Callable, Coroutine, Literal,
    Optional, Union, Any, Dict, List
)
from types import SimpleNamespace

from sanic import Sanic, Blueprint, response
from sanic.request import Request
from discord.ext import commands
from miko import Manager

from aiomysql import Pool

if TYPE_CHECKING:
    from .oauth import DiscordOAuth
    from .rtws import RTWebSocket


class Datas(TypedDict):
    ShortURL: Dict[str, str]


class DiscordObjectData(TypedDict):
    name: str
    id: int
ChannelData = type("ChannelData", (DiscordObjectData,), {})


class GuildData(TypedDict):
    text_channels: List[DiscordObjectData]
    voice_channels: List[DiscordObjectData]
    channels: List[DiscordObjectData]
    icon_url: str


class TypedContext(SimpleNamespace):
    pool: Pool
    bot: "TypedBot"
    env: Manager
    secret: dict
    datas: Datas
    tasks: List[Callable]
    oauth: "DiscordOAuth"
    languages: Dict[int, str]
    rtws: "RTWebSocket"

    def template(
        self, path: str, keys: dict = {}, **kwargs
    ) -> response.BaseHTTPResponse:
        ...

    def get_language(self, user_id: int) -> str:
        ...

    async def fetch_guilds(
        self, user_id: int
    ) -> Optional[List[GuildData]]:
        ...


class TypedSanic(Sanic):
    ctx: TypedContext


class TypedRequest(Request):
    app: TypedSanic


class TypedBot(commands.Bot):
    app: TypedSanic
    pool: Pool

    async def close(self) -> None:
        self.dispatch("close")
        return await super().close()


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