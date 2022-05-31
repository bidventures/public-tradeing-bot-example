import requests
import json
import random
import math
import datetime
URL_STEM = 'https://stage.api.jockmkt.net/v1'

defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

accountTokens = {}
accounts = []
#umarbek@jockmkt.com
#testpass123_
t_2 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfNjQ5ZjFlOWMxY2Q4OGEzOTJjYmIxYmViNjZiMzMyODkiLCJyb2xlIjoiYXBwX3VzZXIiLCJpYXQiOjE1Nzg0MjcwNTgsIm5iZiI6MTU3ODQyNzA1OCwiZXhwIjoxNTgxMDE5MDU4fQ.oS0GnEQbuMF_fKDXApA8XOtrvE6STcrd44oZarnqUt4'
event0_2 = 'evt_d95b8e01de0284c3e957cccf865444c5'

t_1 = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfNGIzYjA3NjcwYmRlOGY1ZDNmZmQ1NzExY2NlODdjMDIiLCJyb2xlIjoiYXBwX3VzZXIiLCJpYXQiOjE1Nzg1ODU5MDEsIm5iZiI6MTU3ODU4NTkwMSwiZXhwIjoxNTgxMTc3OTAxfQ.7Nrq_l78JJGhyFrUDmLJVIWqgKlLl57gufYjqgnfzC4'
event0_1 = 'evt_b5a2b055098283e93da42b99da86cc07'

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfYjJiMDc2ODQ5YjVhOWMzZGVlNTU3Y2NmZTAwMDZjYjkiLCJyb2xlIjoiYXBwX3VzZXIiLCJpYXQiOjE1Nzg2NzI1MjcsIm5iZiI6MTU3ODY3MjUyNywiZXhwIjoxNTgxMjY0NTI3fQ.MAbyP8BOKLg4BnGcoP0zZGR_1z94mQaZs4XoiXIeGFc'
testliveevent = 'evt_4deee6a46d49dc634036ee6aafe6f371'

def getFetchHeaders(token=None):
    if token: 
        return {**defaultHeaders,**{'Authorization':f'Bearer {token}'}}
    else:
        return defaultHeaders

def randn_bm(min, max, skew = 1):
    u, v = 0, 0
    while u == 0: u = random.random()
    while v == 0: v = random.random()
    num = math.sqrt(-2*math.log(u))*math.cos(2*math.pi*v)
    num = (num/10) + .5
    if (num > 1 or num < 0):
        num = randn_bm(min, max, skew)
    num = math.pow(num, skew)
    num *= max - min
    num += min
    return num

    

def fetchHoldings(token):
    url = f'{URL_STEM}/holdings'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch error {resp.status_code}')
    try:
        r = resp.json()['holdings']
    except:
        raise Exception(f'Holdings fetch error')
    return r


def fetchDiscover(token):
    url = f'{URL_STEM}/discover'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch error {resp.status_code}')
    try:
        r = resp.json()['discover']
    except:
        raise Exception(f'Discover fetch error')
    return r

def fetchEventStocks(token, eventId):
    url = f'{URL_STEM}/events/{eventId}/event_stocks'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch error {resp.status_code}')
    try:
        r = resp.json()['event_stocks']
    except:
        raise Exception(f'Discover fetch error')
    return r

def joinContest(token, eventId):
    url = f'{URL_STEM}/contest_entries'
    data = {
        'event_id': eventId
    }
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch error {resp.status_code}')

