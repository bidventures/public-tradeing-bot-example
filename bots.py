import requests
import json
import random
import math
import datetime
import time
import numpy as np
class Bot:
    def __init__(self, params, account, events = []):
        #### Constants
        self.URL_STEM = 'https://stage.api.jockmkt.net/v0.2'


        self.defaultHeaders = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'bvbot/1.0',
            'X-JMK-Region': 'US-MA',
            'X-JMK-Bot-Secret': 'bot_sec_5486915adc83b60cbf2113e930d09d29'
        }
        #self.ranks = { 0: [0, 1, 2, 3, 4, 5], 1: [6, 7, 8, 9, 10], 2: [11, 12, 13, 14, 15], 3: [16, 17, 18, 19, 20], 4: [21, 22, 23, 24, 25, 26, 27, 28, 29, 30], 5: [31, 32, 33, 34, 35, 36, 37, 38, 39, 40]}
        self.params = params
        self.balance = 250
        self.maxProjections = {}
        self.initParams()
        self.events = events
        email, password, name, username = account
        self.username = username
        first, last = name
        self.verbose = True
        if self.verbose: print(f'Running bot loop for {email}...')

        try:
            if self.verbose: print(f'Fetching access token for {email}...')
            self.token = self.fetchAccessToken(email, password)
            if self.verbose: print(f'Got access token for {email}...')
        except:
            if self.verbose: print(f'Failed to fetch token for {email}, trying to create account')
            self.createAccount(email, first, last, username, password)
            if self.verbose: print(f'Created account for {email}, attempting to fetch token for created account...')
            self.token = self.fetchAccessToken(email, password)
            if self.verbose: print(f'Got access token for {email} after creating account')

        try:
            if self.verbose: print(f'Fetching headers for {email}')
            self.headers = self.getFetchHeaders()
            if self.verbose: print(f'Got headers')
        except:
            raise Exception(f'No headers found for {email}')

    def initParams(self):
        """
        Initialize parameters based on params sent to Bot constructor
        """
        self.eventRanks = {}
        self.buyRisk = self.params.get('buyRisk', 0.1)
        self.sellRisk = self.params.get('sellRisk', 0.1)
        self.maxIPOSpending = self.params.get('maxIPOSpending', 0)
        self.prefRanks = self.params.get('prefRanks', [0, 1, 2, 3, 4, 5]) 
        self.IPOconservative = self.params.get('IPOcsv', False)
        self.LIVEconservative = self.params.get('LIVEcsv', False)

    def createRanking(self, numStocks):
        """
        Helper for updateRanks: divides numStocks into 6 ranking categories with more ranks in each new category

        Parameters
        numStocks: total number of event stocks in event

        Returns finalized ranking categories
        """
        # print(f'There are {numStocks} stocks')
        cutoffs = [0.1,0.125,0.125,0.15,0.2,0.275]
        ranks = {}
        count = 0
        for index in range(len(cutoffs)):
            cutoffs[index] = int(cutoffs[index]*numStocks)
        for rank in range(len(cutoffs)):
            curRank = cutoffs[rank]
            ranks[rank] = ranks.get(rank, [])
            for _ in range(int(curRank)):
                ranks[rank].append(count)
                count +=1
        #print(ranks)
        return ranks
        
    
    def updateRanks(self):
        """
        Updates categorical ranks for each event that the user is in
        """
        userEvents = self.fetchUserEvents()
        userEventsActive = [ue for ue in userEvents if (ue['event']['status'] == 'LIVE' or ue['event']['status'] == "IPO")] 
        for ue in userEventsActive:
            if ue['event_id'] not in self.eventRanks:
                #print(ue['event_id'])
                numStocks = len(self.fetchEventStocks(ue['event_id']))
                self.eventRanks[ue['event_id']] = {rank for r in self.prefRanks for rank in self.createRanking(numStocks)[r]}
                if self.verbose: print(f'Prefered ranks for {ue} is {self.eventRanks[ue["event_id"]]}')
        
        
     
    def getFetchHeaders(self):
        if self.token: 
            return {**self.defaultHeaders, **{'Authorization':f'Bearer {self.token}'}}
        else:
            return self.defaultHeaders

    def randn_bm(self,min, max, skew = 1):
        """
        Normal distribution function

        Return a float between min and max
        """
        u, v = 0, 0
        while u == 0: u = random.random()
        while v == 0: v = random.random()
        num = math.sqrt(-2*math.log(u))*math.cos(2*math.pi*v)
        num = (num/10) + .5
        if (num > 1 or num < 0):
            num = self.randn_bm(min, max, skew)
        num = math.pow(num, skew)
        num *= max - min
        num += min
        return num



    def fetchHoldings(self):
        url = f'{self.URL_STEM}/holdings'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch error {resp.status_code}')
        try:
            r = resp.json()['holdings']
        except:
            raise Exception(f'Holdings fetch error')
        return r


    def fetchDiscover(self):
        url = f'{self.URL_STEM}/discover'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch error {resp.status_code}')
        try:
            r = resp.json()['discover']
        except:
            raise Exception(f'Discover fetch error')
        return r

    def fetchEventStocks(self, eventId):
        url = f'{self.URL_STEM}/events/{eventId}/event_stocks'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch error {resp.status_code}')
        try:
            r = resp.json()['event_stocks']
        except:
            raise Exception(f'Discover fetch error')
        return r

    def joinContest(self, eventId):
        url = f'{self.URL_STEM}/entries'
        data = {
            'event_id': eventId
        }
        headers = self.headers
        timeout = 10000
        resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            respagain = requests.post(url = url, json = data, headers = headers, timeout = timeout)
            if respagain.status_code != 200:
                raise Exception(f'Fetch error {respagain.status_code}')

    def cancelOrder(self, orderId):
        url = f'{self.URL_STEM}/orders/{orderId}'
        headers = self.headers
        timeout = 10000
        resp = requests.delete(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch error {resp.status_code}')

    # test_account = [account@gmail.com, password, (first, last), user]
    def fetchAccessToken(self, email, password):
        url = f'{self.URL_STEM}/oauth/tokens'
        data = {
            'grant_type': 'password',
            'username': email,
            'password': password,
            'client_id': 'jmk_ios'
        }
        headers = self.defaultHeaders
        timeout = 10000
        resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try:
            r = resp.json()['token']['access_token']
        except:
            raise Exception(f'token fetch error')
        return r

    def fetchBalances(self):
        url = f'{self.URL_STEM}/balances'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()['balances']
        except: 
            raise Exception(f'token fetch error')
        return r

    def fetchActiveOrders(self):
        url = f'{self.URL_STEM}/orders?active=true&limit=50'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()['orders']
        except: 
            raise Exception(f'token fetch error')
        return r

    def fetchUserEvents(self):
        url = f'{self.URL_STEM}/account/events?limit=50'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()['user_events']
        except: 
            raise Exception(f'token fetch error')
        return r

    def fetchEventStockPayouts(self, eventID):
        url = f'{self.URL_STEM}/events/{eventID}/payouts'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()['payouts']
        except: 
            raise Exception(f'token fetch error')
        return r
    def fetchAccountEvents(self):
        url = f'{self.URL_STEM}/account/events'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try:
            r = resp.json()
        except:
            raise Exception(f'token fetch error')
        return r
    def fetchLeaderboard(self, eventID):
        url = f'{self.URL_STEM}/events/{eventID}/leaderboard'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()
        except: 
            raise Exception(f'token fetch error')
        return r
    
    def fetchUserActivity(self):
        url = f'{self.URL_STEM}/account/activity'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()
        except: 
            raise Exception(f'token fetch error')
        return r
    
    def fetchEventActivity(self, eventID):
        url = f'{self.URL_STEM}/events/{eventID}/activity'
        headers = self.headers
        timeout = 10000
        resp = requests.get(url = url, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')
        try: 
            r = resp.json()
        except: 
            raise Exception(f'token fetch error')
        return r



    def createAccount(self, email, first, last, display, password):
        url = f'{self.URL_STEM}/accounts'
        data = {
            'email': email,
            'first_name': first,
            'last_name': last,
            'display_name': display,
            'password': password
        }
        headers = self.defaultHeaders
        timeout = 10000
        resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')

    def createOrder(self, eventstockID, side, phase, quantity, limitPrice):
        """
        Creates orders by making post request to API

        Parameters
        eventstockID: eventstock_id of stock we are buying
        side: "BUY" or "SELL"
        phase: "IPO" or "LIVE"
        quantity: quantity we want to buy
        limitPrice: buying price 
        """
        assert(side=='buy' or side=='sell')
        assert(phase=='ipo' or phase =='live')
        url = f'{self.URL_STEM}/orders'
        if self.verbose: print(f'Creating order for {eventstockID}, {side} {quantity} for {limitPrice}')
        data = {
            'eventstock_id' : eventstockID,
            'side' : side,
            'type' : 'limit',
            'phase' : phase,
            'quantity' : str(quantity),
            'time_in_force' : 'gtc',
            'limit_price' : '{:.2f}'.format(limitPrice) 
        }
        headers = self.headers
        timeout = 10000
        if self.verbose: print(f'Making order')
        resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
        if self.verbose: print(f'Resp back.. {resp}, because {resp.reason}')
        if resp.status_code != 200:
            raise Exception(f'Fetch Error {resp.status_code}')

    def getJoinableEventIds(self):
        discoverSections = self.fetchDiscover()
        ids = set()
        for section in discoverSections:
            if section['events']:
                for event in section['events']:
                    if event['status'] and event['type']:
                        if event['type'] == 'CONTEST' and (event['status'] == 'SCHEDULED' or event['status'] == 'IPO'):
                            ids.add(event['id'])
                        # elif event['type'] == 'MARKET' and event['status'] == 'LIVE':
        return ids    

    def joinAvailableEvents(self):
        userEvents = self.fetchUserEvents()
        ids = self.getJoinableEventIds() if self.events == [] else self.events
        matchset = set(ue['event_id'] for ue in userEvents)
        joinableEvents = [i for i in ids if i not in matchset]
        for event_id in joinableEvents:
            try:
                self.joinContest(event_id)
                if self.verbose: print(f'{self.username} successfully joined event {event_id}')
            except:
                if self.verbose: print(f'{self.username} unable to join event {event_id}, moving to next event')
    
    def fetchRanking(self, eventStocks):
        ranked = []
        for eventStock in eventStocks:
            projectedLive = eventStock.get('fantasy_points_projected_live') if eventStock.get('fantasy_points_projected_live') != None else eventStock['fantasy_points_projected'] 
            ranked.append((eventStock['id'], projectedLive))
        ranked.sort(key = lambda x: x[1], reverse = True)
        return ranked
    
    def calculateBidProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should BID on during LIVE (those that don't have ask price)

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksLastPrice = {eventStock['id']: eventStock.get('last_price') for eventStock in eventStocks if eventStock.get('ask_price') == None}
        idToEventStock = {eventStock['id']: eventStock for eventStock in eventStocks}
        ranking = self.fetchRanking(eventStocks)
        profitableStocks = []

        for rank in range(len(ranking)):
            stock = ranking[rank][0]
            if stock in eventStocksLastPrice:
                profit = (float(valuations[rank]['amount']) - float(eventStocksLastPrice[stock])) / float(eventStocksLastPrice[stock])
                weight = (math.pow(2, (float(valuations[rank]['amount']) - float(eventStocksLastPrice[stock])) / 10) - 1)
                profit = profit * (1 + weight)
                if idToEventStock[stock].get('amount_completed') != None:
                    #print(stock.get('amount_completed', 0))
                    amountComplete = float(idToEventStock[stock].get('amount_completed', 0))
                else:
                    amountComplete = 0
                profit = profit * (1 + math.log(amountComplete + 0.025, 50))
                if profit > 0.25:
                    profitableStocks.append(( 
                        stock,
                        profit,
                        # {
                        #     'last_price': float(eventStocksLastPrice[stock]),
                        #     'valuation': float(valuations[rank]['amount']),
                        #     'fantasy points projected': float(ranking[rank][1]),
                        #     'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored', 0)),
                        #     'amt_complete': self.simulator.amountComplete(stock)
                        # }
                    ))
        profitableStocks.sort(key = lambda x: x[1], reverse = True)
        profitableStocks = profitableStocks[:random.randint(1, 5)]
        return profitableStocks
    
    def calculateBuyProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should BUY during LIVE (those that have ask price)

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksAsked = {eventStock['id']: eventStock.get('ask_price') for eventStock in eventStocks if eventStock['ask_price'] != None}
        idToEventStock = {eventStock['id']: eventStock for eventStock in eventStocks}
        ranking = self.fetchRanking(eventStocks)
        potentialProfit = []

        for rank in range(len(ranking)):
            stock = ranking[rank][0] #stockid
            if stock in eventStocksAsked:
                profit = (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / float(eventStocksAsked[stock])
                weight = (math.pow(2, (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / 10) - 1)
                profit = profit * (1 + weight)
                if idToEventStock[stock].get('amount_completed') != None:
                    #print(stock.get('amount_completed', 0))
                    amountComplete = float(idToEventStock[stock].get('amount_completed', 0))
                else:
                    amountComplete = 0
                profit = profit * (1 + math.log(amountComplete + 0.2 , 50))
                riskAdd = np.random.normal(0, 0.0125)
                risk = self.buyRisk + riskAdd
                # print(f'This is profit {profit}, amount complete is {amountComplete}')
                if profit > risk:
                    potentialProfit.append((
                        idToEventStock[stock],
                        profit,
                            # {'ask price': float(eventStocksAsked[stock]), 
                            # 'valuation': float(valuations[rank]['amount']),
                            # 'fantasy points projected': float(ranking[rank][1]),
                            # 'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored',0)),
                            # 'weight': weight,
                            # 'amt_complete': self.simulator.amountComplete(stock)}       
                    )) 
        potentialProfit.sort(key = lambda x: x[1], reverse = True)
        potentialProfit = potentialProfit[:random.randint(5, 15)]
        return potentialProfit
    def calculateSellProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should SELL during LIVE

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        holdings = self.fetchHoldings()

        # filter out event stocks that we have orders for
        holdingsIds = {holding['eventstock_id']: holding['selling_power'] for holding in holdings if holding['selling_power'] != '0'} #available might be selling_power in v2

        if len(holdingsIds) == 0:
            if self.verbose: print(f'Nothing to offer for sale from holdings')
            return []

        eventStocksBid = {eventStock['id']: eventStock.get('bid_price') for eventStock in eventStocks if eventStock['bid_price'] != None}
        idToEventStock = {eventStock['id']: eventStock for eventStock in eventStocks}
        ranking = self.fetchRanking(eventStocks)
        profitableStocks = []

        for rank in range((len(ranking))):
            stock = ranking[rank][0] #stockid
            if stock in eventStocksBid:
                profit = (float(eventStocksBid[stock]) - float(valuations[rank]['amount'])) / float(valuations[rank]['amount'])
                weight = (math.pow(2, (float(eventStocksBid[stock]) - float(valuations[rank]['amount'])) / 10) - 1)
                profit = profit * (1 + weight)
                if idToEventStock[stock].get('amount_completed') != None:
                    #print(stock.get('amount_completed', 0))
                    amountComplete = float(idToEventStock[stock].get('amount_completed', 0))
                else:
                    amountComplete = 0
                profit = profit * (1 + math.log(amountComplete + 0.2, 50)) #timing offset
                riskAdd = random.uniform(0, 0.0125)
                risk = self.sellRisk + riskAdd
                if stock in holdingsIds and stock in eventStocksBid and profit > risk:
                    profitableStocks.append((
                        idToEventStock[stock],
                        profit,
                        # {'bid price': float(eventStocksBid[stock]),
                        # 'valuation': float(valuations[rank]['amount']),
                        # 'fantasy points projected': float(ranking[rank][1]),
                        # 'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scores', 0))}
                    ))
        profitableStocks.sort(key = lambda x: x[1], reverse = True)
        profitableStocks = profitableStocks[:random.randint(1, 5)]
        return profitableStocks
        


    def calculateIPOProfits(self, eventStocks, valuations, eventID):
        """
        Ranks eventstocks we should BID during IPO

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        eventID: event id of event
        """
        eventStocksLastPrice = {eventStock['id']: eventStock.get('last_price') for eventStock in eventStocks if eventStock['fantasy_points_projected'] > 0}
        idToEventStock = {eventStock['id']: eventStock for eventStock in eventStocks}
        activeOrders = {order['eventstock_id']: order['quantity'] for order in self.fetchActiveOrders()}
        if self.verbose: print(f'active orders are {activeOrders}')
        ranking = self.fetchRanking(eventStocks)
        potentialProfit = []
        for rank in range(len(ranking)):
            stock = ranking[rank][0]
            if stock in eventStocksLastPrice and int(activeOrders.get(stock, 0)) < random.randint(3, 10) and rank in self.eventRanks[eventID]:
                potentialProfit.append((
                    idToEventStock[stock],
                        # {'last price': float(eventStocksAsked[stock]), 
                        # 'valuation': float(valuations[rank]['amount']),
                        # 'fantasy points projected': float(ranking[rank][1]),
                        # 'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored',0))}       
                )) 
        random.shuffle(potentialProfit)
        potentialProfit = potentialProfit[:random.randint(1, 10)]
        # print(f' Best stocks are {self.showPlayers(potentialProfit)}')
        return potentialProfit


    def placeIPOBid(self, es, eventStocks, valuations, amountComplete, eventCurrency, maxProj):
        """
        Determines if we should BID on an eventstock during IPO, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks in event
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        eventCurrency: currency type for event
        """
        targetId = es['id']


        mapped = [] 
        for stock in eventStocks:
            projection = stock['fantasy_points_projected']
            gap = np.random.normal(math.e**(-4*projection/maxProj+1), (math.e**(-4*projection/maxProj+1))/10) 
            if self.IPOconservative == True:
                projection = projection * (1 - gap) if targetId == stock else projection
            else:
                projection = projection * (1 + gap) if targetId == stock else projection
            if stock['id'] == targetId:
                targetProj = projection
            mapped.append((stock['id'], projection))

        #sort to see which order we end up in
        mapped.sort(key = lambda x: x[1]) 
        mapped.reverse()

        index = mapped.index((targetId, targetProj))

        impliedPayout = 0 if index >= len(valuations) else float(valuations[index]['amount'])


        bidWithChatter = round(self.randn_bm(impliedPayout * 0.9, impliedPayout * 1.1), 2)

        #pay max of either bid w chatter or last event payout
        minValuation = valuations[-1]
        bid = max(float(minValuation['amount']), bidWithChatter)

        balances = self.fetchBalances()
        eventBalance = None
        for balance in balances:
            if balance['currency'] == eventCurrency:
                eventBalance = balance
                break
        last_price = 1
        if es['last_price'] != None:
            last_price = es['last_price']
        if float(last_price) + 0.10 > bid:
            if self.verbose: print(f'Skipping bid for {es["stock"]["name"]}, last price {es["last_price"]} higher than max bid {bid} target {impliedPayout}')
            return

        bid = float(last_price) + random.uniform(0.05, 0.10)

        shareCount = random.randint(1, 5)

        if not eventBalance or float(eventBalance['buying_power']) - bid * shareCount  * 1.05 < 250 - self.maxIPOSpending:
            if self.verbose: print(f'Skipping bid for {es["stock"]["name"]}, {shareCount} @ {bid} plus fees close to available currency {eventBalance["buying_power"]}')
            return

        if self.verbose: print(f'Bidding for {shareCount} share(s) of {es["stock"]["name"]} at {bid} (target of {valuations[index]["amount"]} before timing & chatter)')

        try:
            self.createOrder(targetId, 'buy', 'ipo', shareCount, bid)
        except:
            if self.verbose: print('Bidding failed...')

    def placeLiveBid(self, es, eventStocks, valuations, amountComplete, eventCurrency, stockAsked, maxProj):
        """
        Determines if we should BID on an eventstock during LIVE, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks in event
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        eventCurrency: currency type of event
        stocksAsked: if es has an ask price
        """
        targetId = es['id']

        # project this es at the low end & rest at the high end 
        biddingMap = []
        for eventStock in eventStocks:
            projection = eventStock.get('fantasy_points_projected_live')
            projection = eventStock['fantasy_points_projected'] if projection == None else projection
            gap = np.random.normal(math.e**(-4*projection/maxProj+1), (math.e**(-4*projection/maxProj+1))/10) * (1 - amountComplete)
            if self.LIVEconservative == True:
                projection = projection * (1 - gap) if targetId == eventStock['id'] else projection
            else:
                projection = projection * (1 + gap) if targetId == eventStock['id'] else projection
            if eventStock['id'] == targetId:
                targetBidProj = projection
            biddingMap.append((eventStock['id'], projection))
        # sort to see which order we end up in
        # sellingMap.sort(key = lambda x: x[1])
        # sellingMap.reverse()

        biddingMap.sort(key = lambda x: x[1])
        biddingMap.reverse()

        # check what order we are in 
        # sellingIndex = sellingMap.index((targetId,targetSellProj))
        buyingIndex = biddingMap.index((targetId,targetBidProj))

        # impliedHighPayout = float(valuations[sellingIndex]['amount'])
        impliedLowPayout = float(valuations[buyingIndex]['amount'])

        # highWithChatter = round(self.randn_bm(impliedHighPayout * 1.01, impliedHighPayout * 1.10), 2)
        lowWithChatter = round(self.randn_bm(impliedLowPayout * 0.90, impliedLowPayout * 0.99), 2)

        minValuation = valuations[-1]

        bid = max(float(minValuation['amount']), lowWithChatter)

        # bid at the amount we think they are going to have 
        balances = self.fetchBalances()
        eventBalance = None
        for balance in balances:
            if balance['currency'] == eventCurrency:
                eventBalance = balance

        # possibleShares = [1,2,3,4]
        # random.shuffle(possibleShares)
        # shareCount = possibleShares[0]
        shareCount = 1

        if stockAsked == True:
            if float(es['ask_price']) + 0.10 > bid:
                if self.verbose: print(f'Skipping bid for {es["stock"]["name"]}, {shareCount} @ {bid}, lower than its ask price {es["ask_price"]}')
                return
            bid = float(es['ask_price']) + 0.10
        # else:
        #     bid = lowWithChatter * (1 - random.uniform(0.1, 0.15))

        if not eventBalance or float(eventBalance["buying_power"]) - bid * shareCount * 1.05 < 0:
            if self.verbose: print(f'Skipping bid for {es["stock"]["name"]}, {shareCount} @ {bid} close to available currency {eventBalance["buying_power"]}')
            return
        
        if self.verbose: print(f'Bidding for {shareCount} share(s) of {es["stock"]["name"]} at {bid} range of {impliedLowPayout}, asked is {stockAsked}')

        try: 
            self.createOrder(targetId, 'buy', 'live', shareCount, bid)
        except:
            if self.verbose: print('Placing order failed')

    def placeLiveOffer(self, es, eventStocks, valuations, amountComplete, eventCurrency, shareCount, maxProj):
        """
        Determines if we should SELL an eventstock during LIVE, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks in event
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        eventCurrency: currency type of event
        shareCount: number of sharest to offer
        """
        targetId = es['id']
        sellingMap = []
        for eventStock in eventStocks:
            projection = eventStock.get('fantasy_points_projected_live')
            projection = eventStock['fantasy_points_projected'] if projection == None else projection
            gap = np.random.normal(math.e**(-4*projection/maxProj+1), (math.e**(-4*projection/maxProj+1))/10)  * (1 - amountComplete)
            if self.LIVEconservative == True:
                projection = projection * (1 - gap) if targetId == eventStock['id'] else projection
            else:
                projection = projection * (1 + gap) if targetId == eventStock['id'] else projection
            if eventStock['id'] == targetId:
                targetBidProj = projection
            sellingMap.append((eventStock['id'], projection))

        sellingMap.sort(key = lambda x: x[1])
        sellingMap.reverse()
        
        sellingIndex = sellingMap.index((targetId, targetBidProj))

        impliedHighPayout = float(valuations[sellingIndex]['amount'])

        highWithChatter = round(self.randn_bm(float(impliedHighPayout) * 1.01, float(impliedHighPayout) * 1.10), 2)

        maxValuation = valuations[0]

        offer = min(float(maxValuation['amount']), highWithChatter)

        if float(es['bid_price']) - 0.02 < offer:
            if self.verbose: print(f'Skipping offer for {es["stock"]["name"]}, {shareCount} @ {offer}, higher than its bid price {es["bid_price"]}')
            return
        
        offer = round(float(es['bid_price']) - 0.02, 2)

        if self.verbose: print(f'Offering {shareCount} share(s) of {es["stock"]["name"]} at {offer} (payout of {impliedHighPayout})')
        try:
            self.createOrder(targetId, 'sell', 'live', shareCount, offer)
        except:
            if self.verbose: print('Placing order failed')

    def cancelLiveOrders(self):
        activeOrders = self.fetchActiveOrders()
        ordersToCancel = [order for order in activeOrders if order['phase'] == 'LIVE']

        for order in ordersToCancel:
            if self.verbose: print(f'Cancelling order {order["id"]}')
            self.cancelOrder( order['id'])

    def submitLiveOffers(self):
        """
        Calls placeLiveOffer for eventstocks from calculate profit functions
        """
        userEvents = self.fetchUserEvents()
        userEventsLive = [ue for ue in userEvents if ue['event']['status'] == 'LIVE']

        for ue in userEventsLive:
            if self.verbose: print(f'Analyizing {ue["event"]["name"]} ({ue["event_id"]})')
            maxProj = self.maxProjections[ue['event_id']]

            eventStocks = self.fetchEventStocks(ue['event_id'])
            valuations = self.fetchEventStockPayouts(ue['event_id'])

            profitableStocks = self.calculateSellProfits(eventStocks, valuations)
            if self.verbose: print(f'Stocks to sell {profitableStocks}')

            for es in profitableStocks:
                stock = es[0]
                sharesToSell = 1
                if stock.get('amount_completed') != None:
                    #print(stock.get('amount_completed', 0))
                    amountComplete = float(stock.get('amount_completed', 0))
                else:
                    amountComplete = 0
                #amountComplete = float(stock.get('amount_completed', 0))
                self.placeLiveOffer(stock, eventStocks, valuations, amountComplete, ue['event']['currency_id'], sharesToSell, maxProj)
    

    def submitLiveBids(self):
        """
        Calls placeLiveBid for eventstocks from calculate profit functions
        """
        userEvents = self.fetchUserEvents()
        userEventsLive = [ue for ue in userEvents if ue['event']['status'] == 'LIVE']

        for ue in userEventsLive:
            if self.verbose: print(f'Analyzing {ue["event"]["name"]} ({ue["event_id"]})')
            maxProj = self.maxProjections[ue['event_id']]

            eventStocks = self.fetchEventStocks(ue['event_id'])
            valuations = self.fetchEventStockPayouts(ue['event_id'])
            
            askedStocks = self.calculateBuyProfits(eventStocks, valuations)
            if self.verbose: print(f'Stocks to buy {askedStocks}')
            for es in askedStocks:
                stock = es[0]
                if stock.get('amount_completed') != None:
                    #print(stock.get('amount_completed', 0))
                    amountComplete = float(stock.get('amount_completed', 0))
                else:
                    amountComplete = 0

                #amountComplete = float(stock.get('amount_completed', 0))
                self.placeLiveBid(stock, eventStocks, valuations, amountComplete, ue['event']['currency_id'], True, maxProj)
            
            # notAskedStocks = self.calculateBidProfits(eventStocks, valuations)
            # print(f'Stocks to bid {notAskedStocks}')
            # for es in notAskedStocks:
            #     stock = es[0]
            #     amountComplete = stock.get('amount_completed', 0)
            #     self.placeLiveBid(stock, eventStocks, valuations, amountComplete, ue['event']['currency_id'], False)

    def submitIPOBids(self):
        """
        Calls placeIPOBid for eventstocks from calculate profit functions
        """
        userEvents = self.fetchUserEvents()
        userEventsinIPO = [ue for ue in userEvents if ue['event']['status'] == 'IPO']

        for ue in userEventsinIPO:
            if self.verbose: print(f'Working with event {ue["event_id"]}')
            maxProj = self.maxProjections[ue['event_id']]

            eventStocks = self.fetchEventStocks(ue['event_id'])
            valuations = self.fetchEventStockPayouts(ue['event_id'])

            if len(eventStocks) == 0:
                return

            # activeOrderIds = {activeOrder['eventstock_id'] for activeOrder in activeOrders}
            # eventStocksToBuy = [es for es in eventStocks if es['id'] not in activeOrderIds]

            # if len(eventStocksToBuy) == 0:
            #     print(f'Nothing to do in {ue["event"]["name"]} ({ue["event_id"]})')
            #     continue

            # now = datetime.datetime.now()
            # ipoOpen = datetime.datetime.strptime(ue['event']['ipo_open_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            # ipoClose = datetime.datetime.strptime(ue['event']['live_at_estimated'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
            # amountComplete = (now - ipoOpen) / (ipoClose - ipoOpen)

            # print(f'See IPO is {round(amountComplete*100, 2)}% complete... calculating bids...')

            profitableStocks = self.calculateIPOProfits(eventStocks, valuations, ue['event_id'])
            for es in profitableStocks:
                stock = es[0]
                # print(f'float {stock}')
                if stock.get('amount_completed') != None:
                    amountComplete = float(stock.get('amount_completed', 0))
                else:
                    amountComplete = 0
                #amountComplete = float(stock.get('amount_completed', 0))
                self.placeIPOBid(stock, eventStocks, valuations, amountComplete, ue['event']['currency_id'], maxProj)

            # for es in eventStocks:
            #     amountComplete = es.get('amount_complete', 0)
            #     self.placeIPOBid(es, eventStocks, valuations, amountComplete, ue['event']['currency_id'], ranks)
    def updateMaxProjections(self):
        userEvents = self.fetchUserEvents()
        userEventsActive = [ue for ue in userEvents if (ue['event']['status'] == 'LIVE' or ue['event']['status'] == "IPO")] 
        for ue in userEventsActive:
            eventStocks = self.fetchEventStocks(ue['event_id'])
            self.maxProjections[ue['event_id']] = self.fetchRanking(eventStocks)[0][1]
        if self.verbose: print(f'max projections {self.maxProjections}')

            


    def run(self):
        # Phase One: Join Available Events
        if self.verbose: print(f'Running bot')

        if self.verbose: print('Checking events to join...')
        self.joinAvailableEvents()
        if self.verbose: print('Joined available events')

        if self.verbose: print('Updating ranks...')
        self.updateRanks()
        if self.verbose: print('Updated ranks...')
        
        if self.verbose: print('Updating max projection...')
        self.updateMaxProjections()
        if self.verbose: print('Updated max projection')

        # Phase Two: Place IPO Bids 
        if self.verbose: print('Checking events in IPO for activity')
        self.submitIPOBids()
        if self.verbose: print('IPO bids entered...')

        # Phase Three: Cancel Live Orders -- We'll Reprice in Next Step 
        if self.verbose: print('Cancelling live orders...')
        self.cancelLiveOrders()

        #Phase Four: Place Live Offers from Holdings
        if self.verbose: print('Checking live events to adjust holding offers')
        self.submitLiveOffers()
        
        # Phase Five: Place Live Orders from Balances on Non-Owned Shares
        if self.verbose: print('Checking live events to place orders...')
        self.submitLiveBids()

        if self.verbose: print('Bot loop closed...')




