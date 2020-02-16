import csv
from flask import Flask, request, jsonify
import dateparser
from geopy.geocoders import Nominatim
from geopy import distance
import geopy
from operator import itemgetter

# global variable lol
locations = {}
geolocator = Nominatim(user_agent="coronavirus-tracker-thing")


class Location:
    state: str
    country: str
    date: str
    confirmed: int = 0
    suspected: int = 0
    recovered: int = 0
    death: int = 0

    def __init__(
        self,
        state,
        country,
        date,
        confirmed=0,
        suspected=0,
        recovered=0,
        death=0,
        longitude=0,
        latitude=0,
        population=0,
    ):
        self.state = state
        self.country = country
        if state:
            self.name = state + "," + country
        else:
            self.name = country
        print(self.name)
        self.date = date
        self.confirmed = confirmed
        self.suspected = suspected
        self.recovered = recovered
        self.death = death

        # location = geolocator.geocode(self.name)
        # self.longitude = location.longitude
        # self.latitude = location.latitude
        self.longitude = longitude
        self.latitude = latitude

        self.population = population


def load_data():
    with open("latest_data.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            key = row[0] + row[1]
            print("loading {}".format(key))
            locations[key] = Location(
                row[0],
                row[1],
                dateparser.parse(row[2]),
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
            )


def output_to_csv(outfile):
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        for key, value in locations.items():
            writer.writerow(
                [
                    value.state,
                    value.country,
                    value.date,
                    value.confirmed,
                    value.suspected,
                    value.recovered,
                    value.death,
                    value.longitude,
                    value.latitude,
                    value.population,
                ]
            )


def find_closest(location_name):

    geocode = geolocator.geocode(location_name)
    lat = geocode.latitude
    lon = geocode.longitude
    current_loc = (lat, lon)

    temp_list = []
    for (key, loc) in locations.items():
        temp_list.append(
            (
                loc.state + loc.country,
                distance.distance(current_loc, (loc.latitude, loc.longitude)).miles
            )
        )
        print(loc)

    out = sorted(temp_list, key=itemgetter(1))
    return out[:10]


# MAIN
load_data()
# output_to_csv('latest_data.csv')

app = Flask(__name__)

# TODO add index.html
@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/endpoint", methods=["POST"])
def endpoint():
    if request.method == "POST":
        return jsonify(find_closest(request.form["location"]))
