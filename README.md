# jockmktbot

## How to Setup and Use the Trading Bots

The Bot class in **`bots.py`** has all the logic for trading within the app.

The bot has adjustable behavior using the following parameters:
1. maxIPOSpending - Max amount of coins the bot is willing to spend during the IPO phase (int range: [0, 250] -> default: 0)
2. buyRisk - How risky the bot will be when making decisions about bids, lower values = more risky (float range: [0, 1] -> default: 0.1)
3. sellRisk - How risky the bot will be when making decisions about offers, lowers values = less risky (float range: [0, 1] -> default: 0.1)
4. prefRanks - What tier of players the bot will prefer to target at IPO, the groups of ranks are initialized when we join an event with tier 0 being highest rank (list of ints range: [0, 5] -> default: [0, 1, 2, 3, 4, 5]) 
5. IPOconservative - A measure of whether or not the bot will be conservative during the IPO phase (True or False -> default: False)
6. LIVEconservative - A measure of whether or not the bot will be conservative during the LIVE phase (True or False -> default: False)

To initialize and run a single bot:
1. In **`bots.py`** initialize a Bot instance with your desired parameters and account information
2. Call the .run() function of your Bot instance in a loop
```python
account = [EMAIL, PASSWORD, (FIRST, LAST), USERNAME]
params = {'maxIPOSpending': 150, 'prefRanks': [2, 3]}
b = Bot(params, account)

b.run() # runs the bot once - to continuously run the bot use .run() within a loop
```

To initialize and run multiple bots:
1. In **`accounts.json`**: Follow the structure of the other bots and add your desired parameters 
2. Run **`run.py`**

```javascript
{
    "7": {
            "email": "email@email.com", 
            "password": "password", 
            "name": {"first": "Jock", "last": "Market"}, 
            "username": "jockmkt", 
            "params": {
                "maxIPOSpending": 250, 
                "prefRanks": [1, 5],
                "sellRisk": 0.1,
                "buyRisk": 0.1,
                "IPOcsv": false,
                "LIVEcsv": false
            }
    }
}
```

## Folders/Files

#### Folders

### firebase

- **`firebase_retrieve.ipynb`** : steps to retrieve certain datapoints from collected data on firebase database.

### projectionData

- **`ESPN FF 2019 ProjActual`** : 2019 projected fantasy score vs actual fantasy score in ESPN's NFL Fantasy League.

### pythonBotStructure

- **`trial.py`** : original bot structure for v0.2 in the API.
- **`v1_trial.py`** : original bot structure for v1 in the API.

### screenCaptureData

- JSON data for events in firebase database. Data is analyzed/used in **`plots.ipynb`**.

### simulationData

- CSV files with data created from running through all bot parameter permutations across events. Data is analyzed in python notebook **`botsparams.ipynb`**. 
- **`sim5.csv`** and **`sim6.csv`** are the most recent simulations.

#### Files
- **`accounts.json`** : stores bots information and parameters

- **`bot_strategy.pdf`** : description of bot strategy

- **`bots_with_event_simulator.py`** : bots to be used with the event simulator in **`event_simulator.py`**. Initialized by: 
```python
params = {'maxIPOSpending': 150, 'buyRisk': 0.1, 'sellRisk': 0.1}
s = sim('evt_e369b5a56fadc620') #code to run bot on simulated data from event evt_e369b5a56fadc620
b = Bot(params, s)
b.runBot()
b.earnings #call to check the earnings of the bot
b.resetBot()
```
- **`bots.py`** : structure of bots and methods to interact with API

- **`botsparams.ipynb`** : notebook with analysis of simulation data

- **`event_simulator.py`** : used to simulate captured data

- **`parameterbot.py`** : runs simulations for all possible permutations of bots

- **`plots.ipynb`** : notebook with functions to create player plots, multiple player value charts, and overall performance by rank

- **`run.py`** : runs all bots in accounts.json

- **`screen_capture.py`** : captures event stock data from within app and writes to firebase database# public-tradeing-bot-example
