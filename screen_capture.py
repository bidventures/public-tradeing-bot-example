from bots import Bot
import firebase_admin
from firebase_admin import db
import datetime
import json
import time

class Capture(Bot):
    def __init__(self, account = None):
        """
        Intialize the screen capture with an account
        """
        if account == None:
            self.account = ['datacap@jockmkt.com', 'Datacapturepassword1', ('data', 'cap'), 'datacap']
        else:
            self.account = account
        super().__init__({}, self.account)

    def initFirebase(self):
        """
        Initialize the firebase db to record data
        """
        cred = firebase_admin.credentials.Certificate(('./dbkey/key.json'))
        firebase_admin.initialize_app(cred, {'databaseURL' : 'https://jockmktbot.firebaseio.com/'})
        return db.reference() #root

    def captureLiveBids(self):
        try:
            userEvents = self.fetchUserEvents()
        except Exception as e:
            print(f'Did not get user events at LIVE because of error {e}')
            return
        userEventsLive = [ue for ue in userEvents if ue['event']['status'] == 'LIVE']

        for ue in userEventsLive:
            print(f'Capturing {ue["event"]["name"]} ({ue["event_id"]})')
        
            # fetch data we need
            try:
                eventStocks = self.fetchEventStocks(ue['event_id'])
            except Exception as e:
                print(f'Did not get event stocks because of error {e}')
            newRoot = self.root.child(ue['event_id'])
            for es in eventStocks:
                es['time'] = datetime.datetime.now().isoformat()
                newRoot.child(es['stock_id']).push(es)

    def captureIPOBids(self):
        try:
            userEvents = self.fetchUserEvents()
        except Exception as e:
            print(f'Did not get user events at IPO because of error {e}')
            return
        userEventsinIPO = [ue for ue in userEvents if ue['event']['status'] == 'IPO']

        for ue in userEventsinIPO:
            try:
                eventStocks = self.fetchEventStocks(ue['event_id']) 
            except Exception as e:
                print(f'Did not get event stocks because of error {e}')
            newRoot = self.root.child(ue['event_id'])
            for es in eventStocks:
                es['time'] = datetime.datetime.now().isoformat()
                newRoot.child(es['stock_id']).push(es)
        
    def runCapture(self):
        print(f'Running capture')
        
        # Phase One: Join Available Events
        print('Checking events to join...')
        try:
            self.joinAvailableEvents()
            print('Joined available events')
        except Exception as e:
            print(f'Unable to join events: error {e}')

        # Phase Two: Capture IPO Bids 
        print('Checking bids in IPO')
        try:
            self.captureIPOBids()
            print('IPO bids entered...')
        except Exception as e:
            print(f'Unable to capture IPO bids: error {e}')

        # Phase Three: Capture Live Bids
        print('Checking bids in LIVE')
        try:
            self.captureLiveBids()
            print('LIVE bids entered...')
        except Exception as e:
            print(f'Unable to capture Live bids: error {e}')

    def screenCapture(self):
        try:
            print(f'Initializing firebase')
            self.root = self.initFirebase()
            print(f'Initialized firebase')
        except:
            print(f'Could not initialize firebase, quitting...')
            return
        count = 1
        while True:
            print(f'Running loop #{count}')
            self.runCapture()
            print('Sleeping for 15 seconds...')
            time.sleep(15)
            count += 1

if __name__== "__main__":
    c = Capture()
    c.screenCapture
    pass