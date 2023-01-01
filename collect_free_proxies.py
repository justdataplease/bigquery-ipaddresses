import csv
import requests
from faker import Factory
from random import betavariate
from datetime import datetime


def save_ipaddresses(url, filename):
    # Send a request to the URL and get the response
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the content of the response as a list of lines
        lines = response.text.split("\n")
        lines = [line.split(":")[0] for line in lines]

        # Open a new CSV file for writing
        with open(filename, "w", newline="") as csv_file:
            # Create a CSV writer object
            writer = csv.writer(csv_file)

            # Write each line in the list to the CSV file
            for line in lines:
                writer.writerow([line])

    else:
        print("Failed to download the file")
    return lines


def random_choice(lst, a=2, b=2):
    index = int(betavariate(a, b) * len(lst))
    return lst[index]


def create_fake_orders(filename, customer_ids, number, from_date, to_date):
    fake = Factory.create()
    lines = []

    for i in range(1, number):
        customer_id = random_choice(customer_ids)
        amount = fake.pydecimal(
            left_digits=3,
            right_digits=4,
            positive=True
        )
        order_datetime = fake.date_time_between_dates(
            datetime_start=datetime.strptime(from_date, '%Y-%m-%d'),
            datetime_end=datetime.strptime(to_date, '%Y-%m-%d')
        )
        lines.append(
            {
                'customer_id': customer_id,
                'amount': amount,
                'datetime': order_datetime}
        )

    with open(filename, "w", newline="") as csv_file:
        # Create a CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=lines[0].keys())
        writer.writeheader()
        # Write each row of data to the CSV file
        for row in lines:
            writer.writerow(row)


def main():
    # Download IP Addresses
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    customer_ids = save_ipaddresses(url, filename="free-proxies.csv")

    # Create fake orders
    from_date = "2021-01-01"
    to_date = "2023-12-31"
    number_of_orders = 100000
    create_fake_orders(filename="fake-orders.csv", customer_ids=customer_ids, number=number_of_orders, from_date=from_date, to_date=to_date)


if __name__ == "__main__":
    main()
