import requests
import json

url = "https://graphql.anilist.co"

query = '''
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
        }
      }
    }
  }
}
'''

variables = {
    "userName": "MertNaci"
}

response = requests.post(url, json={"query": query, "variables": variables})

if response.status_code == 200:
    data = response.json()

    all_lists = data["data"]["MediaListCollection"]["lists"]
    for single_list in all_lists:
        list_name = single_list["name"]
        print(f"\n--- {list_name} List ---")

        entries = single_list["entries"]
        for entry in entries:
            anime_title = entry["media"]["title"]["english"]
            if anime_title is None:
                anime_title = entry["media"]["title"]["romaji"]
            print(f"* {anime_title}")

else:
    print("Error!")
    print("Error code:", response.status_code)
    print("Detail:", response.text)