from bots_with_event_simulator import Bot
from event_simulator import Simulator as sim 
import json
import numpy as np
import time
import csv
import itertools

e1 = "evt_1a341f55f12d099b714af8b82c3205c9"
e2 = "evt_d95b8e01de0284c3e957cccf865444c5"
e3 = "evt_c1e04a4f3003dce1549aafec89224dc1"
e4 = "evt_e369b5a56fadc620"
e5 = "evt_11e77bcdb4362e13"
e6 = "evt_0fe9902c2f1c72ae"
events = [e1, e2, e3, e4]
ipospendings = [i*50 for i in range(6)]
buyRisks = [round(i*.25, 2) for i in range(1, 5)]
sellRisks = [round(i*.05, 2) for i in range(2,7)]
possible_ranks = [[], [0], [1], [2], [3], [4], [0, 1], [1,2], [2,3], [3,4]]

n = 6

def generateBots(events= events, ipospendings = ipospendings, sellRisks = sellRisks, buyRisks = buyRisks, ranks = possible_ranks, ipos = [True, False], lives = [True, False]):
    with open(f'simulationData/sim{n}.csv', 'a', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(['Bot', 'maxIPOSpending', 'BuyRisk', 'SellRisk', 'PrefRanks', 'IPOcsv', 'LIVEcsv', 'EventID', 'AvgEarnings'])

    iterables = [(arg) for arg in itertools.product(ipospendings, buyRisks, sellRisks, possible_ranks, [True, False], [True, False])]
    print(f'For each event: {len(iterables)}')
    count = 0
    for event in events:
        s = sim(event)
        for i in iterables:
            count += 1
            b = Bot(params = {'maxIPOSpending': i[0], 'buyRisk': i[1], 'sellRisk': i[2], 'prefRanks': i[3], 'IPOcsv': i[4], 'LIVEcsv': i[5]}, simulator = s)
            earnings = []
            for _ in range(5):
                b.runBot()
                a = b.earnings + b.balance
                earnings.append(a)
                b.resetBot()
            avg_earnings = np.mean(earnings)
            with open(f'simulationData/sim{n}.csv', 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow([f'bot_{count}', i[0], i[1], i[2], i[3], i[4], i[5], event, avg_earnings])