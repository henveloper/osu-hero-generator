from hero_functions.get_audio_length import get_audio_length
from hero_functions.get_img_change_frames import get_img_change_frames
from hero_functions.osu_parser import osu_parsed_data, osu_parser
from hero_functions.assert_image_dimension_consistent import assert_image_dimension_consistent
from hero_functions.chimu import chimu
from hero_functions.compose_image import compose_image
from hero_functions.pick_desired_difficulty_beatmap import pick_desired_difficulty_beatmap
from mutagen.mp3 import MP3
import moviepy.editor as mpe
import math
import cv2


# constants
DIFFICULTY_DESIRED = 3.5
BASE_NOTE_VELOCITY = 600  # in px per second
FPS = 60


def generate_video(id: int):
    OUTPUT_PATH_AVI = f"./output/fh_{id}.avi"
    OUTPUT_PATH_MP4 = f"./output/fh_{id}.mp4"
    images_folder_path = f"./assets/{id}"

    # assert images with same dimensions
    img_names, dimension = assert_image_dimension_consistent(
        images_folder_path)
    print(f"Images asserted to be in consistent dimension {dimension}")

    # download and extracts the assets
    chimu(id)
    print(f"Downloaded and extracted assets of beatmap set {id}.")

    # pick the beatmap that is closest to DIFFICULTY_DESIRED
    target_game_definition: osu_parsed_data = pick_desired_difficulty_beatmap(
        f"./beatmaps/{id}", DIFFICULTY_DESIRED
    )
    print(
        f"Using version={target_game_definition.version}, difficulty={target_game_definition.overall_difficulty}")

    total_length_second = get_audio_length(
        f"./beatmaps/{id}/{target_game_definition.audio_filename}")
    print(f"Length is {total_length_second} seconds.")

    # getting the frames in which the image should change
    img_change_frames = get_img_change_frames(
        target_game_definition, total_length_second, FPS)
    print(f"Number of images required: {len(img_change_frames)+1}")

    frame_to_noteloc_dict = dict()

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
            ratio_ptr -= (note_velocity/FPS) / dimension[0]
            frame_to_noteloc_dict.setdefault(frame_number, list())
            frame_to_noteloc_dict[frame_number].append(ratio_ptr)
        # backward time, forward notes
        ratio_ptr = 0.5
        frame_number = middle_frame_number
        while ratio_ptr <= 1:
            frame_number -= 1
            ratio_ptr += (note_velocity/FPS) / dimension[0]
            frame_to_noteloc_dict.setdefault(frame_number, list())
            frame_to_noteloc_dict[frame_number].append(ratio_ptr)

    # compose the video
    video_writer = cv2.VideoWriter(
        OUTPUT_PATH_AVI, cv2.VideoWriter_fourcc(*'DIVX'), FPS, dimension)
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
            0.9 * dimension[1])), (dimension[0], math.floor(0.9 * dimension[1])), (0, 0, 0), 5)
        cv2.circle(img,
                   (math.floor(dimension[0] * 0.5),
                    math.floor(0.9 * dimension[1])),
                   34,
                   (0, 0, 0),
                   -1)
        notes = frame_to_noteloc_dict.get(frame_number)
        if notes is not None:
            compose_image(img, dimension, notes)

        # write the frame
        video_writer.write(img)

    video_writer.release()

    video = mpe.VideoFileClip(OUTPUT_PATH_AVI)
    audio = mpe.AudioFileClip(
        f"./beatmaps/{id}/{target_game_definition.audio_filename}")
    video = video.set_audio(audio)
    video.write_videofile(OUTPUT_PATH_MP4, codec="libx264", fps=FPS)


if __name__ == "__main__":
    data = [1795684, 1812415, 1870775, 1881219]
    for id in data:
        generate_video(id)
