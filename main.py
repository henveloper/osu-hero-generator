from hero_functions.osu_parser import osu_parser
from hero_functions.chimu import chimu
from hero_functions.compose_image import compose_image
from mutagen.mp3 import MP3
import moviepy.editor as mpe
import math
import os
import cv2


# constants
NO_RENDER = True
BEATMAP_SET_ID = 491879
DIFFICULTY_DESIRED = 4.6



OSU_FILE_PATH = "./beatmaps/639535/sample.osu"
IMAGES_FOLDER = "C:/repo/stable-diffusion-hero/images"
HITMARK_FILE_PATH = "./assets/hitmark.png"
MP3_PATH = "./beatmaps/639535/rabbit.mp3"
BASE_NOTE_VELOCITY = 40  # in px per second
NUM_BAR_PER_IMG_CHANGE = 1
FPS = 60
DIMENSION = (1088, 1536)
OUTPUT_PATH = "./output/a.avi"
OUTPUT_PATH2 = "./output/b.mp4"


def main():
    # download and extracts the assets
    chimu(BEATMAP_SET_ID)
    print("Downloaded and extracted assets.")

    # pick the osu map that is closest to DIFFICULTY_DESIRED
    target_game_definition = None
    min_target_delta = None
    for file in os.listdir(f"./beatmaps/{BEATMAP_SET_ID}"):
        if file == "a.osu" or not file.endswith(".osu"):
            continue
        game_definition = osu_parser(f"./beatmaps/{BEATMAP_SET_ID}/{file}")
        difficulty_delta_abs = abs(game_definition.overall_difficulty - DIFFICULTY_DESIRED)
        if target_game_definition is None:
            target_game_definition = game_definition
            min_target_delta = difficulty_delta_abs
            continue
        if difficulty_delta_abs <= min_target_delta:
            target_game_definition = game_definition
            min_target_delta = difficulty_delta_abs
    print(f"Using version={target_game_definition.version}, difficulty={target_game_definition.overall_difficulty}")

    total_length_second = MP3(f"./beatmaps/{BEATMAP_SET_ID}/{target_game_definition.audio_filename}").info.length
    print(f"Length is {total_length_second} seconds.")
    target_game_definition = osu_parser(OSU_FILE_PATH)

    img_change_frames = set()
    frame_to_noteloc_dict = dict()

    beatlength = None
    for i in range(len(target_game_definition.timing_points)):
        time, beatlength_this, measure = target_game_definition.timing_points[i]
        if beatlength_this > 0:
            beatlength = beatlength_this
        next_time = total_length_second
        if i < len(target_game_definition.timing_points) - 1:
            next_time, _, _ = target_game_definition.timing_points[i+1]

        while time < next_time:
            img_change_frames.add(math.floor(time * FPS))
            time += beatlength * measure * NUM_BAR_PER_IMG_CHANGE

    print(f"Number of images required: {len(img_change_frames)+1}")
        

    for ho_time in target_game_definition.hit_objects:
        middle_frame_number = math.floor(ho_time * FPS)
        # TODO: impl velocity change wrt to info
        note_velocity = BASE_NOTE_VELOCITY

        frame_to_noteloc_dict.setdefault(middle_frame_number, list())
        frame_to_noteloc_dict[middle_frame_number].append(0.5)

        # forward time, backward notes
        ratio_ptr = 0.5
        frame_number = middle_frame_number
        while ratio_ptr >= 0:
            frame_number += 1
            ratio_ptr -= note_velocity / DIMENSION[0]
            frame_to_noteloc_dict.setdefault(frame_number, list())
            frame_to_noteloc_dict[frame_number].append(ratio_ptr)
        # backward time, forward notes
        ratio_ptr = 0.5
        frame_number = middle_frame_number
        while ratio_ptr <= 1:
            frame_number -= 1
            ratio_ptr += note_velocity / DIMENSION[0]
            frame_to_noteloc_dict.setdefault(frame_number, list())
            frame_to_noteloc_dict[frame_number].append(ratio_ptr)
    
    if NO_RENDER:
        return

    # compose the video
    video_writer = cv2.VideoWriter(
        OUTPUT_PATH, cv2.VideoWriter_fourcc(*'DIVX'), FPS, DIMENSION)
    img_names = [os.path.join(IMAGES_FOLDER, n)
                 for n in os.listdir(IMAGES_FOLDER)]
    img_ptr = 0

    total_frames = math.ceil(total_length_second * FPS)
    for frame_number in range(total_frames):
        if frame_number % 100 == 99:
            print(f"frame {frame_number} of {total_frames}")

        if frame_number in img_change_frames:
            img_ptr += 1
            img_ptr %= len(img_names)
        img = cv2.imread(img_names[img_ptr])

        # slider - point in (row, col) as in matrices

        cv2.line(img, (0, math.floor(
            0.9 * DIMENSION[1])), (DIMENSION[0], math.floor(0.9 * DIMENSION[1])), (0, 0, 0), 5)
        cv2.circle(img,
                (math.floor(DIMENSION[0] * 0.5), math.floor(0.9 * DIMENSION[1])),
                34, 
                (0, 0, 0),
                -1)
        notes = frame_to_noteloc_dict.get(frame_number)
        if notes is not None:
            compose_image(img, DIMENSION, notes)

        # write the frame
        video_writer.write(img)

        # if frame_number > 500:
        # break

    video_writer.release()

    video = mpe.VideoFileClip(OUTPUT_PATH)
    audio = mpe.AudioFileClip(MP3_PATH)
    video = video.set_audio(audio)
    video.write_videofile(OUTPUT_PATH2, fps=FPS)


if __name__ == "__main__":
    main()
