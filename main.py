import requests
import secrets
import time
from datetime import datetime,timedelta,timezone

ANILIST_URL = "https://graphql.anilist.co"
ANILIST_USERNAME = "MertNaci"

def send_telegram_message(message):
    token = secrets.TELEGRAM_TOKEN
    chat_id = secrets.CHAT_ID
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(send_url, json=payload)
    if response.status_code != 200:
        print(f"Telegram Error: {response.text}")
    else:
        print("Notification sent successfully.")

def get_user_watching_ids():
    query = """
    query ($userName: String) {
      MediaListCollection(userName: $userName, type: ANIME) {
        lists {
          name
          entries {
            media {
              id
              title {
                english
                romaji
              }
            }
          }
        }
      }
    }
    """
    variables = {"userName": ANILIST_USERNAME}
    response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})

    if response.status_code != 200:
        print(f"AniList Error: {response.text}")
        return {}

    data = response.json()
    anime_map = {}

    if data.get("data"):
        for single_list in data["data"]["MediaListCollection"]["lists"]:
            if single_list["name"] == "Watching" or single_list["name"] == "Current":
                for entry in single_list["entries"]:
                    media_id = entry["media"]["id"]

                    title = entry["media"]["title"]["english"]
                    if title is None:
                        title = entry["media"]["title"]["romaji"]

                    anime_map[media_id] = title

    return anime_map

def check_recent_episodes(anime_map):
    if not anime_map:
        return None

    current_time = int(time.time())
    yesterday_time = current_time - 86400

    media_ids = list(anime_map.keys())

    query = """
    query ($mediaIds: [Int], $airingAfter: Int, $airingBefore: Int) {
      Page(perPage: 50) {
        airingSchedules(mediaId_in: $mediaIds, airingAt_greater: $airingAfter, airingAt_lesser: $airingBefore, sort: TIME_DESC) {
          episode
          airingAt
          mediaId
        }
      }
    }
    """

    variables = {
        "mediaIds": media_ids,
        "airingAfter": yesterday_time,
        "airingBefore": current_time
    }

    response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"AniList Error: {response.text}")
        return None

if __name__ == "__main__":
    print("Step 1: Fetching watching list...")
    my_anime_map = get_user_watching_ids()

    if my_anime_map:
        print(f"Found {len(my_anime_map)} watching anime. Checking last 24 hours...")

        data = check_recent_episodes(my_anime_map)

        has_new_episode = False
        notification_message = "**New Episode Alert!** \n\n_Aired within the last 24 hours:_\n\n"

        if data and data.get("data"):
            schedules = data["data"]["Page"]["airingSchedules"]

            if schedules:
                has_new_episode = True

                for item in schedules:
                    ep_num = item["episode"]
                    airing_at = item["airingAt"]
                    media_id = item["mediaId"]

                    anime_name = my_anime_map.get(media_id, "Unknown Anime")

                    dt_object = datetime.fromtimestamp(airing_at, timezone.utc) + timedelta(hours=3)
                    time_str = dt_object.strftime("%H:%M")

                    current_ts = int(time.time())
                    hours_ago = (current_ts - airing_at) // 3600

                    notification_message += f"*{anime_name}*\n   --> Episode {ep_num} aired! ({time_str} - {hours_ago} hrs ago)\n\n"

            if has_new_episode:
                print("New episodes found, sending to Telegram...")
                send_telegram_message(notification_message)
            else:
                print("No new episodes aired in the last 24 hours.")
        else:
            print("Data could not be fetched or is empty.")
    else:
        print("Watching list is empty or could not be fetched.")