from asyncio import sleep
from random import uniform

import aiohttp
from aiocfscrape import CloudflareScraper
from fake_useragent import UserAgent

from data import config
from utils.blum import BlumBot
from utils.core import logger
from utils.helper import format_duration


async def start(thread: int, account: str, proxy: [str, None]):
    while True:
        async with CloudflareScraper(headers={'User-Agent': UserAgent(os='android').random},
                                     timeout=aiohttp.ClientTimeout(total=60)) as session:
            try:
                blum = BlumBot(account=account, thread=thread, session=session, proxy=proxy)
                max_try = 2

                await sleep(uniform(*config.DELAYS['ACCOUNT']))
                await blum.login()

                while True:
                    try:
                        msg = await blum.claim_daily_reward()
                        if isinstance(msg, bool) and msg:
                            logger.success(f"{account} | Claimed daily reward!")

                        timestamp, start_time, end_time, play_passes = await blum.balance()

                        claim_amount, is_available = await blum.friend_balance()
                        # logger.info(f"{account} | {claim_amount} | {is_available}")
                        if claim_amount != 0 and is_available:
                            amount = await blum.friend_claim()
                            logger.success(f"{account} | Claimed friend ref reward {amount}")

                        if config.PLAY_GAMES is False:
                            play_passes = 0
                        elif play_passes and play_passes > 0 and config.PLAY_GAMES is True:
                            await blum.play_game(play_passes)

                        await sleep(uniform(3, 10))

                        try:
                            timestamp, start_time, end_time, play_passes = await blum.balance()
                            if start_time is None and end_time is None and max_try > 0:
                                await blum.start()
                                logger.info(f"{account} | Start farming!")
                                max_try -= 1

                            elif start_time is not None and end_time is not None and timestamp is not None and timestamp >= end_time and max_try > 0:
                                await blum.refresh()
                                timestamp, balance = await blum.claim()
                                logger.success(f"{account} | Claimed reward! Balance: {balance}")
                                max_try -= 1

                            elif end_time is not None and timestamp is not None:
                                sleep_duration = end_time - timestamp
                                logger.info(f"{account} | Sleep {format_duration(sleep_duration)}")
                                max_try += 1
                                await sleep(sleep_duration)
                                await blum.refresh()

                            elif max_try == 0:
                                break

                        except Exception as e:
                            logger.error(f"{account} | Error in farming management: {e}")

                        await sleep(10)
                    except Exception as e:
                        logger.error(f"{account} | Error: {e}")
            except Exception as outer_e:
                logger.error(f"{account} | Session error: {outer_e}")
            finally:
                logger.info(f"{account} | Reconnecting, 61 s")
                await sleep(61)


async def stats():
    logger.success("Analytics disabled")
