import requests

from atrscraper import ATRScraper
from race import Race
from rpscraper import RPScraper
from abandonedcatcher import AbandonedRaceCatcher
from bs4 import BeautifulSoup as BS
from bs4 import Comment
import time
import headerProxy

from tpdexception import TPDError

class RDScraper:
    def __init__(self, raceday=None):
        if raceday is not None:
            self.url = f"https://www.attheraces.com/racecards/{raceday.location}/{raceday.date}"

            r = requests.get(self.url, headers = headerProxy.chromeHeader)
            print(self.url)
            while int(r.status_code) != 200:
                print(f"Recieved {r}: Sleeping for 2s and retrying.")
                time.sleep(2)
                r = requests.get(self.url)

            soup = BS(r.content, "html.parser")

            aban_catcher = AbandonedRaceCatcher(raceday)

            for r in soup.find_all("div", class_="flex--tablet"):
                time_as_string = r.find("b").getText().split()[0].replace(":", "")

                try:
                    if aban_catcher.abandoned_races[time_as_string]:
                        print(f"Race abandonded at {time_as_string}")
                        continue

                except KeyError:
                    continue

                raceday.race_times.append(time_as_string)

                print(
                    f"{raceday.location}, {raceday._year}, {raceday._month}, {raceday._day}, {time_as_string}"
                )

                # raceday.races['Test Key'] = Race('Newcastle', 2020, 6, 4, 1300)
                raceday.races[time_as_string] = Race(
                    raceday.location,
                    raceday._year,
                    raceday._month,
                    raceday._day,
                    time_as_string,
                )

            print(raceday.races)
            
            # raceday.raceday_id = f"{raceday._year}_{raceday._month}_{raceday.date[0:2]}_{raceday.location}" 
            date_id = str(raceday._date).replace('-', '_')
            raceday.raceday_id = f"{date_id}_{raceday.location}" 
            
            ats = ATRScraper()

            for _, race in raceday.races.items():
                try:
                    ats.scrape(race)
                    race.race_id = f"{date_id}_{raceday.location}_{race.time}"
                    rps = RPScraper(race)
                    rps.scrape(race)
                except TPDError:
                    continue
        else:
            print("Raceday is none, call scrape() on a raceday.")

    def scrape(self, raceday):
        print("DEPRECATED -- DOES NOT WORK.")
        self.url = (
            f"https://www.attheraces.com/racecards/{raceday.location}/{raceday.date}"
        )

        r = requests.get(self.url, headers = headerProxy.chromeHeader)

        soup = BS(r.content, "html.parser")

        for r in soup.find_all("h2", class_=["h4", "push--xx-small"]):
            time_as_string = r.find("b").getText().split()[0]
            raceday.race_times.append(time_as_string.replace(":", ""))
