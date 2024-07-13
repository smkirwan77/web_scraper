from bs4 import BeautifulSoup as BS
from bs4 import Comment
import requests
import numpy as np
from horse import Horse
from intDist import get_intDists
import headerProxy
import time

from tpdexception import TPDError

## GUVE HORSE NAMES -> Rename (CC)



class ATRScraper:
    """
    ATRScraper is a HTML scraper designed to pull sectional times from a AtTheRaces and 
    provide those sectional times to a Race class.
    """

    def __init__(self, race=None):
        if race is not None:
            # Order these are called in is important
            self.url = f"https://www.attheraces.com/racecard/{race.location}/{race.date}/{race.time}"
            self.get_sectional_html(race)

            self.give_race_horse(race)

            self.give_race_data(race)

            self.give_stride_data(race)

            self.give_sectional_tools_data(race)

            self.give_sectional_splits(race)
            
            #self.give_distance_data(race)

    def scrape(self, race):
        # print(f"{race.location}, {race.date}, {race.time}")
        self.url = f"https://www.attheraces.com/racecard/{race.location}/{race.date}/{race.time}"
        self.get_sectional_html(race)

        self.give_race_horse(race)

        self.give_race_data(race)

        self.give_stride_data(race)

        self.give_sectional_tools_data(race)

        self.give_sectional_splits(race)
        
        self.race_dist_int(race)
        
        #self.give_distance(race)
        
    def get_sectional_html(self, race):
        """Requests the HTML from self.url and pulls the RaceID"""

        if self.url is None:
            raise AttributeError("URL must not be NoneType")

        self.res = requests.get(self.url, headers = headerProxy.chromeHeader)

        print(self.res.status_code)
        if self.res.content is None:
            raise AttributeError("Get request on self.url.content is None")

        # AtTheRaces stores their RaceID, which is needed to make the GET request for the sectional times,
        # This is stored in a comment in the page. It is found, pulled, stripped, and stored.

        soup = BS(self.res.content, "html.parser")

        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        raceids = []
        
        for c in comments:
            for item in c.split("\n"):
                if "RaceID" in item:
                    raceids.append(item.strip())
        self.raceid = raceids[0].split(" ")[1]
        race.url_id = raceids[0].split(" ")[1]
        
        
        self.sectional_url = f"https://www.attheraces.com/ajax/sectionals/{self.raceid}/times?page=/racecard/{race.location}/{race.date}/{race.time}&raceid={self.raceid}"
        race.tools_url = f"https://www.attheraces.com/ajax/sectionals/{self.raceid}/tools?page=/racecard/{race.location}/{race.date}/{race.time}&raceid={self.raceid}"
        race.stride_url = f"https://www.attheraces.com/ajax/sectionals/{self.raceid}/stride?page=/racecard/{race.location}/{race.date}/{race.time}/stride-data&raceid={self.raceid}"
        race.sectional_url = f"https://www.attheraces.com/ajax/sectionals/{self.raceid}/times?page=/racecard/{race.location}/{race.date}/{race.time}&raceid={self.raceid}"
        race.distance_url = f"https://www.attheraces.com/ajax/sectionals/{self.raceid}/distanceran?page=/racecard/{race.location}/{race.date}/{race.time}&raceid={self.raceid}"
        
        
        return self.sectional_url

    def give_race_horse(self, race):
        """ Horse names scraped from AtTheRaces Sectional Times"""
        if self.sectional_url is None:

            raise ValueError("Sectional URL is not defined.")
        # sectional_data = requests.get(self.url)
        soup = BS(self.res.content, "html.parser")

        # There are 2 instances of a div with class card-body. The first has the horse information and the second
        # has the sectional times for the horse at the equivalent card entry in the alternate card-body.

        try:

            for h in soup.find_all("div", class_="card-body")[0].find_all(
                "div", class_="card-entry"
            ):
                # name of the horse and the position it finished stored.
                name = (
                    (
                        h.find("a", class_="horse__link")
                        .getText()
                        .split("\r\n")[1]
                        .strip()
                    )
                    .replace("'", "")
                    .lower()
                )
                try:
                    rp_temp = (
                        h.find("span", class_="p--large font-weight--semibold")
                        .getText()
                        .strip()
                    )

                    if  "-" in rp_temp:
                        raw_position = -1
                    
                    raw_position = int(rp_temp)

                except AttributeError:
                    break
                except ValueError:
                    raw_position = -1

                strange_pos = ["B", "F", "PU", "DQ", "RR", "U", "S", "R", None]

                result = []

                for w in strange_pos:
                    result.append(w == raw_position)
                if any(result) != True:
                    raw_position = int(raw_position)
                else:
                    raw_position = raw_position
                # extracting the age and weight of the horse, at run time.
                raw_age_and_weight = (
                    h.find("div", class_="card-cell card-cell--stats unpadded")
                    .getText()
                    .strip()
                )

                raw_age_and_weight = raw_age_and_weight.split("\n")
                weight = raw_age_and_weight[1].strip().split("-")
                weight_pounds = int(int(weight[0]) * 14 + int(weight[1]))
                age = int(raw_age_and_weight[0])
                raw_claim = np.NaN
                
                # information about the jockey, trainer, and the rating the horse was given that day.
                if len(h.find_all("span", class_="icon-text__t tooltip")) == 2:
                    raw_jockey = (
                        h.find_all("span", class_="icon-text__t tooltip")[0]
                        .getText()
                        .strip()
                    )
                    raw_trainer = (
                        h.find_all("span", class_="icon-text__t tooltip")[1]
                        .getText()
                        .strip()
                    )

                else:
                    claim_name = (
                        h.find_all("span", class_="icon-text__t")[0]
                        .find_all("span", class_="tooltip")[0]
                        .getText()
                    )
                    claim_weight = (
                        h.find_all("span", class_="icon-text__t")[0]
                        .find_all("span", class_="tooltip")[1]
                        .getText()
                    ).split('(')[1].split(')')[0]
                    raw_jockey = claim_name 
                    raw_claim = int(claim_weight)
                    raw_trainer = (
                        h.find_all("span", class_="icon-text__t tooltip")[0]
                        .getText()
                        .strip()
                    )

                raw_rating = (
                    h.find("span", class_="text-pill text-pill--steel tooltip")
                    .getText()
                    .strip()
                )
                if raw_rating == "-":
                    raw_rating = np.NaN
                else:
                    raw_rating = int(raw_rating)

                # raw_rating needs a if statement when there is no rating
                try:
                    raw_draw = int(
                        h.find("span", class_="font-weight--bold visible--inline-block")
                        .getText()
                        .strip()
                        .split("(")[1]
                        .split(")")[0]
                    )
                except:
                    raw_draw = 0

                # for national hunt races theres no draw so will have to come up with something in time
                raw_sp = (
                    (
                        h.find("div", class_="card-cell card-cell--odds unpadded")
                        .getText()
                        .strip()
                    )
                    .split(" ")[0]
                    .split("/")
                )
                if raw_sp[0] == "Evens":
                    raw_sp = 1
                else:
                    raw_sp = round(float(int(raw_sp[0]) / int(raw_sp[1])), 2)
                
                #raw_comment = (
                 #   h.find("span", class_="text-transform--capitalize-first")
                  #  .getText()
                   # .strip()
                #)

                # Horse object initialized with the scraped properties of the horse for this particular race.
                race.horses.append(
                    Horse(
                        name,
                        raw_position,
                        age,
                        weight_pounds,
                        raw_jockey,
                        raw_claim,
                        raw_trainer,
                        raw_draw,
                        raw_rating,
                        raw_sp,
                        code="flat",
                    )
                )
        except IndexError:
            pass

    def give_sectional_splits(self, race):
        i = 0
        seconds_per_unit = {"s": 1, "m": 60}

        sectional_data = requests.get(race.sectional_url, headers = headerProxy.chromeHeader)
        print(sectional_data.status_code)
        while int(sectional_data.status_code) != 200:
            print(f"Recieved {sectional_data.status_code}: Sleeping for 2s and retrying.")
            time.sleep(2)
            sectional_data = requests.get(race.sectional_url, headers = headerProxy.chromeHeader)

        soup = BS(sectional_data.content, "html.parser")

        race.sectional_split_times = {}

        try:
            i_catch = 0
            for i, h in enumerate(
                soup.find_all("div", class_="card-body")[1].find_all(
                    "div", class_="card-entry"
                )
            ):
                i_catch = i
                data = []

                if race.distance_markers is None:
                    raise TPDError("Distance Markers not present", race)

                for j, k in enumerate(race.distance_markers):
                    data.append( float(
                        [
                            section.getText()
                            for section in h.find_all("span", class_="visible")
                        ][j]
                    )
                    )
                    #race.sectional_split_times[race.horses[i].name] = data
                    time_string = (
                        h.find_all(
                            "div", class_=["card-sectional", "card-sectional--finish"]
                        )[-1]
                        .getText()
                        .strip()
                    )

                # The final time is given in the format 'Xm YY+.YYs'. In converting this we split the string into its Xm and Yx compnents.
                # The unit (m/s) is used to index a dictionary where the value of the key is the number of seconds in that unit.
                # That is s -> 1, m -> 60.
                # print(time_string.split())

                time_string_list = time_string.split()

                if len(time_string_list) != 2:
                    if "m" in time_string_list[0]:
                        time_string_list.append("0s")
                    if "s" in time_string_list[0]:
                        time_string_list.insert(0, "0m")

                    final_min, final_sec = time_string_list

                else:
                    final_min, final_sec = time_string.split()

                final_time = (
                    float(final_min[:-1]) * seconds_per_unit[final_min[-1]]
                ) + (float(final_sec[:-1]) * seconds_per_unit[final_sec[-1]])

                # This is added up and added to the end of the sectional times list for that horse.
                data.append(final_time)
                
                race.sectional_split_times[race.horses[i].name] = data

            race.TPD["Sectional Splits"] = race.sectional_split_times

            race.TPD = {}
        except IndexError:
            print(f"delete this later {race.time}")
            # race.TPD[i_catch.name] = None
            # (f"No sectional data for {race.time} {race.location} {race.date}")

        for j, i in enumerate(race.horses):
            try:
                if type(i.pos) is int:
                    # race.horses[j].TPD = {}
                    # ###move stride data from race to horses
                    # race.horses[j].TPD['FbyF freq'] = (race.stride_data[i.name]['FbyF_freq'])
                    # race.horses[j].TPD['FbyF length'] = (race.stride_data[i.name]['FbyF_length'])
                    # race.horses[j].TPD['peak freq'] = (race.stride_data[i.name]['FbyF_freq'])
                    # race.horses[j].TPD['peak length'] = (race.stride_data[i.name]['FbyF_length'])
                    # race.horses[j].TPD['peak length'] = (race.stride_data[i.name]['FbyF_length'])
                    # ###move sectional tools from race to horse
                    # race.horses[j].TPD['Finishing Speed'] = (race.sectional_tools[i.name]['Finishing speed'])
                    # race.horses[j].TPD['Efficiency Grade'] = (race.sectional_tools[i.name]['efficiency grade'])
                    # race.horses[j].TPD['Efficiency Score'] = (race.sectional_tools[i.name]['efficiency score'])
                    # race.horses[j].TPD['Sectional Speed'] = (race.sectional_tools[i.name]['sectional_speed'])
                    # ###move sectional split times from race to horse
                    # race.horses[j].TPD['Sectional Splits'] = (race.sectional_split_times[i.name])

                    race.TPD[i.name] = {}

                    race.TPD[i.name]["FbyF freq"] = race.stride_data[i.name][
                        "FbyF_freq"
                    ]
                    race.TPD[i.name]["FbyF length"] = race.stride_data[i.name][
                        "FbyF_length"
                    ]
                    race.TPD[i.name]["peak freq"] = race.stride_data[i.name][
                        "peak freq"
                    ]
                    race.TPD[i.name]["peak length"] = race.stride_data[i.name][
                        "peak length"
                    ]

                    # print(race.sectional_tools[i.name])
                    a = race.sectional_tools[i.name]["finishing speed"]
                    race.TPD[i.name]["Finishing Speed"] = a
                    race.TPD[i.name]["Efficiency Grade"] = race.sectional_tools[i.name][
                        "efficiency grade"
                    ]
                    race.TPD[i.name]["Efficiency Score"] = race.sectional_tools[i.name][
                        "efficiency score"
                    ]
                    race.TPD[i.name]["Sectional Speed"] = race.sectional_tools[i.name][
                        "sectional_speed"
                    ]
                    race.TPD[i.name]["FbyF Energy"] = race.sectional_tools[i.name][
                        "Energy"
                    ]
                    race.TPD[i.name]["FbyF Opt Energy"] = race.sectional_tools[i.name][
                        "Opt Energy"
                    ]

                    try:
                        race.TPD[i.name]["Sectional Splits"] = race.sectional_split_times[i.name]

                    except KeyError as err:
                        print("Fucking horse")
                        print(err)
                    race.TPD[i.name]["Basic Data"] = vars(race.horses[j])

                else:
                    continue
            except (IndexError, KeyError):
                print(f"{i.name} had no data.")
                race.TPD[i.name] = None

    def give_stride_data(self, race):
        ## race.stride_data => dict to be replaced with race.stride_data = StrideData(data_1, ..., data_n)
        stride_data = requests.get(race.stride_url, headers = headerProxy.chromeHeader)
        print(stride_data.status_code)
        while int(stride_data.status_code) != 200:
            print(f"Recieved {stride_data.status_code}: Sleeping for 2s and retrying.")
            time.sleep(2)
            stride_data = requests.get(race.stride_url, headers = headerProxy.chromeHeader)

        soup = BS(stride_data.content, "html.parser")
        race.stride_data = {}
        race.TPD = {}
        try:
            stuff = soup.find_all("div", class_="card-body")[1].find_all(
                "div", class_="card-entry"
            )
            # print(h.find('a', class_="horse__link").find('span').getText())

            for i, h in enumerate(stuff):
                somedata = h.find_all("div", class_="width--24")

                data = {}
                if somedata[1].getText().split("/")[0].strip() != "N":
                    data["peak length"] = float(
                        somedata[1].getText().split("/")[0].strip()
                    )
                    data["peak freq"] = float(
                        somedata[1].getText().split("/")[1].strip()
                    )
                    # race.stride_data[race.horses[i].name] = data
                    race.stride_data[race.horses[i].name] = data
                else:
                    data["peak length"] = 0
                    data["peak freq"] = 0
                    race.stride_data[race.horses[i].name] = data
                race.stride_data[race.horses[i].name] = data
                race.stride_data[race.horses[i].name] = data

        except IndexError:
            print(f"No stride data for {race.time} {race.location} {race.date}")

        try:
            stuff = soup.find_all("div", class_="card-body")[1].find_all(
                "div", class_="card-entry"
            )
            race.distance_markers = (
                stuff[0]
                .find_all("div", class_="chart-energy-distribution")[0]
                .attrs["data-data"][1:-1]
                .split(",")[0::3]
            )
            for i, j in enumerate(race.distance_markers):
                race.distance_markers[i] = j.split("[")[1].replace("", "").strip('"')
            race.distance_markers[i] = race.distance_markers[i].strip(".")

            # this new chunk of code pulls more stride data, more then likely not the best way to get it done.

            for i, h in enumerate(stuff):
                FbyF_length = []
                FbyF_freq = []

                for j, k in enumerate(race.distance_markers):
                    FbyF_length.append( float(
                        stuff[i]
                        .find_all("div", class_="chart-energy-distribution")[0]
                        .attrs["data-data"][1:-1]
                        .split(",")[1::3][j]
                    )
                    )
                    FbyF_freq.append( float(
                        stuff[i]
                        .find_all("div", class_="chart-energy-distribution")[1]
                        .attrs["data-data"][1:-1]
                        .split(",")[1::3][j]
                    )
                    )
                    race.stride_data[race.horses[i].name]["FbyF_length"] = FbyF_length
                    race.stride_data[race.horses[i].name]["FbyF_freq"] = FbyF_freq

                # race.TPD["Sride Data"] = race.stride_data

        except IndexError:
            print(f"No stride data for {race.time} {race.location} {race.date}")

    def give_race_data(self, race):
        # NOTE: basic_data as it is called here is pulled in multiple locations.
        #       probably worthwile just pulling this once at some point based on
        #       whether it exists or not.

        # basic_data = requests.get(self.url)
        soup = BS(self.res.content, "html.parser")

        try:
            winning_time_string = (
                soup.find_all("span", class_="padded-right--x-small")[5]
                .getText()
                .split(":")[1]
                .strip()
            )

            winning_time_list = winning_time_string.split()
            seconds_per_unit = {"s": 1, "m": 60}
            if len(winning_time_list) != 2:
                if "m" in winning_time_list[0]:
                    winning_time_list.append("0s")
                if "s" in winning_time_list[0]:
                    winning_time_list.insert(0, "0m")

                final_min, final_sec = winning_time_list

            else:
                final_min, final_sec = winning_time_string.split()

            final_time = (float(final_min[:-1]) * seconds_per_unit[final_min[-1]]) + (
                float(final_sec[:-1]) * seconds_per_unit[final_sec[-1]]
            )

            race.winning_time = final_time

        except IndexError as err:
            print("Winning Time Unavailable")
            print(err)

            race.winning_time = None

        race.goingATR = soup.find_all("p", class_="p--medium")[1].getText().strip()
               
        race.draw_advantage = (
            soup.find(
                "div",
                class_="race-header__details race-header__details--secondary text-align--tablet-right",
            )
            .find_all("p")[1]
            .getText()
            .split(":")[1]
            .strip()
        )

        race.race_tote_returns = list(
            filter(None, soup.find("tbody").getText().strip().split("\n"))
        )

        race.race_dist = (
            soup.find("div", class_="p--large font-weight--semibold").getText().strip()
        )

        ####new way of sorting out atr details
        race.race_class = str
        race.age_group = str
        race.winning_prize_money = int
        race.runners = int
        race.title = str

        # Class, age group, prize, runners.
        race.description = list(
            soup.find(
                "div", class_="race-header__details race-header__details--primary"
            )
            .find_all("p")[1]
            .getText()
            .strip()
            .split("|")
        )
        
        race.age_group = race.description[-1].strip()
        race.race_class = race.description[-2].strip()
        
        race.atrdescription = "".join(race.description[:-2])

        
        race_details =  list(
                            soup.find(
                                "div", class_="race-header__details race-header__details--primary"
                                ).find_all("p")[2]
                .getText()
                .strip()
                .split("-")
            )
   
        race.winning_prize_money = int(race_details[0].split("£")[1].replace(",", ""))
        race.runners = int(race_details[1].split()[0])


        race.title = soup.find( "div", class_="race-header__details race-header__details--primary"
                               ).find_all("p")[0
                                                ].getText().strip()
 

    def give_sectional_tools_data(self, race):

        tools_data = requests.get(race.tools_url, headers = headerProxy.chromeHeader)

        print(tools_data.status_code)
        while int(tools_data.status_code) != 200:
            print(f"Recieved {tools_data.status_code}: Sleeping for 2s and retrying.")
            time.sleep(2)
            tools_data = requests.get(race.tools_url, headers = headerProxy.chromeHeader)


        soup = BS(tools_data.content, "html.parser")
        race.sectional_tools = {}

        try:
            stuff = soup.find_all("div", class_="card-body")[1].find_all(
                "div", class_="card-entry"
            )
            race.finishing_speed = float(soup.find("span", class_="value").getText())
            race.early_pace = (
                soup.find(
                    "div", class_="sectional-analysis__pace js-sectional__analysis-pace"
                )
                .getText()
                .split(":")[1]
                .strip()
                .replace("?", "")
            )
            for i, h in enumerate(stuff):
                data = {}
                data["efficiency grade"] = h.find_all(
                    "span", class_="text-pill text-pill--medium text-pill--grey tooltip"
                )[0].getText()

                data["efficiency score"] = float(
                    h.find_all(
                        "span",
                        class_="text-pill text-pill--medium text-pill--grey tooltip",
                    )[0]["title"].split(":")[1]
                )

                data["finishing speed"] = float(
                    h.find_all("div", class_="width--24 p--medium")[0].getText()
                )
                race.sectional_tools[race.horses[i].name] = data

                sectional_speed = []
                for j in range(0, 3):
                    sectional_speed.append(
                        float(
                            h.find_all("div", class_="width--24")[1]
                            .find_all("span")[j]
                            .getText()
                            .strip()
                        )
                    )
                    race.sectional_tools[race.horses[i].name][
                        "sectional_speed"
                    ] = sectional_speed

                FbyF_Energy = []
                FbyF_Opt_Energy = []
                for j, k in enumerate(race.distance_markers):
                    FbyF_Energy.append( float(
                        stuff[i]
                        .find_all("div", class_="chart-energy-distribution")[0]
                        .attrs["data-data"][1:-1]
                        .split(",")[1::3][j]
                    )
                        )
                    FbyF_Opt_Energy.append(float(
                        stuff[i]
                        .find_all("div", class_="chart-energy-distribution")[0]
                        .attrs["data-data"][1:-1]
                        .split(",")[2::3][j]
                        .split("]")[0]
                        .strip('"')
                    )
                    )

                    race.sectional_tools[race.horses[i].name]["Energy"] = FbyF_Energy

                    race.sectional_tools[race.horses[i].name][
                        "Opt Energy"
                    ] = FbyF_Opt_Energy

                # race.TPD["Sectional Tools"] = race.sectional_tools

        except IndexError:
            print(f"No sectional data for {race.time} {race.location} {race.date}")
            
            
            
            
    def race_dist_int(self, race):
        
        race.dist_furl = get_intDists(race.race_dist)                
