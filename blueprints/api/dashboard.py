# RT.Blueprints.API - Dashboard

from __future__ import annotations

from functools import wraps
from urllib.parse import unquote

from backend.rt_module.src.setting import CommandData, CommandRunData
from backend import TypedSanic, Request, logger
from backend.utils import api, CoolDown, try_loads


data: dict[str, CommandData] = {}
def log(mode, msg, extend=""):
    return getattr(logger, mode)(f"[Dashboard{extend}] {msg}")
MANYERR = "リクエストしすぎです。| Too many requests."


def on_load(app: TypedSanic):
    async def update_dashboard_data(new_data: dict[CommandData]):
        global data
        data = new_data
        log("info", "Update", ".data")
    app.ctx.rtc.set_event(update_dashboard_data, "dashboard.update")


    def check_user(func):
        # 普通のAPIにつけるデコレータ, エイリアス
        @wraps(func)
        async def new(request, *args, **kwargs):
            if request.ctx.user:
                return await func(request, *args, **kwargs)
            else:
                return api("Error", None, 403)
        return new


    @app.get("/api/dashboard/get/datas/<guild_id:int>")
    @app.ctx.oauth.require_login(True)
    @CoolDown(3, 1, MANYERR)
    @check_user
    async def get_datas(_: Request, guild_id: int):
        "チャンネルのリストを取得します。"
        if guild := await app.ctx.rtc.request("get_guild", guild_id):
            return api("Ok", {
                "channels": {
                    channel["id"]: channel["name"]
                    for channel in guild["channels"]
                },
                "roles": {
                    role["id"]: role["name"]
                    for role in guild["roles"]
                },
                "members": {
                    member["id"]: member["name"]
                    for member in guild["members"]
                }
            })
        return api("Error", "Not Found", 404)


    @app.get("/api/dashboard/get/commands")
    @app.ctx.oauth.require_login(True)
    @CoolDown(3, 1, MANYERR)
    @check_user
    async def get_comands(request: Request):
        "ダッシュボードに表示するコマンドのデータを返す。"
        if data:
            return api("Ok", {
                "data": data, "guilds": {
                    guild["id"]: guild["name"]
                    for guild in await app.ctx.rtc.request(
                        "get_guilds", request.ctx.user.id
                    )
                }
            })
        else:
            return api("Error", None, 503)


    @app.post("/api/dashboard/post/<guild_id:int>/<channel_id:int>/<command_name>")
    @app.ctx.oauth.require_login(True)
    @CoolDown(3, 5, MANYERR)
    @check_user
    async def run_command(
        request: Request, guild_id: int, channel_id: int, command_name: str
    ):
        "コマンドを実行します。"
        return api(
            "Ok", await app.ctx.rtc.request(
                "dashboard.run", CommandRunData(
                    name=unquote(command_name), kwargs=try_loads(request), channel_id=channel_id,
                    guild_id=guild_id, user_id=request.ctx.user.id
                )
            )
        )

    @app.get("/api/dashboard/help/<command_name>")
    @app.ctx.oauth.require_login(True)
    @CoolDown(3, 1, MANYERR)
    @check_user
    async def get_help(request: Request, command_name: str):
        if data := await app.ctx.rtc.request("get_help", command_name):
            return api("Ok", data.get(
                await app.ctx.rtc.request("get_lang", request.ctx.user.id),
                data.get("ja", "E404iSsct7423J4")
            ))
