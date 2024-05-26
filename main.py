from utils.core import create_sessions
from utils.telegram import Accounts
from utils.starter import start, stats
import asyncio
from itertools import zip_longest
from utils.core import get_all_lines
import os


async def main():
    print("Soft created by: https://t.me/hidden_coding\n")
    action = int(input("Select action:\n1. Start soft\n2. Get statistics\n3. Create pyrogram sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')

    if action == 3:
        await create_sessions()

    if action == 2:
        await stats()

    if action == 1:
        accounts = await Accounts().get_accounts()
        proxys = get_all_lines("data/proxy.txt")

        tasks = []
        for thread, (account, proxy) in enumerate(zip_longest(accounts, proxys)):
            if not account: break
            tasks.append(asyncio.create_task(start(account=account, thread=thread, proxy=proxy)))

        await asyncio.gather(*tasks)


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
