import requests

VERSION = "5.0.0"
LATEST_RELEASE_URL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest"


def getLatestVersion():
    final_url = followRedirect(LATEST_RELEASE_URL)
    LatestVersion = final_url.removeprefix(
        "https://github.com/O2theC/CrabChampionSaveManager/releases/tag/"
    )
    return LatestVersion


def followRedirect(url):
    response = requests.get(url)
    return response.url
