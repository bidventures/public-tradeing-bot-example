import sys
sys.path.append("../jockmktbot/")
import firebase_admin
from firebase_admin import db
import random
import time
import json 
import os

class Simulator:
    def __init__(self, eventID = None):
        """
        Simulator constructor used to load in data for bots_with_event_simulator

        Parameters
        eventID: name of screen capture file for an event, contained in screenCaptureData

        Initializes eventStocks, data, and LIVEStart
        """
        self.valuations = [{'position': 0, 'amount': '50.0000'}, {'position': 1, 'amount': '40.0000'}, {'position': 2, 'amount': '32.0000'}, {'position': 3, 'amount': '27.0000'}, {'position': 4, 'amount': '24.0000'}, {'position': 5, 'amount': '22.0000'}, {'position': 6, 'amount': '20.0000'}, {'position': 7, 'amount': '18.0000'}, {'position': 8, 'amount': '17.0000'}, {'position': 9, 'amount': '16.0000'}, {'position': 10, 'amount': '15.0000'}, {'position': 11, 'amount': '14.0000'}, {'position': 12, 'amount': '13.0000'}, {'position': 13, 'amount': '12.0000'}, {'position': 14, 'amount': '11.0000'}, {'position': 15, 'amount': '10.5000'}, {'position': 16, 'amount': '10.0000'}, {'position': 17, 'amount': '9.0000'}, {'position': 18, 'amount': '8.5000'}, {'position': 19, 'amount': '8.0000'}, {'position': 20, 'amount': '7.5000'}, {'position': 21, 'amount': '7.0000'}, {'position': 22, 'amount': '6.5000'}, {'position': 23, 'amount': '6.0000'}, {'position': 24, 'amount': '5.5000'}, {'position': 25, 'amount': '5.0000'}, {'position': 26, 'amount': '4.6700'}, {'position': 27, 'amount': '4.3400'}, {'position': 28, 'amount': '4.0000'}, {'position': 29, 'amount': '3.6700'}, {'position': 30, 'amount': '3.3400'}, {'position': 31, 'amount': '3.0000'}, {'position': 32, 'amount': '2.6700'}, {'position': 33, 'amount': '2.3400'}, {'position': 34, 'amount': '2.0000'}, {'position': 35, 'amount': '1.0000'}, {'position': 36, 'amount': '1.0000'}, {'position': 37, 'amount': '1.0000'}, {'position': 38, 'amount': '1.0000'}, {'position': 39, 'amount': '1.0000'}, {'position': 40, 'amount': '1.0000'}, {'position': 41, 'amount': '1.0000'}, {'position': 42, 'amount': '1.0000'}, {'position': 43, 'amount': '1.0000'}, {'position': 44, 'amount': '1.0000'}, {'position': 45, 'amount': '1.0000'}, {'position': 46, 'amount': '1.0000'}, {'position': 47, 'amount': '1.0000'}, {'position': 48, 'amount': '1.0000'}, {'position': 49, 'amount': '1.0000'}]
        print(f'Initializing DB...')
        self.eventRef = self.initData(eventID)
        print(f'Initializing EventStocks...')
        self.eventStocks = self.initEventStocks()


        print(f'Cleaning data...')
        self.data, self.numIterations = self.getData()
        self.LIVEStart = self.getLIVEStart()
        self.currentIteration = 0
        self.isDone = False
        
        
    def initData(self, eventID):
        """
        Returns the screen capture data from the screenCaptureData folder 

        Parameters
        eventID: name of screen capture file for an event, contained in screenCapture Folder (str)
        """
        if eventID is None:
            randomEvent = random.choice(os.listdir('screenCaptureData'))
            eventID = os.path.splitext(randomEvent)[0]
        
        with open(f'screenCaptureData/{eventID}.json','r') as fp:
            return dict(json.load(fp))
            
    def initEventStocks(self):
        """
        Returns eventStocks: dictionary mapping eventstock_id to eventstock information at current iteration (initially None)
        """
        currentEventStocks = {event: None for event in self.eventRef}
        return currentEventStocks

    def fetchEventStocks(self):
        return self.eventStocks
    
    def fetchEventStockPayouts(self):
        return self.valuations

    def fetchPhase(self):
        if self.currentIteration >= self.LIVEStart:
            return "LIVE"
        else:
            return "IPO"
    
    def fetchIfDone(self):
        return self.isDone
    
    def fetchIteration(self):
        return self.currentIteration
    
    def fetchRanking(self, iteration = None, wantNames = True):
        """
        Helper function used to rank eventstocks at some iteration of simulation

        Parameters
        iteration: iteration of simulation wanted (int)
        wantNames: if we want to see eventstock name with points projected (True or False)

        Returns an ordered list of either (eventstock_id, projected points) or (names, projected points)
        """
        if iteration == None: 
            iteration = self.currentIteration
        ranked = []
        for stock in self.eventStocks:
            projectLive = self.data[stock][iteration-1][1].get('fantasy_points_projected_live') 
            pointsProjected = projectLive 
            projectNotLive = self.data[stock][iteration-1][1]['fantasy_points_projected']
            pointsProjected = projectNotLive if pointsProjected == None else pointsProjected 
            if wantNames == True:
                ranked.append((self.data[stock][iteration-1][1]["stock"]["name"], pointsProjected))     
            else:
                ranked.append((stock, pointsProjected))
        ranked.sort(key = lambda x: x[1], reverse = True)
        return ranked
    def getData(self):
        """
        Returns eventstock information sorted on time: dictionary of {stock1: [(time1, data1), (time2, data2), ...], stock2: [(time1, data1),...]}
        """
        masterDict = {}  # {stock1: [(time1, data1), (time2, data2)]}
        iterations = float('inf')

        for stock in self.eventStocks:
            masterDict[stock] = []
            stockRef = self.eventRef[stock]
            for dataPoint in stockRef.values():
                masterDict[stock].append([dataPoint['time'], dataPoint])
            masterDict[stock].sort(key = lambda x: x[0]) #sort based on time
            iterations = min(iterations, len(masterDict[stock])) #make sure to have the stock w the min # of data points as # of iterations
        return masterDict, iterations
                    
    def reset(self):
        """
        Resets the simulation, used by the bot's resetBot()
        """
        print(f'Resetting simulation...')
        self.currentIteration = 0
        self.isDone = False
        resetStocks = {stock: None for stock in self.eventStocks}
        self.eventStocks = resetStocks
    def getLIVEStart(self):
        """
        Returns the iteration when event goes live (when fantasy_points_scored is first seen)
        """
        LIVEStart = float('inf')
        for randomStock in self.data:
            for iteration in range(len(self.data[randomStock])):
                if 'fantasy_points_scored' in self.data[randomStock][iteration][1]:
                    if iteration < LIVEStart:
                        LIVEStart = iteration
        return LIVEStart

    def simulate(self):
        """
        Simulates one iteration of the simulation, prints out ranking at end of simulation
        """
        print('Simulating one iteration...')
        if self.currentIteration != self.numIterations:
            print(f'On iteration {self.currentIteration} out of {self.numIterations}')
            for stock in self.eventStocks:
                self.eventStocks[stock] = self.data[stock][self.currentIteration][1] #update stocks to the next iteration 
            print("-----------------------------------------------------------------------------")
            self.currentIteration +=1
        else:
            self.isDone = True
            print('Simulation has ended')
            rank = [(self.eventStocks[stock]["stock"]["name"], self.eventStocks[stock].get("fantasy_points_projected_live", None)) for stock in self.eventStocks]
            sort_rank = sorted(rank, key = lambda x: x[1], reverse = True)
            final_rankings = [{'name': i[0], 'fantasy points': i[1], 'valuation': float(self.valuations[e]['amount'])} for e, i in enumerate(sort_rank)]
            print(f'Final Rankings:')
            for place in final_rankings:
                print(place)
        
    def calcEarnings(self, holdings):
        """
        Returns the amount earned from holdings

        Parameters
        holdings: dictionary mapping stockevent_id (str) to # of shares (int)
        """
        ranked = self.fetchRanking(iteration = self.numIterations, wantNames = False) #rankings on last iteration
        rank = {j[0]: float(self.valuations[i]['amount']) for i, j in enumerate(ranked)}
        score = 0
        for stock_id, shares in holdings.items():
            if stock_id in rank:
                score += rank[stock_id]*shares
        return score

        

        

        

