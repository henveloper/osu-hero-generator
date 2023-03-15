import os
import zipfile
from requests import get

def chimu(beatmap_id: int):
    # https://chimu.moe/docs
    url = f"https://api.chimu.moe/v1/set/{beatmap_id}"
    get(url)

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
    
