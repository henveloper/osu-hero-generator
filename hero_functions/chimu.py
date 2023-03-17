import os
from pprint import pprint
import zipfile
from urllib.parse import urlencode
from requests import get


def download_beatmaps():
    # https://chimu.moe/docs

    # query
    query_base_path = "https://api.chimu.moe/v1/search"
    """
    genre mapping
    2 -> game
    """
    query_query = urlencode({
        "status": 1, # ranked
        "mode": 1, # osu!taiko
        "genre": 2,
        "min_diff": 4,
        "max_diff": 5.5,
        "amount": 10,
        # "min_length": 300,
        # "max_length": 600
        "max_length": 60
    })
    query_path = f"{query_base_path}?{query_query}"
    query_response = get(query_path).json()
    set_ids = list(map(lambda q: q["SetId"], query_response["data"]))
    pprint(list(map(lambda q: (q["SetId"], q["Title"]), query_response["data"])))

    for beatmap_id in set_ids:
        url = f"https://api.chimu.moe/v1/set/{beatmap_id}"
        get(url)

        # TODO: can't -r if no admin privledge
        # rm file if files exist in beatmap set folder
        if os.path.exists(f"./beatmaps/{beatmap_id}"):
            for file in os.listdir(f"./beatmaps/{beatmap_id}"):
                os.unlink(f"./beatmaps/{beatmap_id}/{file}")
        else:
            os.mkdir(f"./beatmaps/{beatmap_id}")

        # if get not raise, then it is 200
        download_path = f"https://chimu.moe/d/{beatmap_id}"

        # download file
        osu_save_path = f"./beatmaps/{beatmap_id}/a.osu"
        with open(osu_save_path, "wb") as file:
            response = get(download_path)
            file.write(response.content)

        # unzip the osu file
        with zipfile.ZipFile(osu_save_path, "r") as f:
            f.extractall(f"./beatmaps/{beatmap_id}")

    return set_ids
