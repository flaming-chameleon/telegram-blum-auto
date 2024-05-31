import argparse
import asyncio
import os
from itertools import zip_longest

from utils.core import create_sessions, get_all_lines, logger
from utils.starter import start
from utils.telegram import Accounts


async def main():
    print("Soft created by: https://t.me/hidden_coding\n")

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')
    action = parser.parse_args().action

    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    if not os.path.exists('statistics'):
        os.mkdir('statistics')

    if not action:
        action = int(input("Select action:\n1. Start soft\n2. Create pyrogram sessions\n\n> "))

    if action == 1:
        await create_sessions()

    if action == 2:
        try:
            accounts = await Accounts().get_accounts()

            proxys = get_all_lines("data/proxy.txt")

            tasks = []
            for thread, (account, proxy) in enumerate(zip_longest(accounts, proxys)):
                if not account: break  # Exit loop if no more accounts
                tasks.append(asyncio.create_task(start(account=account, thread=thread, proxy=proxy)))

            await asyncio.gather(*tasks)
        except ValueError:
            logger.error('No sessions, please add one by typing 2 in this CMD next start')


if __name__ == '__main__':
    print("""
          

  _    _ _     _     _             _____          _      
 | |  | (_)   | |   | |           / ____|        | |     
 | |__| |_  __| | __| | ___ _ __ | |     ___   __| | ___ 
 |  __  | |/ _` |/ _` |/ _ \ '_ \| |    / _ \ / _` |/ _ \\
 | |  | | | (_| | (_| |  __/ | | | |___| (_) | (_| |  __/
 |_|  |_|_|\__,_|\__,_|\___|_| |_|\_____\___/ \__,_|\___|
                                                         
                    by Aero25x                                           
          
          """)
    asyncio.get_event_loop().run_until_complete(main())
