from api.riot_client import get_riot_id, UserNotFoundError


def init_db(db_conn):
    cur = db_conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS members "
        "(discord_id varchar(32) PRIMARY KEY, tft_username varchar(32), riot_id varchar(64), riot_puuid varchar(96));"
    )
    db_conn.commit()
    cur.close()


def register_member(db_conn, discord_id, tft_username):
    try:
        riot_ids = get_riot_id(tft_username)
    except UserNotFoundError:
        raise

    cur = db_conn.cursor()
    cur.execute(
        "INSERT INTO members (discord_id, tft_username, riot_id, riot_puuid) "
        "VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (discord_id) DO UPDATE SET "
        "(tft_username, riot_id, riot_puuid) = (EXCLUDED.tft_username, EXCLUDED.riot_id, EXCLUDED.riot_puuid)",
        (
            discord_id,
            tft_username,
            riot_ids["id"],
            riot_ids["puuid"],
        ),
    )
    db_conn.commit()
    cur.close()


def fetch_member(db_conn, discord_id):
    cur = db_conn.cursor()
    cur.execute(
        "SELECT tft_username FROM members WHERE discord_id = %s",
        (str(discord_id),),
    )
    res = cur.fetchone()
    cur.close()

    return res[0] if res else None
