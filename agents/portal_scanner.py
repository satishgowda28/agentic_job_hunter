import logging
from urllib.parse import urlparse

import requests
import yaml

from agents.types import Portal, Portals

API_URL = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "lever": "https://api.lever.co/v0/postings/{slug}",
}


def scan_portals():
    with open("config/portals.yml", "r") as file:
        try:
            data = yaml.safe_load(file)
            companines = Portals(**data).companies
            for company in companines:
                ats = detect_ats(company)
                if ats is None:
                    continue
                else:
                    fetch_data(ats, company)
        except yaml.YAMLError as err:
            print(err)


def detect_ats(portals: Portal) -> str | None:
    ats_keywords = ["greenhouse", "ashby", "lever"]
    for key in ats_keywords:
        if key in portals.careers_url:
            return key
    return None


def fetch_data(ats: str, portal: Portal):
    api_template = API_URL.get(ats, "")
    if api_template != "":
        slug = urlparse(portal.careers_url).path.strip("/")
        api_url = api_template.replace("{slug}", slug)
        # call api call
        reponse = handle_get_details(api_url)
        print(reponse)
    pass


def handle_get_details(api_url: str):
    data = None
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except Exception as err:
        logging.exception(f"failed loading ATS url {api_url}, err: {err}")

    return data


if __name__ == "__main__":
    scan_portals()
