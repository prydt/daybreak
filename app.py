import csv
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
import dateparser
from geopy.geocoders import Nominatim
from geopy import distance
import geopy
from operator import itemgetter
from math import e

# global variable lol
locations = {}
HDIs = {}
geolocator = Nominatim(user_agent="daybreak-app")


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
        self.date = date
        self.confirmed = confirmed
        self.suspected = suspected
        self.recovered = recovered
        self.death = death
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
    line_count = 0
    with open("HDI_final.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            HDIs[row[0]] = row[1]


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


def get_HDI_rank(country):
    return HDIs[country]


def get_population(key):
    return locations[key].population


def find_closest(location):
    lat = location.latitude
    lon = location.longitude
    current_loc = (lat, lon)

    temp_list = []
    for (key, loc) in locations.items():
        temp_list.append(
            (
                loc.state + loc.country,
                distance.distance(current_loc, (loc.latitude, loc.longitude)).miles,
            )
        )

    out = sorted(temp_list, key=itemgetter(1))
    return out[0]


def fractional(coef, power):
    return coef * ((e ** power) / ((e ** power) + 1))


def danger_coef(distance, confirmed_cases, hdi_rank):
    delta = (
        fractional(-7, (distance / 220.0) - 5)
        + 7
        + fractional(6, (confirmed_cases / 90.0) - 5)
        + fractional(1, (hdi_rank / 17.0) - 4)
    )
    return fractional(1, delta - 7)


def predicted_confirmed(population, inital_amt):
    return population / (
        (1 + ((population - inital_amt) / inital_amt) * e ** ((-1 * 1.888) / 103))
    )


# MAIN
load_data()
# output_to_csv('latest_data.csv')

app = Flask(__name__, static_url_path="")

@app.route("/<path:path>")
def root():
    return send_from_directory("/static", path)



@app.route("/endpoint", methods=["POST"])
def endpoint():
    if request.method == "POST":
        location = geolocator.geocode(request.form["location"])
        location = geolocator.reverse(
            str(location.latitude) + ", " + str(location.longitude), language="en_US"
        )
        country = location.raw["address"]["country"]
        closest = find_closest(location)
        closest_dist = closest[1]
        confirmed_cases = int(locations[closest[0]].confirmed) + int(
            locations[closest[0]].death
        )
        hdi = get_HDI_rank(country)

        danger = "{0:.2f}%".format(
            danger_coef(closest_dist, confirmed_cases, int(hdi)) * 100
        )

        pop = int(get_population(closest[0]))
        predicted = predicted_confirmed(pop, confirmed_cases)
        print(confirmed_cases)
        print(predicted)
        danger2 = "{0:.2f}%".format(
            danger_coef(closest_dist, predicted, int(hdi)) * 100
        )

        out = {
            "closest_name": closest[0],
            "distance": closest_dist,
            "confirmed_cases": confirmed_cases,
            "danger_coef": danger,
            "predicted_danger_coef": danger2,
        }
        return jsonify(out)
