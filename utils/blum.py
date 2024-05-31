import asyncio
import random
from urllib.parse import unquote

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from data import config
from utils.core import logger


class BlumBot:
    def __init__(self, thread, account, session, proxy):
        """
        Initialize the BlumBot with thread id, account name, and optional proxy.
        """
        self.proxy = f"http://{proxy}" if proxy is not None else None
        self.thread = thread

        if proxy:
            proxy = {
                "scheme": "http",
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(name=account, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR,
                             proxy=proxy)
        self.session = session
        self.refresh_token = ''

    async def play_game(self, play_passes: int):
        """
        Play the game a specified number of times using available play passes.
        """
        while play_passes:
            await asyncio.sleep(random.uniform(*config.DELAYS['PLAY']))
            game_id = await self.start_game()

            if not game_id or game_id == "cannot start game":
                logger.info(f"{self.client.name} | Couldn't start play in game! play_passes: {play_passes}")
                break

            await asyncio.sleep(random.uniform(30, 40))

            msg, points = await self.claim_game(game_id)
            if isinstance(msg, bool) and msg:
                logger.info(f"{self.client.name} | Finish play in game!; reward: {points}")
            else:
                logger.info(f"{self.client.name} | Couldn't play game; msg: {msg} play_passes: {play_passes}")
                break

            await asyncio.sleep(random.uniform(30, 40))

            play_passes -= 1

    async def claim_daily_reward(self):
        """
        Claim the daily reward.
        """
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/daily-reward?offset=-180",
                                       proxy=self.proxy)
        txt = await resp.text()
        await asyncio.sleep(1)
        return True if txt == 'OK' else txt

    async def refresh(self):
        """
        Refresh the authorization token.
        """
        json_data = {'refresh': self.refresh_token}
        resp = await self.session.post("https://gateway.blum.codes/v1/auth/refresh", json=json_data, proxy=self.proxy)
        resp_json = await resp.json()

        self.session.headers['Authorization'] = "Bearer " + resp_json.get('access')
        self.refresh_token = resp_json.get('refresh')

    async def start_game(self):
        """
        Start a new game and return the game ID.
        """
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/play", proxy=self.proxy)
        response_data = await resp.json()
        if "gameId" in response_data:
            return response_data.get("gameId")
        elif "message" in response_data:
            return response_data.get("message")

    async def claim_game(self, game_id: str):
        """
        Claim the reward for a completed game.
        """
        points = random.randint(*config.POINTS)
        json_data = {"gameId": game_id, "points": points}

        resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/claim", json=json_data,
                                       proxy=self.proxy)
        if resp.status != 200:
            await asyncio.sleep(1)
            resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/claim", json=json_data,
                                           proxy=self.proxy)

        txt = await resp.text()

        return True if txt == 'OK' else txt, points

    async def claim(self):
        """
        Claim the farming rewards.
        """
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/claim", proxy=self.proxy)
        if resp.status != 200:
            await asyncio.sleep(1)
            resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/claim", proxy=self.proxy)

        resp_json = await resp.json()

        return int(resp_json.get("timestamp") / 1000), resp_json.get("availableBalance")

    async def start(self):
        """
        Start the farming process.
        """
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/start", proxy=self.proxy)

        if resp.status != 200:
            await asyncio.sleep(1)
            resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/start", proxy=self.proxy)

    async def balance(self):
        """
        Get the current balance and farming status.
        """
        resp = await self.session.get("https://game-domain.blum.codes/api/v1/user/balance", proxy=self.proxy)
        resp_json = await resp.json()
        await asyncio.sleep(1)

        timestamp = resp_json.get("timestamp")
        play_passes = resp_json.get("playPasses")

        start_time = None
        end_time = None
        if resp_json.get("farming"):
            start_time = resp_json["farming"].get("startTime")
            end_time = resp_json["farming"].get("endTime")

        return (int(timestamp / 1000) if timestamp is not None else None,
                int(start_time / 1000) if start_time is not None else None,
                int(end_time / 1000) if end_time is not None else None,
                play_passes)

    async def login(self):

        """
        Login to the game using Telegram mini app authentication.
        """
        try:
            json_data = {"query": await self.get_tg_web_data()}

            resp = await self.session.post("https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP",
                                           json=json_data, proxy=self.proxy)
            resp_json = await resp.json()

            self.session.headers['Authorization'] = "Bearer " + resp_json.get("token").get("access")
            self.refresh_token = resp_json.get("token").get("refresh")
            return True
        except:
            return False

    async def get_tg_web_data(self):
        """
        Get the Telegram web data needed for login.
        """
        await self.client.connect()

        web_view = await self.client.invoke(RequestWebView(
            peer=await self.client.resolve_peer('BlumCryptoBot'),
            bot=await self.client.resolve_peer('BlumCryptoBot'),
            platform='android',
            from_bot_menu=False,
            url='https://telegram.blum.codes/'
        ))

        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
