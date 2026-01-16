import requests
import json
import secrets

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
              nextAiringEpisode {
                episode
                timeUntilAiring
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
        final_message = "--- My Current Anime Schedule --- \n\n"

        all_lists = data["data"]["MediaListCollection"]["lists"]

        for single_list in all_lists:
            list_name = single_list["name"]

            if list_name == "Watching" or list_name == "Current":
                final_message += f"-- {list_name} --\n"

                entries = single_list["entries"]
                for entry in entries:
                    title = entry["media"]["title"]["english"]
                    if title is None:
                        title = entry["media"]["title"]["romaji"]

                    next_ep = entry["media"]["nextAiringEpisode"]

                    if next_ep is not None:
                        ep_num = next_ep["episode"]
                        seconds = next_ep["timeUntilAiring"]

                        days = seconds // 86400
                        hours = (seconds % 86400) // 3600

                        final_message += f"*{title}* \n    -->Episode {ep_num}: {days} days, {hours} hours left.\n\n"
                    else:
                        final_message += f"*{title}* (Up to date / Finished)\n\n"
                final_message += "\n"

        print("Sending to Telegram...")
        send_telegram_message(final_message)
        print("Operation complete!")