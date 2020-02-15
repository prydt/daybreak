import os
import csv
from datetime import datetime
import dateparser


class Location:
    state: str
    country: str
    date: str
    confirmed: int = 0
    suspected: int = 0
    recovered: int = 0
    death: int = 0

    def __init__(
        self, state, country, date, confirmed=0, suspected=0, recovered=0, death=0
    ):
        self.state = state
        self.country = country
        self.date = date
        self.confirmed = confirmed
        self.suspected = suspected
        self.recovered = recovered
        self.death = death


data_dict = {}


def extract_from_file(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        line = 0
        for row in reader:
            if line == 0:
                line += 1
                continue
            key = row[0] + ":" + row[1]
            date = dateparser.parse(row[2])
            print(date)

            if not key in data_dict:
                data_dict[key] = Location(
                    row[0], row[1], date, row[3], row[4], row[5], row[6]
                )
            else:
                if date == max(data_dict[key].date, date):
                    data_dict[key] = Location(
                        row[0], row[1], date, row[3], row[4], row[5], row[6]
                    )

            line += 1
    return


def extract_from_dir(dirname):
    for (dirpath, dirnames, filenames) in os.walk(dirname):
        for filename in filenames:
            extract_from_file(dirname + "/" + filename)


def output_to_csv(outfile):
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")

        for key, value in data_dict.items():
            writer.writerow(
                [
                    value.state,
                    value.country,
                    value.date,
                    value.confirmed,
                    value.suspected,
                    value.recovered,
                    value.death,
                ]
            )
    return


if __name__ == "__main__":
    extract_from_dir("2019-coronavirus-data")
    output_to_csv("latest_data.csv")
