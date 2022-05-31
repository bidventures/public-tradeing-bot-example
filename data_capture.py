from bots import Bot
import datetime
import time
import os
import csv
import argparse


class Capture(Bot):
    def __init__(self, account=None):
        """
        Intialize the screen capture with an account
        """
        if account is None:
            self.account = [
                "newdatacap@jockmkt.com",
                "Datacapturepassword2",
                ("newdata", "cap"),
                "newdatacap",
            ]
        else:
            self.account = account
        super().__init__({}, self.account)
        self.player_history = {}
        self.current_events = set()

    # def getEvents(self, sector):
    #     discoverSections = self.fetchDiscover()
    #     ids = set()
    #     for section in discoverSections:
    #         if section["events"]:
    #             for event in section["events"]:
    #                 if event["sector"] == sector and (
    #                     event["status"] == "IPO" or event["status"] == "LIVE"
    #                 ):
    #                     ids.add(event["id"])
    #     return ids

    def getEventData(self, sector):
        try:
            discoverSections = self.fetchDiscover()
            for section in discoverSections:
                if section["events"]:
                    for event in section["events"]:
                        if event["sector"] == sector and (
                            event["status"] == "IPO" or event["status"] == "LIVE"
                        ):
                            if event["id"] not in self.current_events:
                                self.current_events.add(event["id"])
                                self.initCSV([event["id"]])
                            self.getEventStockData(event)
        except Exception as e:
            print(f"error {e} could not fetch discover page, skipping...")

    def getEventStockData(self, e):
        try:
            eventStocks = self.fetchEventStocks(e["id"])
        except Exception as e:
            print(
                f"error {e} could not fetch event stocks for event {e['id']}, skipping..."
            )
            eventStocks = []
            pass
        post = []
        for es in eventStocks:
            new = (
                e["name"],
                datetime.datetime.now().isoformat(),
                es["id"],
                es["event_id"],
                es["stock"]["name"],
                es["stock"]["sector"],
                es["fantasy_points_projected"],
                es["fantasy_points_projected_live"],
                es["fantasy_points_scored"],
                es["amount_completed"],
                es["estimated_price"],
                es["last_price"],
                es["ask_price"],
                es["bid_price"],
            )
            if es["id"] not in self.player_history:
                self.player_history[es["id"]] = es["amount_completed"]
                post.append(new)
            else:
                if not self.player_history[es["id"]] == es["amount_completed"]:
                    self.player_history[es["id"]] = es["amount_completed"]
                    post.append(new)
        if post:
            print(f'posting {len(post)} eventstocks')
            self.handleCSV(e["id"], post)

    def handleCSV(self, eventId, data):
        PATH = f"./data/{eventId}.csv"
        try:
            with open(PATH, "a") as f:
                writer = csv.writer(f)
                writer.writerows(data)
        except Exception as e:
            print(f"Could not write to file {PATH} - error {e}")
            pass

    def initCSV(self, eventIds):
        if not os.path.exists("./data"):
            os.mkdir("./data")
        for ids in eventIds:
            if not os.path.exists(f"./data/{ids}.csv"):
                with open(f"./data/{ids}.csv", "w") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "name",
                            "time",
                            "id",
                            "event_id",
                            "stock_name",
                            "sector",
                            "fantasy_points_projected",
                            "fantasy_points_projected_live",
                            "fantasy_points_scored",
                            "amount_completed",
                            "estimated_price",
                            "last_price",
                            "ask_price",
                            "bid_price",
                        ]
                    )

    def runCapture(self, sector, waittime):
        count = 1
        while True:
            print(f"Running loop #{count}")
            self.getEventData(sector)
            print(f"Sleeping for {waittime} seconds...")
            time.sleep(waittime)
            count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sector code for events to capture (NBA, PGA, ...)"
    )
    parser.add_argument(
        "sector", metavar="S", type=str, nargs="?", help="NBA, PGA, NFL, etc."
    )
    args = parser.parse_args()
    sector = args.sector
    waittime = {"NBA": 30, "NFL": 30, "PGA": 600}.get(sector, 30)

    c = Capture()
    # events = c.getEvents(sector)
    # c.initCSV(events)
    c.runCapture(sector, waittime)
    pass
