from argparse import ArgumentParser
import time
from mutagen.mp3 import MP3
from hero_functions.chimu import chimu
from hero_functions.get_audio_length import get_audio_length
from hero_functions.get_img_change_frames import get_img_change_frames
from hero_functions.osu_parser import osu_parsed_data
from hero_functions.pick_desired_difficulty_beatmap import pick_desired_difficulty_beatmap

"""
py ./bulk_img_count_check.py --fps 60 --difficulty 4.5 --beatmaps 1812415 1870775 1667710 1795684 1881219
"""


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--beatmaps", nargs="+", type=int)
    arg_parser.add_argument("--fps", type=int)
    arg_parser.add_argument("--difficulty", type=float)
    args = arg_parser.parse_args()
    beatmaps = args.beatmaps
    fps = args.fps
    difficulty = args.difficulty

    for beatmap in beatmaps:
        # download and extracts the assets
        chimu(beatmap)

        # pick the beatmap that is closest to DIFFICULTY_DESIRED
        target_game_definition: osu_parsed_data = pick_desired_difficulty_beatmap(
            f"./beatmaps/{beatmap}", difficulty
        )

        # get length for img_change_frame calculation
        total_length_second = get_audio_length(f"./beatmaps/{beatmap}/{target_game_definition.audio_filename}")

        # getting the frames in which the image should change
        img_change_frames = get_img_change_frames(
            target_game_definition, total_length_second, fps)
        print(f"{beatmap}\t{len(img_change_frames)}")

        # seems chimu have rate limit mechanism
        time.sleep(10)


if __name__ == "__main__":
    main()
