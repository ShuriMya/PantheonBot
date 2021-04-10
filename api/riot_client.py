import os
import requests
from dotenv import load_dotenv

RIOT_API_URL = "https://euw1.api.riotgames.com"
RIOT_MATCHES_API_URL = "https://europe.api.riotgames.com"

load_dotenv()
RIOT_API_TOKEN = os.getenv("RIOT_API_TOKEN")


class UserNotFoundError(Exception):
    pass


class MatchNotFoundError(Exception):
    pass


def get_riot_id(username):
    resp = requests.get(
        f"{RIOT_API_URL}/tft/summoner/v1/summoners/by-name/{username}",
        headers={"X-Riot-Token": RIOT_API_TOKEN},
    )

    if resp.status_code != 200:
        raise UserNotFoundError()

    resp = resp.json()
    return {"id": resp["id"], "puuid": resp["puuid"]}


def get_tft_profile_from_id(summonerId):
    resp = requests.get(
        f"{RIOT_API_URL}/tft/league/v1/entries/by-summoner/{summonerId}",
        headers={"X-Riot-Token": RIOT_API_TOKEN},
    )

    if resp.status_code != 200:
        raise UserNotFoundError()

    return resp.json()


def get_user_latest_matches_ids(puuid, count=50):
    resp = requests.get(
        f"{RIOT_MATCHES_API_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}",
        headers={"X-Riot-Token": RIOT_API_TOKEN},
    )

    if resp.status_code != 200:
        raise MatchNotFoundError()

    return resp.json()


def get_match_from_id(match_id):
    resp = requests.get(
        f"{RIOT_MATCHES_API_URL}/tft/match/v1/matches/{match_id}",
        headers={"X-Riot-Token": RIOT_API_TOKEN},
    )

    if resp.status_code != 200:
        raise MatchNotFoundError()

    return resp.json()
