import csv
import requests
from faker import Factory
from random import betavariate
from datetime import datetime


def save_ipaddresses(url: str, filename: str) -> list:
    """
    This function retrieves and returns a list of HTTP proxy addresses. It is also write them into a CSV.
    :param url: GitHub url to get the list of HTTP proxy addresses
    :param filename: The name of the output CSV
    :return:
    """
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


def random_choice(lst: list, a: int = 2, b: int = 2) -> str:
    """
    Select randomly and element from a list with probability from the Beta distribution.
    :param lst: A list to select a random element
    :param a: Beta parameter a
    :param b: Beta parameter b
    :return:
    """
    index = int(betavariate(a, b) * len(lst))
    return lst[index]


def create_fake_orders(filename: str, customer_ids: list, number: int, from_date: str, to_date: str) -> None:
    """
    This function generates fake orders for a list of customer_ids. It writes the results into a CSV.
    :param filename: The name of the output CSV
    :param customer_ids: The list of customer_ids
    :param number: The number of orders to generate
    :param from_date: Date span used to generate random timestamp (%Y-%m-%d)
    :param to_date: Date span used to generate random timestamp (%Y-%m-%d)
    :return:
    """
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
