import math
from datetime import datetime, timedelta

from api.riot_client import (
    get_match_from_id,
    get_riot_id,
    get_tft_profile_from_id,
    get_user_latest_matches_ids,
    UserNotFoundError,
    MatchNotFoundError,
)


def get_match_activity(username):

    # Sub-functions

    def get_match_summary(match_id, user_puuid):
        def format_response(response):
            queue_id = response["info"]["queue_id"]
            if queue_id == 1090:
                game_type = "Normal"
            elif queue_id == 1100:
                game_type = "Ranked"
            else:
                game_type = "Custom"

            return {
                "date": datetime.fromtimestamp(
                    response["info"]["game_datetime"] / 1000
                ),
                "game_type": game_type,
                "position": next(
                    participant["placement"]
                    for participant in response["info"]["participants"]
                    if participant["puuid"] == user_puuid
                ),
            }

        try:
            resp = get_match_from_id(match_id)
        except MatchNotFoundError:
            return {}

        return format_response(resp)

    def get_num_recent_matches(match_ids):
        if not match_ids:
            return 0

        date_cutoff = datetime.now() - timedelta(days=14)

        try:
            last_game_timestamp = get_match_from_id(match_ids[0])["info"][
                "game_datetime"
            ]
            if datetime.fromtimestamp(last_game_timestamp / 1000) < date_cutoff:
                return 0

            dicho_indexes = [0, len(match_ids) - 1]
            while dicho_indexes[0] < dicho_indexes[1]:
                mid_index = math.ceil((dicho_indexes[0] + dicho_indexes[1]) / 2)
                mid_game_timestamp = get_match_from_id(match_ids[mid_index])["info"][
                    "game_datetime"
                ]

                if datetime.fromtimestamp(mid_game_timestamp / 1000) >= date_cutoff:
                    dicho_indexes[0] = mid_index
                else:
                    dicho_indexes[1] = mid_index - 1

            return dicho_indexes[0] + 1
        except MatchNotFoundError:
            return None

    # End of sub-functions

    try:
        user_puuid = get_riot_id(username)["puuid"]
    except UserNotFoundError:
        return {}

    try:
        user_matches_ids = get_user_latest_matches_ids(user_puuid)
    except MatchNotFoundError:
        return {}

    return {
        "last_game": get_match_summary(user_matches_ids[0], user_puuid),
        "num_recent_games": get_num_recent_matches(user_matches_ids),
    }


def get_tft_profile(username):
    def format_response(response):
        if not response:
            return {
                "summoner_name": username,
                "rank": "Unranked",
                "lp": 0,
                "games": 0,
                "wins": 0,
                "winrate": 0,
            }

        single_resp = response[0]
        formatted_tier = single_resp["tier"].title()
        if formatted_tier in ("Master", "Grandmaster", "Challenger"):
            formatted_rank = formatted_tier
        else:
            formatted_rank = f"{formatted_tier} {single_resp['rank']}"

        return {
            "summoner_name": single_resp["summonerName"],
            "rank": formatted_rank,
            "lp": single_resp["leaguePoints"],
            "games": single_resp["wins"] + single_resp["losses"],
            "wins": single_resp["wins"],
            "winrate": single_resp["wins"]
            / (single_resp["wins"] + single_resp["losses"]),
        }

    try:
        user_id = get_riot_id(username)["id"]
    except UserNotFoundError:
        return {}
    return format_response(get_tft_profile_from_id(user_id))


def get_tft_full_profile(username):
    basic_profile = get_tft_profile(username)

    return {
        **basic_profile,
        "activity": get_match_activity(username),
    }
