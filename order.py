import os
from pprint import pprint
from argparse import ArgumentParser
from urllib.parse import urlencode
import zipfile
from requests import get
from hero_functions.get_audio_length import get_audio_length
from hero_functions.get_img_change_frames import get_img_change_frames
from hero_functions.osu_parser import osu_parsed_data
from hero_functions.pick_desired_difficulty_beatmap import pick_desired_difficulty_beatmap

# consts
TARGET_DIFFICULTY = 4.5


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--count", required=True, type=int)
    arg_parser.add_argument("--fps", required=True, type=int)
    args = arg_parser.parse_args()
    count = args.count
    fps = args.fps

    """
    query chimu apis
    https://chimu.moe/docs

    genre mapping
    2 -> video game
    10 -> electronic
    """
    query_base_path = "https://api.chimu.moe/v1/search"
    query_query = urlencode({
        "status": 1,  # ranked
        "mode": 1,  # osu!taiko
        "genre": 10,
        "min_diff": 4,
        "max_diff": 5.5,
        "amount": count,
        "min_length": 300,
        "max_length": 600
        # "max_length": 60
    })
    query_path = f"{query_base_path}?{query_query}"
    query_response = get(query_path).json()
    beatmapset_ids = list(map(lambda q: q["SetId"], query_response["data"]))
    pprint(
        list(map(lambda q: (q["SetId"], q["Title"]), query_response["data"])))

    # for each beatmapset, download and extract it
    for beatmapset_id in beatmapset_ids:
        # remove artifacts or create file
        if os.path.isdir(f"./beatmaps/{beatmapset_id}"):
            for file in os.listdir(f"./beatmaps/{beatmapset_id}"):
                os.remove(f"./beatmaps/{beatmapset_id}/{file}")
        else:
            os.mkdir(f"./beatmaps/{beatmapset_id}")

        # download file
        download_path = f"https://chimu.moe/d/{beatmapset_id}"
        osu_save_path = f"./beatmaps/{beatmapset_id}/definition.osu"
        with open(osu_save_path, "wb") as file:
            response = get(download_path)
            file.write(response.content)

        # unzip the osu file
        with zipfile.ZipFile(osu_save_path, "r") as f:
            f.extractall(f"./beatmaps/{beatmapset_id}")

        # remove the zip file
        os.remove(osu_save_path)

    # for each beatmap set, determine the desired difficulty
    for beatmapset_id in beatmapset_ids:
        # download and extracts the assets

        # pick the beatmap that is closest to DIFFICULTY_DESIRED
        target_game_definition: osu_parsed_data = pick_desired_difficulty_beatmap(
            f"./beatmaps/{beatmapset_id}", TARGET_DIFFICULTY
        )

        # get length for img_change_frame calculation
        total_length_second = get_audio_length(
            f"./beatmaps/{beatmapset_id}/{target_game_definition.audio_filename}")

        # getting the frames in which the image should change
        img_change_frames = get_img_change_frames(
            target_game_definition, total_length_second, fps)

        # print in required format
        print(f"{beatmapset_id}, {len(img_change_frames)}")


if __name__ == "__main__":
    main()
