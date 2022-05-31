import sys
sys.path.append("../jockmktbot/")
from event_simulator import Simulator as sim
import random
import math
import matplotlib.pyplot as plt
import numpy as np

class Bot:
    def __init__(self, params, simulator):
        """
        Initialize Bot parameters, simulator variables

        Parameters
        params: parameters with fields 'buyRisk', 'sellRisk', 'maxIPOSpending', 'prefRanks', 'prefPositions', 'IPOcsv', 'LIVEcsv'
        simulator: Simulator instance
        """
        self.balance = 250
        self.params = params
        self.simulator = simulator
        self.ranks = self.initRanks()
        self.initParams()

        self.IPOHoldings = {} # {eventstock_id: quantity}
        self.LIVEHoldings = {} # {eventstock_id: quantity}
        self.liveHoldingsPrice = set() # {eventstock_id: bought price}
        self.liveSellingsPrice = set() # {eventstock_id: sold price}
        self.priceOfIPOHoldings = {} # {eventstock_id: ipo price}
        self.priceOfBids = {} # {eventstock_id: bid price}

        self.bestBuyStocksGraph = {'x':[],'y':[]}
        self.spendingGraph = {'x':[], 'y':[]}
        self.bestSellStocksGraph = {'x':[], 'y':[]}

        self.stockHistory = {}
        self.buyingHistory = {}
        self.sellingHistory = {}
        self.biddingHistory = {}
    def initRanks(self):
        """
        Initialize groups of ranks for groups 0,1,2,3,4,5 based on number of EventStocks in simulated event
        
        Return dictionary with groups 0,1,2,3,4,5 as keys, and corresponding ranks in each group as values
        """
        numStocks = len(self.simulator.fetchEventStocks())
        print(f'There are {numStocks} stocks')
        cutoffs = [0.1, 0.125, 0.125, 0.15, 0.2, 0.275]
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
        return ranks
        
    def initParams(self):
        """
        Initialize parameters based on params sent to Bot constructor
        """
        self.buyRisk = self.params.get('buyRisk', 0.45)
        self.sellRisk = self.params.get('sellRisk', 0.2)
        self.maxIPOSpending = self.params.get('maxIPOSpending', 0)
        self.prefRanks = {rank for r in self.params.get('prefRanks', [0,1,2,3,4]) for rank in self.ranks[r]} # 5 ranges shown above
        self.prefPositions = self.params.get('prefPositions', {}) #subset 
        self.IPOconservative = self.params.get('IPOcsv', True)
        self.LIVEconservative = self.params.get('LIVEcsv', True)
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
    def showPlayers(self, holdings):
        """
        Helper function to view player names

        Parameters:
        holdings: a dictionary with keys as eventstock_id's and any corresponding values

        Returns a dictionary with keys as names and the input corresponding values
        """
        return {self.simulator.eventStocks[stock]['stock']['name']: holdings[stock] for stock in holdings}
    
    def updateSpendingGraphs(self, eventstockID, side, phase, quantity, limitPrice):
        """
        Updates spending graphs with our balance 
        """
        self.spendingGraph['x'].append(self.simulator.fetchIteration())
        self.spendingGraph['y'].append(self.balance)
    
    def updateStockGraphs(self, side, profitableStocks, eventStocks):
        """
        Updates buy and sell graphs with the best valued stocks
        """
        if side == "BUY" and profitableStocks:
            self.bestBuyStocksGraph['x'].append(self.simulator.fetchIteration())
            self.bestBuyStocksGraph['y'].append(profitableStocks[0][1])
        elif side == "SELL" and profitableStocks:
            self.bestSellStocksGraph['x'].append(self.simulator.fetchIteration())
            self.bestSellStocksGraph['y'].append(profitableStocks[0][1])

    def showGraphs(self):
        """
        Helper function to print all graphs after simulation
        """
        fig, (ax_0, ax_1, ax_2) = plt.subplots(3, sharex = True)
        fig.suptitle('Stats')
        ax_0.scatter(self.bestBuyStocksGraph['x'], self.bestBuyStocksGraph['y'])
        ax_0.set(xlabel = 'iteration', ylabel = 'bestBuyStocks')
        ax_1.scatter(self.bestSellStocksGraph['x'], self.bestSellStocksGraph['y'])
        ax_1.set(xlabel = 'iteration', ylabel = 'bestSellStocks')
        ax_2.scatter(self.spendingGraph['x'], self.spendingGraph['y'])
        ax_2.set(xlabel = 'iteration', ylabel = 'balance')
        plt.show()

    def resetBot(self):
        """
        Resets bot
        """
        print(f'Resetting holdings...')
        self.IPOHoldings = {} 
        self.LIVEHoldings = {} 
        self.liveHoldingsPrice = set() 
        self.liveSellingsPrice = set() 
        self.priceOfIPOHoldings = {} 
        self.priceOfBids = {} 

        self.bestBuyStocksGraph = {'x':[],'y':[]}
        self.spendingGraph = {'x':[], 'y':[]}
        self.bestSellStocksGraph = {'x':[], 'y':[]}

        self.stockHistory = {}
        self.buyingHistory = {}
        self.sellingHistory = {}
        self.biddingHistory = {}
        print(f'Resetting balance to 250...')
        self.balance = 250
        print(f'Resetting simulator...')
        self.simulator.reset()
        print(f'Done resetting')
    
    def LIVESell(self, eventstockID, side, phase, quantity, limitPrice):
        """
        Used to track stocks that we have sold

        Parameters
        eventstockID: eventstock_id of stock we are selling
        quantity: quantity we want to sell
        limitPrice: selling price 
        """
        eventStocks = self.simulator.fetchEventStocks()
        print(f'Before selling {eventStocks[eventstockID]["stock"]["name"]} we have {self.LIVEHoldings.get(eventstockID, 0) + self.IPOHoldings.get(eventstockID, 0)} stocks in holdings')
        phaseBought = "LIVE" if (eventstockID in self.LIVEHoldings and self.LIVEHoldings.get(eventstockID, 0) > 0) else "IPO"
        self.LIVEHoldings[eventstockID] = self.LIVEHoldings.get(eventstockID, 0) - 1 if phaseBought == "LIVE" else self.LIVEHoldings.get(eventstockID, 0)
        self.IPOHoldings[eventstockID] = self.IPOHoldings.get(eventstockID, 0) - 1 if phaseBought == "IPO" else self.IPOHoldings.get(eventstockID, 0)
        self.liveSellingsPrice.add((eventstockID, limitPrice))
        self.balance += limitPrice * quantity
        self.sellingHistory[self.simulator.fetchIteration()] = self.sellingHistory.get(self.simulator.fetchIteration(), [])
        self.sellingHistory[self.simulator.fetchIteration()].append(f'{eventStocks[eventstockID]["stock"]["name"]} for {limitPrice}')
        self.stockHistory[eventstockID] = self.stockHistory.get(eventstockID, [])
        self.stockHistory[eventstockID].append(f'LIVE sell at {limitPrice}')
        print(f'Selling {eventStocks[eventstockID]["stock"]["name"]} for {limitPrice}, balance is {self.balance}')
        print(f'After selling {eventStocks[eventstockID]["stock"]["name"]} we have {self.LIVEHoldings.get(eventstockID, 0) + self.IPOHoldings.get(eventstockID, 0)} stocks in holdings')


    def LIVEBuy(self, eventstockID, side, phase, quantity, limitPrice, stockAsked):
        """
        Used to track stocks that we have bought at LIVE 

        Parameters
        eventstockID: eventstock_id of stock we are buying
        quantity: quantity we want to buy
        limitPrice: buying price 
        stocksAsked: if the stock we want to buy already has an ask price
        """
        eventStocks = self.simulator.fetchEventStocks()
        self.balance -= limitPrice * quantity
        self.buyingHistory[self.simulator.fetchIteration()] = self.buyingHistory.get(self.simulator.fetchIteration(), [])
        self.stockHistory[eventstockID] = self.stockHistory.get(eventstockID, [])

        if stockAsked == True:
            self.liveHoldingsPrice.add((eventstockID, limitPrice))
            self.LIVEHoldings[eventstockID] = self.LIVEHoldings.get(eventstockID, 0) + 1
            self.buyingHistory[self.simulator.fetchIteration()].append(f'{eventStocks[eventstockID]["stock"]["name"]} for {limitPrice}')
            self.stockHistory[eventstockID].append(f'LIVE bought at {limitPrice}')
            print(f'Buying {eventStocks[eventstockID]["stock"]["name"]} for {limitPrice}, balance is {self.balance}')
        else:
            self.stockHistory[eventstockID].append(f'LIVE bid at {limitPrice}')
            self.priceOfBids[eventstockID] = limitPrice


    def IPOBuy(self, eventstockID, side, phase, quantity, limitPrice):
        """
        Used to track stocks that we have bought at IPO

        Parameters
        eventstockID: eventstock_id of stock we are buying
        quantity: quantity we want to buy
        limitPrice: buying price 
        """
        eventStocks = self.simulator.fetchEventStocks()
        self.IPOHoldings[eventstockID] = self.IPOHoldings.get(eventstockID, 0) + quantity
        self.priceOfIPOHoldings[eventstockID] = limitPrice
        self.stockHistory[eventstockID] = self.stockHistory.get(eventstockID, [])
        self.stockHistory[eventstockID].append(f'IPO bought at {limitPrice}')
        self.balance -= limitPrice * quantity
        self.buyingHistory[self.simulator.fetchIteration()] = self.buyingHistory.get(self.simulator.fetchIteration(), [])
        self.buyingHistory[self.simulator.fetchIteration()].append(f'IPO {eventStocks[eventstockID]["stock"]["name"]} bought for {limitPrice}')

    def createOrder(self, eventstockID, side, phase, quantity, limitPrice, stockAsked):
        """
        Creates orders by calling IPOBuy, LIVEBuy, and LIVESell

        Parameters
        eventstockID: eventstock_id of stock we are buying
        side: "BUY" or "SELL"
        phase: "IPO" or "LIVE"
        quantity: quantity we want to buy
        limitPrice: buying price 
        stocksAsked: if the stock we want to buy already has an ask price
        """
        if side == 'BUY':
            if phase == 'IPO':
                self.IPOBuy(eventstockID, side, phase, quantity, limitPrice)
            else:
                self.LIVEBuy(eventstockID, side, phase, quantity, limitPrice, stockAsked)
        else:
            self.LIVESell(eventstockID, side, phase, quantity, limitPrice)
        self.updateSpendingGraphs(eventstockID, side, phase, quantity, limitPrice)

    def updateIPOHoldings(self):
        """
        Updates our holdings during IPO if we were outbid
        """
        if self.simulator.fetchPhase() == 'IPO':
            eventStocks = self.simulator.fetchEventStocks()
            stocksToDelete = set()
            for eventStock in self.IPOHoldings:
                if self.priceOfIPOHoldings[eventStock] < float(eventStocks[eventStock].get("last_price", float('inf'))):
                    print(f'Outbid on {eventStock}, our price: {self.priceOfIPOHoldings[eventStock]} | new price: {eventStocks[eventStock]["last_price"]}')
                    print(f'Before getting outbid we have a balance of {self.balance}')
                    self.balance += self.IPOHoldings[eventStock] * self.priceOfIPOHoldings[eventStock]
                    print(f'After getting outbid we have a balance of {self.balance}')
                    stocksToDelete.add(eventStock)
                    self.stockHistory[eventStock].append(f'IPO outbid at {eventStocks[eventStock]["last_price"]}')
            for eventStock in stocksToDelete:
                del self.IPOHoldings[eventStock]
                del self.priceOfIPOHoldings[eventStock]
                print(f'After getting outbid, shares are now {self.IPOHoldings.get(eventStock)}')
        else:
            print(f'Skipping IPO Holdings update')
    
    def updateBids(self):
        """
        Updates our bids for stocks wo ask price during LIVE if the stock now has an ask price
        """
        if self.simulator.fetchPhase() == 'LIVE':
            eventStocks = self.simulator.fetchEventStocks()
            stocksToDelete = set()
            for eventStock in self.priceOfBids:
                askPrice = eventStocks[eventStock].get("ask_price")
                if askPrice != None:
                    self.balance += self.priceOfBids[eventStock]
                    stocksToDelete.add(eventStock)
                    if float(askPrice) < self.priceOfBids[eventStock]:
                        print(f'Transaction for {eventStocks[eventStock]["stock"]["name"]} successful \
                            Our price: {self.priceOfBids[eventStock]}, Ask price: {eventStocks[eventStock].get("ask_price")}')
                        self.LIVEBuy(eventStock, 'BUY', 'LIVE', 1, round(float(askPrice), 2), stockAsked = True)
                        self.biddingHistory[self.simulator.fetchIteration()] = self.biddingHistory.get(self.simulator.fetchIteration(), [])
                        self.biddingHistory[self.simulator.fetchIteration()].append(f'{eventStocks[eventStock]["stock"]["name"]} for {askPrice}')
                    else: 
                        print(f'Transaction for {eventStocks[eventStock]["stock"]["name"]} unsuccessful \
                        Our price: {self.priceOfBids[eventStock]}, Ask price: {eventStocks[eventStock]["ask_price"]}')
            for eventStock in stocksToDelete:
                del self.priceOfBids[eventStock]
                
    
    def placeLiveOffer(self, es, eventStocks, valuations, amountComplete):
        """
        Determines if we should SELL an eventstock during LIVE, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        """
        targetId = es
        mapped = []
        for stock in eventStocks:
            projection = eventStocks[stock].get('fantasy_points_projected_live')
            projection = eventStocks[stock]["fantasy_points_projected"] if projection == None else projection
            gap = np.random.normal(2.71**(-5*projection/100-0.25), (2.71**(-5*projection/100-0.25))/20) * (1 - amountComplete)
            #gap = random.uniform(0.05, 0.1) * (1 - amountComplete)
            if self.LIVEconservative == True:
                projection = projection * (1 - gap) if targetId == stock else projection
            else:
                projection = projection * (1 + gap) if targetId == stock else projection 
            if stock == targetId:
                targetBidProj = projection
            mapped.append((stock, projection))
        print(f'We project {eventStocks[targetId]["stock"]["name"]} to get {targetBidProj}')
        mapped.sort(key = lambda x: x[1])
        mapped.reverse()

        buyingIndex = mapped.index((targetId, targetBidProj))
        impliedLowPayout = float(valuations[buyingIndex]['amount'])
        lowWithChatter = round(self.randn_bm(impliedLowPayout * 0.90, impliedLowPayout * 0.99), 2)
        minValuation = valuations[-1]
        bid = max(float(minValuation['amount']), lowWithChatter)
        shareCount = 1
        print(f'We want to sell {eventStocks[targetId]["stock"]["name"]} at {bid}')
        bidPrice = float(eventStocks[targetId]['bid_price'])
        if bid > bidPrice:
            print(f'Price for {eventStocks[targetId]["stock"]["name"]} is too low ({bidPrice})')
            return
        newBid = round(bidPrice, 2)
        print(f'Selling {shareCount} share(s) of {eventStocks[es]["stock"]["name"]} at {newBid}, implied payout of {impliedLowPayout}')

        try:
            self.createOrder(targetId, 'SELL', 'LIVE', shareCount, newBid, stockAsked = None)
        except:
            print('Placing sell order failed')
    
    def placeLiveBid(self, es, eventStocks, valuations, amountComplete, stockAsked):
        """
        Determines if we should BID on an eventstock during LIVE, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        stocksAsked: if es has an ask price
        """
        targetId = es
        mapped = []

        for stock in eventStocks:
            projection = eventStocks[stock].get('fantasy_points_projected_live')
            projection = eventStocks[stock]["fantasy_points_projected"] if projection == None else projection
            gap = np.random.normal(2.71**(-5*projection/100-0.25), (2.71**(-5*projection/100-0.25))/20) * (1 - amountComplete)
            #gap = random.uniform(0.05, 0.1) * (1 - amountComplete)
            #print(f'gap for {eventStocks[stock]["stock"]["name"]} is {gap}')
            if self.LIVEconservative == True:
                projection = projection * (1 - gap) if targetId == stock else projection
            else:
                projection = projection * (1 + gap) if targetId == stock else projection
            if stock == targetId:
                targetBidProj = projection
            mapped.append((stock, projection))
        print(f'We project {eventStocks[targetId]["stock"]["name"]} to get {targetBidProj}')
        mapped.sort(key = lambda x: x[1])
        mapped.reverse()

        buyingIndex = mapped.index((targetId, targetBidProj))
        impliedLowPayout = float(valuations[buyingIndex]['amount'])
        lowWithChatter = round(self.randn_bm(impliedLowPayout * 0.90, impliedLowPayout * 0.99), 2)
        minValuation = valuations[-1]
        bid = max(float(minValuation['amount']), lowWithChatter)
        shareCount = 1
        print(f'We value {eventStocks[targetId]["stock"]["name"]} at {bid}')

        if stockAsked == True:
            askPrice = float(eventStocks[targetId]['ask_price'])
            if bid < askPrice:
                print(f'Price for {eventStocks[targetId]["stock"]["name"]} is too high ({askPrice})')
                return
        else:
            askPrice = lowWithChatter * (1 - random.uniform(0.05, 0.1))
            print('This stock is for last price, not ask price') 

        newBid = round(askPrice, 2)
        if self.balance - newBid * shareCount * 1.05 < 0:
            print(f'Skipping bid for {eventStocks[es]["stock"]["name"]}, {shareCount} @ {newBid} close to available currency {self.balance}')
            return
        print(f'Bidding for {shareCount} share(s) of {eventStocks[es]["stock"]["name"]} at {newBid}, implied payout of {impliedLowPayout}')
        try:
            self.createOrder(targetId, 'BUY', 'LIVE', shareCount, newBid, stockAsked)
        except:
            print('Placing buy order failed')

    def placeIPOBid(self, es, eventStocks, valuations):
        """
        Determines if we should BID on an eventstock during IPO, calls createOrder if we should

        Parameters
        es: eventstock_id of the stock
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        amountComplete: amount that es's game is complete
        """
        targetId = es
        prefOffset = np.random.normal(0.25, 0.05)
        mapped = [] 

        for stock in eventStocks:
            projection = eventStocks[stock]['fantasy_points_projected']
            prefOffset = np.random.normal(2.71**(-5*projection/100-0.25), (2.71**(-5*projection/100-0.25))/20)
            if self.IPOconservative == True:
                projection = projection * (1 - prefOffset) if targetId == stock else projection
            else:
                projection = projection * (1 + prefOffset) if targetId == stock else projection
            if stock == targetId:
                targetProj = projection
            mapped.append((stock, projection))
        mapped.sort(key = lambda x: x[1]) 
        mapped.reverse()

        index = mapped.index((targetId, targetProj))
        print(f'This is index: {index}')
        impliedPayout = 0 if index >= len(valuations) else float(valuations[index]['amount'])
        bidWithChatter = round(self.randn_bm(impliedPayout * 0.9, impliedPayout * 1.1), 2)
        minValuation = valuations[-1]
        bid = max(float(minValuation['amount']), bidWithChatter)
        if eventStocks[es].get('last_price', None):
            if float(eventStocks[es]['last_price']) >= bid:
                print(f'Skipping bid for {eventStocks[es]["stock"]["name"]}, last price {eventStocks[es]["last_price"]} higher than max bid {bid} target {impliedPayout}')
                return
        else:
            print("No last price")
            return
        shareCount = 1
        if self.balance - bid * shareCount  * 1.05 < 250 - self.maxIPOSpending:
            print(f'Skipping bid for {eventStocks[es]["stock"]["name"]}, {shareCount} @ {bid} because it exceeds our maxIPOSpending of {self.maxIPOSpending}')
            return
        print(f'Bidding for {shareCount} share(s) of {eventStocks[es]["stock"]["name"]} at {float(eventStocks[es]["last_price"])} (target of {valuations[index]["amount"]} before timing & chatter)')

        try:
            self.createOrder(targetId, 'BUY', 'IPO', shareCount, round(float(eventStocks[es]["last_price"]), 2), None)
        except:
            print('IPO Bidding failed...')

    
    def calculateBidProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should BID on during LIVE (those that don't have ask price)

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksLastPrice = {eventStock: eventStocks[eventStock].get('last_price') for eventStock in eventStocks if 'ask_price' not in eventStocks[eventStock]}
        ranking = self.simulator.fetchRanking(wantNames = False)
        profitableStocks = []

        for rank in range(len(ranking)):
            stock = ranking[rank][0]
            if stock in eventStocksLastPrice and stock not in self.priceOfBids:
                profit = (float(valuations[rank]['amount']) - float(eventStocksLastPrice[stock])) / float(eventStocksLastPrice[stock])
                profit = profit * (1 + math.log(self.simulator.amountComplete(stock) + 0.1, 50))
                profitableStocks.append(( 
                    stock,
                    profit,
                    {
                        'last_price': float(eventStocksLastPrice[stock]),
                        'valuation': float(valuations[rank]['amount']),
                        'fantasy points projected': float(ranking[rank][1]),
                        'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored', 0)),
                        'amt_complete': self.simulator.amountComplete(stock)
                    }
                ))
        profitableStocks.sort(key = lambda x: x[1], reverse = True)
        profitableStocks = profitableStocks[:random.randint(1, 5)]
        profitableStocks = {stockProfit[0]: stockProfit[1:] for stockProfit in profitableStocks}
        print(f'Best stocks to bid on are {self.showPlayers(profitableStocks)}')
        return profitableStocks

    def calculateBuyProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should BUY during LIVE (those that have ask price)

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksAsked = {eventStock: eventStocks[eventStock].get('ask_price') for eventStock in eventStocks if 'ask_price' in eventStocks[eventStock]}
        ranking = self.simulator.fetchRanking(wantNames = False)
        profitableStocks = []

        for rank in range(len(ranking)):
            stock = ranking[rank][0]
            if stock in eventStocksAsked and (stock, round(float(eventStocksAsked[stock]), 2)) not in self.liveHoldingsPrice:
                profit = (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / float(eventStocksAsked[stock])
                weight = (math.pow(2, (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / 10) - 1)
                profit = profit * (1 + weight)
                profit = profit * (1 + math.log(self.simulator.amountComplete(stock) + 0.2, 50)) #timing offset
                prefOffset = random.uniform(0.05, 0.10)
                profit = profit * (1 + prefOffset) if eventStocks[stock]['stock']['details']['position'] in self.prefPositions else profit 
                profit = profit if rank in self.prefRanks else profit * (1 - prefOffset)
                riskAdd = np.random.normal(0, 0.0125)
                risk = self.buyRisk + riskAdd
                if profit > risk:
                    profitableStocks.append((
                        stock,
                        profit,
                            {
                            'ask price': float(eventStocksAsked[stock]), 
                            'valuation': float(valuations[rank]['amount']),
                            'fantasy points projected': float(ranking[rank][1]),
                            'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored', 0)),
                            'weight': weight,
                            'amt_complete': self.simulator.amountComplete(stock)
                            }       
                    )) 
        profitableStocks.sort(key = lambda x: x[1], reverse = True)
        self.updateStockGraphs('BUY', profitableStocks, eventStocks)
        profitableStocks = profitableStocks[:random.randint(1, 10)] #randomly pick from 1 to 10 stocks
        profitableStocks = {stockProfit[0]: stockProfit[1:] for stockProfit in profitableStocks}
        print(f'Best stocks to buy are {self.showPlayers(profitableStocks)}')
        return profitableStocks

    def calculateIPOProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should BID during IPO

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksAsked = {eventStock: eventStocks[eventStock].get('last_price', float('inf')) for eventStock in eventStocks}
        ranking = self.simulator.fetchRanking(wantNames = False)
        profitableStocks = []

        for rank in range(len(ranking)):
            stock = ranking[rank][0]
            profit = (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / float(eventStocksAsked[stock])
            profitWeight = (math.pow(2, (float(valuations[rank]['amount']) - float(eventStocksAsked[stock])) / 10) - 1)
            profit = profit * (1 + profitWeight)
            if stock in eventStocksAsked and rank in self.prefRanks:
                profitableStocks.append((
                    stock,
                    profit,
                        {
                        'last price': float(eventStocksAsked[stock]), 
                        'valuation': float(valuations[rank]['amount']),
                        'fantasy points projected': float(ranking[rank][1]),
                        'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scored', 0))
                        }       
                )) 
        random.shuffle(profitableStocks)
        profitableStocks = profitableStocks[:random.randint(1, 10)] #randomly pick from 1 to 10 stocks
        profitableStocks = {stockProfit[0]: stockProfit[1:] for stockProfit in profitableStocks}
        print(f'Best IPO stocks are {self.showPlayers(profitableStocks)}')
        return profitableStocks

    def calculateSellProfits(self, eventStocks, valuations):
        """
        Ranks eventstocks we should SELL during LIVE

        Parameters
        eventStocks: eventStocks during current_iteration
        valuations: payouts for the event 
        """
        eventStocksBid = {eventStock: eventStocks[eventStock].get('bid_price', 0) for eventStock in eventStocks}
        ranking = self.simulator.fetchRanking(wantNames = False)
        profitableStocks = []

        for rank in range((len(ranking))):
            stock = ranking[rank][0]
            profit = (float(eventStocksBid[stock]) - float(valuations[rank]['amount'])) / float(valuations[rank]["amount"])
            profitWeight = (math.pow(2, (float(eventStocksBid[stock]) - float(valuations[rank]['amount'])) / 10) - 1)
            profit = profit * (1 + profitWeight)
            profit = profit * (1 + math.log(self.simulator.amountComplete(stock) + 0.2, 50)) #timing offset
            inHoldings = (stock in self.IPOHoldings and self.IPOHoldings[stock] > 0) or (stock in self.LIVEHoldings and self.LIVEHoldings[stock] > 0)
            riskAdd = np.random.normal(0, 0.0125)
            risk = self.sellRisk + riskAdd
            if inHoldings and stock in eventStocksBid and (stock, round(float(eventStocksBid[stock]), 2)) not in self.liveSellingsPrice and profit > risk:
                profitableStocks.append((
                    stock,
                    profit,
                    {
                    'bid price': float(eventStocksBid[stock]),
                    'valuation': float(valuations[rank]['amount']),
                    'fantasy points projected': float(ranking[rank][1]),
                    'actual fantasy points': float(eventStocks[stock].get('fantasy_points_scores', 0))
                    }
                ))     
        profitableStocks.sort(key = lambda x: x[1], reverse = True)
        self.updateStockGraphs('SELL', profitableStocks, eventStocks)
        profitableStocks = profitableStocks[:random.randint(1, 5)] #randomly pick from 1 to 5 stocks
        profitableStocks = {stockProfit[0]: stockProfit[1:] for stockProfit in profitableStocks}
        print(f'Stocks to sell are {self.showPlayers(profitableStocks)}')
        return profitableStocks
        
    def submitLiveBids(self):
        """
        Calls placeLiveBid for eventstocks from calculate profit functions
        """
        if self.simulator.fetchPhase() == "LIVE":
            print(f'In LIVE...')
            eventStocks = self.simulator.fetchEventStocks()
            valuations = self.simulator.fetchEventStockPayouts()
            
            askedStocks = self.calculateBuyProfits(eventStocks, valuations)
            notAskedStocks = self.calculateBidProfits(eventStocks, valuations)

            
            keyAskedStocks = {stock: eventStocks[stock] for stock in askedStocks}
            for es in keyAskedStocks:
                amountComplete = self.simulator.amountComplete(es)
                self.placeLiveBid(es, eventStocks, valuations, amountComplete, stockAsked = True)

            keyNotAskedStocks = {stock: eventStocks[stock] for stock in notAskedStocks}
            for es in keyNotAskedStocks:
                amountComplete = self.simulator.amountComplete(es)
                self.placeLiveBid(es, eventStocks, valuations, amountComplete, stockAsked = False)
        else:
            print('Skipping LIVE offers...')

    def submitLiveOffers(self):
        """
        Calls placeLiveOffer for eventstocks from calculate profit functions
        """
        if self.simulator.fetchPhase() == "LIVE":
            print(f'In LIVE...')
            eventStocks = self.simulator.fetchEventStocks()
            valuations = self.simulator.fetchEventStockPayouts()

            profitableStocks = self.calculateSellProfits(eventStocks, valuations)
            keyStocks = {stock: eventStocks[stock] for stock in profitableStocks}
            for es in keyStocks:
                amountComplete = self.simulator.amountComplete(es)
                self.placeLiveOffer(es, eventStocks, valuations, amountComplete)
        else:
            print('Skipping LIVE buys...')

    def submitIPOBids(self):
        """
        Calls placeIPOBid for eventstocks from calculate profit functions
        """
        if self.simulator.fetchPhase() == "IPO":
            print(f'In IPO...')
            eventStocks = self.simulator.fetchEventStocks()
            valuations = self.simulator.fetchEventStockPayouts()
        
            eventStocksToBuy = [es for es in eventStocks]
            if len(eventStocksToBuy) == 0:
                print(f'No stocks to buy')
                return

            profitableStocks = self.calculateIPOProfits(eventStocks, valuations)
            keyStocks = {stock: eventStocks[stock] for stock in profitableStocks}
            for es in keyStocks:
                self.placeIPOBid(es, eventStocks, valuations)
        else:
            print('Skipping IPO...')

    def runBot(self):
        """
        Runs bots
        """
        while True:
            self.simulator.simulate()
            self.updateIPOHoldings()
            self.updateBids()
            self.submitIPOBids()
            self.submitLiveBids()
            self.submitLiveOffers()
            if self.simulator.fetchIfDone() == True:
                self.earnings = self.simulator.calcEarnings(self.IPOHoldings) + self.simulator.calcEarnings(self.LIVEHoldings) + self.balance
                print('Closing bot')
                print(f'Final balance is: {self.earnings}')
                return 
        


e1 = "evt_1a341f55f12d099b714af8b82c3205c9"
e2 = "evt_d95b8e01de0284c3e957cccf865444c5"
e3 = "evt_c1e04a4f3003dce1549aafec89224dc1"
e4 = "evt_e369b5a56fadc620"
e5 = "evt_bea1906a6b41b872"
e6 = "evt_11e77bcdb4362e13"
e7 = "evt_0fe9902c2f1c72ae"