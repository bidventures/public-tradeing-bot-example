import json
import sys
sys.path.append("../jockmktbot/")
from bots import Bot
import time
import random
import argparse

def initBots(num, events):
    """
    Returns a list of initialized Bot instances
    """
    # with open('/home/ubuntu/bots/jockmktbot/accounts.json') as f:
    # with open('accounts.json') as f:
        # data = json.load(f)
    bots = []
    while num > 0:
        #generate account
        i = str(random.randint(0, 1000))
        # if i not in data['accounts']:
        # data['accounts'][i] = generate_account(i)
        # acc = data['accounts'][i]
        acc = generate_account(i)
        account = (acc['email'], acc['password'], (acc['name']['first'], acc['name']['last']), acc['username']) 
        params = acc['params']
        
        #generate bot
        bot = Bot(params = params, account = account, events = events)

        #if bot is already in-use, check if it has joined events not in events
        try:
            append = True
            for event in bot.fetchUserEvents():
                if events and event['event']['id'] not in events and event['event']['status'] != 'CONTEST_PAID':
                    append = False
                    break
            if append:
                bots.append(bot)
                num -= 1
        except:
            bots.append(bot)
            num -= 1
    return bots

def runBots(bots):
    """
    Main function to run the bots
    """
    while bots:
        random.shuffle(bots)
        delete = []
        for bot in bots:
            try:
                bot.run()
                r = {i['event']['status'] for i in bot.fetchUserEvents() if i['event'] and i['event']['status']}
                if r == {'CONTEST_PAID'} or not r:
                    print(f'{bot.username} is not in any scheduled or live events and will no longer be active')
                    delete.append(bot)
            except Exception as e:
                print(f'Error {e} running bot {bot.username}')
                continue
        for i in delete:
            bots.remove(i)

def checkBalances(bots):
    """
    Prints balances for each bot
    """
    for i in range(len(bots)):
        print(f"bot {i} has balance {bots[i].fetchBalances()}")

def checkBotEvents(bots):
    """
    Prints rankings for each bot's events
    """
    eventIDs = set()
    for i in range(len(bots)):
        events = bots[i].fetchAccountEvents()['user_events']
        print(f'Bot {i} results')
        for e in events:
            print(f'{e["event"]["name"]} : rank {e.get("contest_position")}, final balance {e.get("contest_balance")}, earnings {e.get("contest_prize_amount")}')
            eventIDs.add(e['event']['id'])

def generate_account(i):
    first, last = 'first', 'last'
    username = f'userbot_{i}'
    password = f'{username}P@ssword1'
    email = f'{username}_bot@jockmkt.com'
    params = {
    "maxIPOSpending": random.randint(200, 250), 
    "sellRisk": random.random(),
    "buyRisk": random.random(),
    "IPOcsv": False if random.random() > 0.5 else True,
    "LIVEcsv": False if random.random() > 0.5 else True
    }
    res = {
      "email": email,
      "password": password,
      "name": { "first": first, "last": last},
      "username": username,
      "params": params
    }
    return res

if __name__== "__main__":
    parser = argparse.ArgumentParser(description = 'Runs bots in events')
    parser.add_argument('num', metavar='num_bots', type = int, nargs = 1, help = 'Number of bots to run')
    parser.add_argument('events', metavar='events', nargs='*', help='Events to run bots on, or None for all events')
    args = parser.parse_args()

    num, events = args.num[0], args.events
    confirm = f'{num} bots will run on event(s): {events}' if events else f'{num} bots will run on all events'
    print(confirm)

    bots = initBots(num, events)
    print('bots initialized, starting loop')
    runBots(bots)
    pass