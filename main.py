import html
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

ANILIST_URL = "https://graphql.anilist.co"
ANILIST_USERNAME = "MertNaci"

# Turkey has been fixed at UTC+3 since 2016 (no DST)
TR_TZ = timezone(timedelta(hours=3))
# Each run reports episodes aired on the previous calendar day (00:00–00:00 TR)
CUTOFF_HOUR = 0
REQUEST_TIMEOUT = 15  # seconds

WATCHING_QUERY = """
query ($userName: String) {
  MediaListCollection(userName: $userName, type: ANIME, status_in: [CURRENT, REPEATING]) {
    lists {
      entries {
        media {
          id
          title { english romaji }
        }
      }
    }
  }
}
"""

AIRING_QUERY = """
query ($mediaIds: [Int], $after: Int, $before: Int, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    airingSchedules(mediaId_in: $mediaIds, airingAt_greater: $after, airingAt_lesser: $before, sort: TIME) {
      episode
      airingAt
      mediaId
    }
  }
}
"""


def load_telegram_config():
    """GitHub Actions: environment variables. Local: local_secrets.py (gitignored)."""
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if token and chat_id:
        return token, chat_id
    try:
        import local_secrets
    except ImportError:
        sys.exit("TELEGRAM_TOKEN / CHAT_ID not found (set env vars or create local_secrets.py)")
    return local_secrets.TELEGRAM_TOKEN, local_secrets.CHAT_ID


def anilist_query(query, variables):
    response = requests.post(
        ANILIST_URL,
        json={"query": query, "variables": variables},
        timeout=REQUEST_TIMEOUT,
    )
    try:
        body = response.json()
    except ValueError:
        response.raise_for_status()
        raise
    if response.status_code != 200 or body.get("errors"):
        raise RuntimeError(f"AniList error ({response.status_code}): {body.get('errors')}")
    return body["data"]


def get_watching_anime():
    data = anilist_query(WATCHING_QUERY, {"userName": ANILIST_USERNAME})
    collection = data.get("MediaListCollection") or {}

    anime_map = {}
    for single_list in collection.get("lists") or []:
        for entry in single_list.get("entries") or []:
            media = entry["media"]
            anime_map[media["id"]] = media["title"]["english"] or media["title"]["romaji"]
    return anime_map


def get_check_window(now):
    """Fixed 24h window ending at the most recent cutoff, independent of when
    GitHub actually starts the job, so daily runs never overlap or leave gaps."""
    now_local = now.astimezone(TR_TZ)
    end = now_local.replace(hour=CUTOFF_HOUR, minute=0, second=0, microsecond=0)
    if end > now_local:
        end -= timedelta(days=1)
    return end - timedelta(days=1), end


def get_aired_episodes(media_ids, start, end):
    episodes = []
    page = 1
    while True:
        data = anilist_query(AIRING_QUERY, {
            "mediaIds": media_ids,
            "after": int(start.timestamp()) - 1,  # airingAt_greater is exclusive
            "before": int(end.timestamp()),
            "page": page,
        })
        episodes.extend(data["Page"]["airingSchedules"])
        if not data["Page"]["pageInfo"]["hasNextPage"]:
            return episodes
        page += 1


def build_message(episodes, anime_map, start, end):
    parts = [
        "<b>New Episode Alert!</b>\n"
        f"<i>Aired {start:%d.%m %H:%M} – {end:%d.%m %H:%M}</i>"
    ]
    for ep in episodes:
        title = html.escape(anime_map.get(ep["mediaId"], "Unknown Anime"))
        aired = datetime.fromtimestamp(ep["airingAt"], TR_TZ)
        parts.append(f"<b>{title}</b>\n   → Episode {ep['episode']} ({aired:%d.%m %H:%M})")
    return "\n\n".join(parts)


def send_telegram_message(text):
    token, chat_id = load_telegram_config()
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Telegram error ({response.status_code}): {response.text}")


def main():
    dry_run = "--dry-run" in sys.argv

    anime_map = get_watching_anime()
    if not anime_map:
        print("Watching list is empty.")
        return

    start, end = get_check_window(datetime.now(timezone.utc))
    print(f"{len(anime_map)} anime in watching list. "
          f"Checking {start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} (TR)")

    episodes = get_aired_episodes(list(anime_map), start, end)
    if not episodes:
        print("No new episodes in this window.")
        return

    message = build_message(episodes, anime_map, start, end)
    if dry_run:
        print("--- dry run, not sending ---")
        print(message)
        return

    send_telegram_message(message)
    print(f"Notification sent ({len(episodes)} episodes).")


if __name__ == "__main__":
    main()