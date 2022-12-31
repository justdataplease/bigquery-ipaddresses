import os
from dotenv import load_dotenv
import requests, zipfile, io

load_dotenv()  # take environment variables from .env.

ROOT_DB_PATH = os.path.dirname(__file__)


def update_db():
    db_url = "https://download.maxmind.com/app/geoip_download"
    response = requests.get(db_url, params={'edition_id': "GeoLite2-City-CSV", 'license_key': os.getenv('MAXMIND_LICENCE_KEY'), 'suffix': 'zip'},
                            stream=True)
    print(response.text)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    print(f"Extracted files : {z.namelist()}")
    z.extractall(ROOT_DB_PATH)


if __name__ == "__main__":
    update_db()