def cancelOrder(token, orderId):
    url = f'{URL_STEM}/orders/{orderId}'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.delete(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch error {resp.status_code}')

# test_account = [account@gmail.com, password, (first, last), user]
def fetchAccessToken(email, password):
    url = f'{URL_STEM}/oauth/tokens'
    data = {
        'grant_type': 'password',
        'username': email,
        'password': password,
        'client_id': 'jmk_ios'
    }
    headers = defaultHeaders
    timeout = 10000
    resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')
    try:
        r = resp.json()['token']['access_token']
    except:
        raise Exception(f'Token fetch error')
    return r

def fetchBalances(token):
    url = f'{URL_STEM}/balances'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')
    try: 
        r = resp.json()['balances']
    except: 
        raise Exception(f'Token fetch error')
    return r

def fetchActiveOrders(token):
    url = f'{URL_STEM}/orders?active=true&limit=50'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')
    try: 
        r = resp.json()['orders']
    except: 
        raise Exception(f'Token fetch error')
    return r

def fetchUserEvents(token):
    url = f'{URL_STEM}/account/events?limit=50'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')
    try: 
        r = resp.json()['user_events']
    except: 
        raise Exception(f'Token fetch error')
    return r

def fetchEventStockPayouts(token, eventID):
    url = f'{URL_STEM}/events/{eventID}/payouts'
    headers = getFetchHeaders(token)
    timeout = 10000
    resp = requests.get(url = url, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')
    try: 
        r = resp.json()['payouts']
    except: 
        raise Exception(f'Token fetch error')
    return r

def createAccount(email, first, last, display, password):
    url = f'{URL_STEM}/accounts'
    data = {
        'email': email,
        'first_name': first,
        'last_name': last,
        'display_name': display,
        'password': password
    }
    headers = defaultHeaders
    timeout = 10000
    resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')

def createOrder(token, eventstockID, side, phase, quantity, limitPrice):
    assert(side=='buy' or side=='sell')
    assert(phase=='ipo' or phase =='live')
    url = f'{URL_STEM}/orders'
    print(f'Creating order for {eventstockID}, {side} {quantity} for {limitPrice}')
    data = {
        'eventstock_id' : eventstockID,
        'side' : side,
        'type' : 'limit',
        'phase' : phase,
        'quantity' : str(quantity),
        'time_in_force' : 'gtc',
        'limit_price' : '{:.2f}'.format(limitPrice) 
    }
    headers = getFetchHeaders(token)
    timeout = 10000
    print(f'Making order')
    resp = requests.post(url = url, json = data, headers = headers, timeout = timeout)
    print(f'Resp back.. {resp}, because {resp.reason}')
    if resp.status_code != 200:
        raise Exception(f'Fetch Error {resp.status_code}')

def getJoinableEventIds(token):
    discoverSections = fetchDiscover(token)
    ids = []
    for section in discoverSections:
        if section['events']:
            for event in section['events']:
                ids.append(event['id'])
    return ids    

def joinAvailableEvents(token):
    userEvents = fetchUserEvents(token)
    ids = getJoinableEventIds(token)
    matchset = set(ue['event_id'] for ue in userEvents)
    joinableEvents = [i for i in ids if i not in matchset]
    for event_id in joinableEvents:
        joinContest(token, event_id)


def placeIPOBid(token, es, eventStocks, valuations, amountComplete, eventCurrency):
    targetId = es['id']
    mapped = [] 
    for stock in eventStocks:
        projection = stock['fantasy_points_projected']
        gap = projection * 0.1
        if stock['id'] == targetId:
            mapped.append((stock['id'], projection - gap))
            targetProj = projection - gap
        else:
            mapped.append((stock['id'], projection + gap))

    #sort to see which order we end up in
    mapped.sort(key = lambda x: x[1]) 
    mapped.reverse()

    index = mapped.index((targetId,targetProj))

    impliedPayout = float(valuations[index]['amount'])

    bidWithIPOTimingChatter = impliedPayout * 0.8 + impliedPayout * 0.2 * amountComplete

    bidWithChatter = round(randn_bm(bidWithIPOTimingChatter * 0.9, bidWithIPOTimingChatter * 1.1),2)

    #pay max of either bid w chatter or last event payout
    minValuation = valuations[-1]
    bid = max(float(minValuation['amount']),bidWithChatter)

    balances = fetchBalances(token)
    eventBalance = None
    for balance in balances:
        if balance['currency'] == eventCurrency:
            eventBalance = balance
            break

    if float(es['last_price']) and float(es['last_price']) >= bid:
        print(f'Skipping bid for {es["stock"]["name"]}, last price {es["last_price"]} higher than max bid {bid} target {impliedPayout}')
        return

    possibleShares = [1,2,3,4,5]
    random.shuffle(possibleShares)
    shareCount = possibleShares[0]

    if not eventBalance or float(eventBalance['buying_power']) - bid * shareCount  * 1.05 < 0:
        print(f'Skipping bid for {es["stock"]["name"]}, {shareCount} @ {bid} plus fees close to available currency {eventBalance["buying_power"]}')
        return
    
    print(f'Bidding for {shareCount} share(s) of {es["stock"]["name"]} at {bid} (target of {valuations[index]["amount"]} before timing & chatter)')

    try:
        createOrder(token, targetId, 'buy', 'ipo', shareCount, bid)
    except:
        print('Bidding failed...')

def placeLiveBid(token, es, eventStocks, valuations, amountComplete, eventCurrency):
    targetId = es['id']

    # project this es at the high end & the rest at the low end
    sellingMap = []
    for event in eventStocks:
        projection = event['fantasy_points_projected_live'] or event["fantast_points_projected"]
        gap = projection * 0.10 * (1 - amountComplete)
        if event["id"] == targetId:
            sellingMap.append((event["id"], projection + gap))
            targetSellProj = projection + gap
        else:
            sellingMap.append((event["id"], projection - gap))
    
    # project this es at the low end & rest at the high end 
    biddingMap = []
    for event in eventStocks:
        projection = event['fantasy_points_projected_live'] or event["fantast_points_projected"]
        gap = projection * 0.10 * (1 - amountComplete)
        if event["id"] == targetId:
            biddingMap.append((event["id"], projection - gap))
            targetBidProj = projection - gap
        else:
            biddingMap.append((event["id"], projection + gap))
    
    # sort to see which order we end up in
    sellingMap.sort(key = lambda x: x[1])
    sellingMap.reverse()

    biddingMap.sort(key = lambda x: x[1])
    biddingMap.reverse()

    # check what order we are in 
    sellingIndex = sellingMap.index((targetId,targetSellProj))
    buyingIndex = biddingMap.index((targetId,targetBidProj))

    impliedHighPayout = float(valuations[sellingIndex]['amount'])
    impliedLowPayout = float(valuations[buyingIndex]['amount'])

    highWithChatter = round(randn_bm(impliedHighPayout * 1.01, impliedHighPayout * 1.10),2)
    lowWithChatter = round(randn_bm(impliedLowPayout * 0.90, impliedLowPayout * 0.99), 2)

    minValuation = valuations[-1]
    
    bid = max(float(minValuation['amount']), lowWithChatter)

    # bid at the amount we think they are going to have 
    balances = fetchBalances(token)
    eventBalance = None
    for balance in balances:
        if balance['currency'] == eventCurrency:
            eventBalance = balance
    
    possibleShares = [1,2,3,4]
    random.shuffle(possibleShares)
    shareCount = possibleShares[0]

    if not eventBalance or float(eventBalance["buying_power"]) - bid * shareCount * 1.05 < 0:
        print(f'Skipping bid for {es["stock"]["name"]}, {shareCount} @ {bid} close to available currency {eventBalance["buying_power"]}')
        return
    
    print(f'Bidding for {shareCount} share(s) of {es["stock"]["name"]} at {bid} (range of {impliedLowPayout} to {impliedHighPayout})')

    try: 
        createOrder(token, targetId, 'buy', 'live', shareCount, bid)
    except:
        print('Placing order failed')

def placeLiveOffer(token, es, eventStocks, valuations, amountComplete, eventCurrency, sellQuantity):
    targetId = es['id']
    sellingMap = [] 
    biddingMap = []
    for stock in eventStocks:
        proj = stock['fantasy_points_projected_live'] or stock['fantasy_points_projected']
        gap = proj * 0.10 * (1 - amountComplete)
        if stock['id'] == targetId:
            targetSellingProj = proj + gap
            sellingMap.append((stock['id'], targetSellingProj))

            targetBiddingProj = proj - gap
            biddingMap.append((stock['id'], targetBiddingProj))
        else:
            sellingMap.append((stock['id'], proj - gap))
            biddingMap.append((stock['id'], proj + gap))

    sellingMap.sort(key = lambda x: x[1])
    sellingMap.reverse()
    biddingMap.sort(key = lambda x: x[1])
    biddingMap.reverse()

    sellingIndex = sellingMap.index((targetId, targetSellingProj))
    biddingIndex = biddingMap.index((targetId, targetBiddingProj))

    impliedHighPayout = float(valuations[sellingIndex]['amount'])
    impliedLowPayout = float(valuations[biddingIndex]['amount'])

    highWithChatter = round(randn_bm(float(impliedHighPayout) * 1.01, float(impliedHighPayout) * 1.10), 2)
    lowWithChatter = round(randn_bm(float(impliedLowPayout) * 0.9, float(impliedLowPayout) * 0.99), 2)

    maxValuation = valuations[0]

    offer = min(float(maxValuation['amount']), highWithChatter)

    print(f'Offering {sellQuantity} share(s) of {es["stock"]["name"]} at {offer} (range of {impliedLowPayout} to {impliedHighPayout})')
    try:
        createOrder(token, es['id'], 'sell', 'live', sellQuantity, offer)
    except:
        print('Placing order failed')

def cancelLiveOrders(token):
    activeOrders = fetchActiveOrders(token)
    ordersToCancel = [order for order in activeOrders if order['phase'] == 'LIVE']

    for order in ordersToCancel:
        print(f'Cancelling order {order["id"]}')
        cancelOrder(token, order['id'])
    
def submitLiveOffers(token):
    userEvents = fetchUserEvents(token)
    userEventsLive = [ue for ue in userEvents if ue['event']['status'] == 'LIVE']

    for ue in userEventsLive:
        print(f'Analyizing {ue["event"]["name"]} ({ue["event_id"]})')
    
        # fetch data we need
        eventStocks = fetchEventStocks(token, ue['event_id'])
        valuations = fetchEventStockPayouts(token, ue['event_id'])
        holdings = fetchHoldings(token)

        # filter out event stocks that we have orders for
        holdingsIds = {holding['eventstock_id']: holding['available'] for holding in holdings} #available might be selling_power in v2
        eventStocksToOffer = [es for es in eventStocks if es['id'] in holdingsIds]

        if len(eventStocksToOffer) == 0:
            print(f'Nothing to offer for sale from holdings in {ue["event"]["name"]} ({ue["event_id"]})')
            continue #this is different from original code

        random.shuffle(eventStocksToOffer)
        shuffledEventStocks = eventStocksToOffer

        amountComplete = ue['event']['amount_completed'] if ue['event']['amount_completed'] != None else 0

        print(f'See event is {(amountComplete * 100)}% complete... pricing holding offers...')

        for es in shuffledEventStocks[:20]:
            if es['id'] in holdingsIds:
                sharesToSell = holdingsIds[es['id']]
                placeLiveOffer(token, es, eventStocks, valuations, amountComplete, ue['event']['currency_id'], sharesToSell)
            else:
                continue

def submitLiveBids(token):
    userEvents = fetchUserEvents(token)
    userEventsLive = [ue for ue in userEvents if ue['event']['status'] == 'LIVE']

    for ue in userEventsLive:
        print(f'Analyzing {ue["event"]["name"]} ({ue["event_id"]})')
        
        eventStocks = fetchEventStocks(token, ue['event_id'])
        valuations = fetchEventStockPayouts(token, ue['event_id'])
        holdings = fetchHoldings(token)
        
        holdingsIds = {holding['eventstock_id'] for holding in holdings}
        eventStocksToBuy = [es for es in eventStocks if es['id'] not in holdingsIds]
        
        if len(eventStocksToBuy) == 0:
            print(f'Nothing to offer for sale from holdings in {ue["event"]["name"]} ({ue["event_id"]})')
            continue
        
        random.shuffle(eventStocksToBuy)
        shuffledEventStocks = eventStocksToBuy
        
        amountComplete = ue['event']['amount_completed'] if ue['event']['amount_completed'] else 0
        
        print(f'See event is {round(amountComplete * 100, 2)}% complete... pricing other bids...')
        
        for es in shuffledEventStocks[0:20]:
            placeLiveBid(token, es, eventStocks, valuations, amountComplete, ue['event']['currency_id'])

def submitIPOBids(token):
    userEvents = fetchUserEvents(token)
    userEventsinIPO = [ue for ue in userEvents if ue['event']['status'] == 'IPO']

    for ue in userEventsinIPO:
        activeOrders = fetchActiveOrders(token)
        eventStocks = fetchEventStocks(token, ue['event_id'])
        valuations = fetchEventStockPayouts(token, ue['event_id'])

        activeOrderIds = {activeOrder['eventstock_id'] for activeOrder in activeOrders}
        eventStocksToBuy = [es for es in eventStocks if es['id'] not in activeOrderIds]

        if len(eventStocksToBuy) == 0:
            print(f'Nothing to do in {ue["event"]["name"]} ({ue["event_id"]})')
            continue

        now = datetime.datetime.now()
        ipoOpen = datetime.datetime.strptime(ue['event']['ipo_open_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        ipoClose = datetime.datetime.strptime(ue['event']['live_at_estimated'], '%Y-%m-%dT%H:%M:%S.%fZ')
        
        amountComplete = (now - ipoOpen) / (ipoClose - ipoOpen)

        print(f'See IPO is {round(amountComplete*100, 2)}% complete... calculating bids...')

        random.shuffle(eventStocksToBuy)
        shuffledEventStocks = eventStocksToBuy

        for es in shuffledEventStocks[0:20]:
            placeIPOBid(token, es, eventStocks, valuations, amountComplete, ue['event']['currency_id'])


def runBots(accounts):
    for account in accounts:
        email, password, name, username = account
        first, last = name
        print(f'Running bot loop for {email}...')

        try:
            token = accountTokens[email]
        except:
            raise Exception(f'Cannot execute bot loop for {account[email]}, token missing in map')

        # Phase One: Join Available Events
        print('Checking events to join...')
        joinAvailableEvents(token)
        print('Joined available events')

        # Phase Two: Place IPO Bids 
        print('Checking events in IPO for activity')
        submitIPOBids(token)
        print('IPO bids entered...')

        # Phase Three: Cancel Live Orders -- We'll Reprice in Next Step 
        print('Cancelling live orders...')
        cancelLiveOrders(token)

        # Phase Four: Place Live Offers from Holdings
        print('Checking live events to adjust holding offers')
        submitLiveOffers(token)

        # Phase Five: Place Live Orders from Balances on Non-Owned Shares
        print('Checking live events to place orders...')
        submitLiveBids(token)

        print('Bot loop closed...')

    random.shuffle(accounts)


def bots(accounts):
    for account in accounts:
        email, password, name, username = account
        first, last = name
        try:
            print(f'Fetching access token for {email}...')
            token = fetchAccessToken(email, password)
            print(f'Got access token for {email}...')
        except:
            print(f'Failed to fetch token for {email}, trying to create account')
            createAccount(email, first, last, username, password)
            print(f'Created account for {email}, attempting to fetch token for created account...')
            token = fetchAccessToken(email, password)
            print(f'Got access token for {email} after creating account')

        accountTokens[email] = token
    runBots(accounts)


