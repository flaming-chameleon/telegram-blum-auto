from utils.core import create_sessions  # Import function to create pyrogram sessions
from utils.telegram import Accounts  # Import Accounts class to manage Telegram accounts
from utils.starter import start, stats  # Import functions to start the process and get statistics
import asyncio  # Import asyncio for asynchronous programming
from itertools import zip_longest  # Import zip_longest for pairing accounts with proxies
from utils.core import get_all_lines  # Import function to read all lines from a file
import os  # Import os for interacting with the operating system

async def main():
    # Print creator's information
    print("Soft created by: https://t.me/hidden_coding\n")
    
    # Get user input for selecting an action
    action = int(input("Select action:\n1. Start soft\n2. Create pyrogram sessions\n\n> "))

    # Create directories if they do not exist
    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')

    # Create pyrogram sessions
    if action == 2:
        await create_sessions()

    # # Get statistics
    # if action == 2:
    #     await stats()

    # Start the main process
    if action == 1:
        # Get accounts from the Accounts class
        accounts = await Accounts().get_accounts()
        # Read proxies from file
        proxys = get_all_lines("data/proxy.txt")

        tasks = []
        # Iterate over accounts and proxies, creating a task for each pair
        for thread, (account, proxy) in enumerate(zip_longest(accounts, proxys)):
            if not account: break  # Exit loop if no more accounts
            # Create and append the task to the tasks list
            tasks.append(asyncio.create_task(start(account=account, thread=thread, proxy=proxy)))

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    # Print application banner
    print("""
          

  _    _ _     _     _             _____          _      
 | |  | (_)   | |   | |           / ____|        | |     
 | |__| |_  __| | __| | ___ _ __ | |     ___   __| | ___ 
 |  __  | |/ _` |/ _` |/ _ \ '_ \| |    / _ \ / _` |/ _ \\
 | |  | | | (_| | (_| |  __/ | | | |___| (_) | (_| |  __/
 |_|  |_|_|\__,_|\__,_|\___|_| |_|\_____\___/ \__,_|\___|
                                                         
                    by Aero25x                                           
          
          """)
    
    # Run the main asynchronous function
    asyncio.get_event_loop().run_until_complete(main())
