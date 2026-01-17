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

def get_anime_list():
    query = """
    query ($userName: String) {
      MediaListCollection(userName: $userName, type: ANIME) {
        lists {
          name
          entries {
            media {
              title {
                english
                romaji
              }
              airingSchedule(notYetAired: false) {
                nodes {
                   episode
                   airingAt
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"userName": ANILIST_USERNAME}
    response = requests.post(ANILIST_URL, json={"query": query, "variables": variables})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"AniList Error: {response.text}")
        return None

if __name__ == "__main__":
    print("Fetching data...")
    data = get_anime_list()

    if data:
        notification_message = "**New Episode Alert!** \n\n_Aired within the last 24 hours:_\n\n"
        has_new_episode = False

        current_time = int(time.time())

        all_lists = data["data"]["MediaListCollection"]["lists"]

        for single_list in all_lists:
            list_name = single_list["name"]

            if list_name == "Watching" or list_name == "Current":
                entries = single_list["entries"]

                for entry in entries:
                    schedule_nodes = entry["media"]["airingSchedule"]["nodes"]

                    if schedule_nodes:
                        last_aired_ep = schedule_nodes[-1]
                        ep_num = last_aired_ep["episode"]
                        airing_at = last_aired_ep["airingAt"]

                        time_difference = current_time - airing_at

                        if 0 <= time_difference <= 86400:
                            has_new_episode = True

                            title = entry["media"]["title"]["english"]
                            if title is None:
                                title = entry["media"]["title"]["romaji"]

                            dt_object = datetime.fromtimestamp(airing_at, timezone.utc) + timedelta(hours=3)
                            time_str = dt_object.strftime("%H:%M")

                            notification_message += f"*{title}*\n   -->Episode {ep_num} aired! (Time: {time_str})\n\n"

        if has_new_episode:
            print("New aired episode found, sending message...")
            send_telegram_message(notification_message)
        else:
            print("No new episodes aired in the last 24 hours.")

    print("Operation complete!")