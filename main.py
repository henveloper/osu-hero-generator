from argparse import ArgumentParser
from traceback import print_exc
from hero_functions.get_audio_length import get_audio_length
from hero_functions.get_img_change_frames import get_img_change_frames
from hero_functions.osu_parser import osu_parsed_data
from hero_functions.assert_image_dimension_consistent import assert_image_dimension_consistent
from hero_functions import gameplay_painter
from hero_functions.pick_desired_difficulty_beatmap import pick_desired_difficulty_beatmap
import os
import moviepy.editor as mpe
import math
import cv2


# constants
# TODO: figure out how to use same value with order.py
TARGET_DIFFICULTY = 4.5
# how many seconds til the note reachs half screen
BEAT_REACTION_TIME = 2


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--gallery_path", required=True, type=str)
    arg_parser.add_argument("--dump_path", required=True, type=str)
    arg_parser.add_argument("--fps", required=True, type=int)
    arg_parser.add_argument("--debug", action="store_true")
    args = arg_parser.parse_args()
    gallery_path = args.gallery_path
    dump_path = args.dump_path
    fps = args.fps
    debug = args.debug

    beatmapset_ids = os.listdir(gallery_path)
    for id in beatmapset_ids:
        try:
            generate_video(int(id), gallery_path, dump_path, fps, debug)
        except Exception as ex:
            print_exc()
            pass


def generate_video(id: int, gallery_root: str, dump_path: str, fps: int, debug: True):
    """
    main entry pt for generate video
    """

    OUTPUT_PATH_MP4_MUTE = f"{dump_path}/fh_{id}_mute.mp4"
    OUTPUT_PATH_MP4 = f"{dump_path}/fh_{id}.mp4"
    gallery_folder_path = f"{gallery_root}/{id}"

    # assert images with same dimensions
    img_names, sd_dimension = assert_image_dimension_consistent(
        gallery_folder_path)
    assert (sd_dimension[0]/sd_dimension[1] < 16/9)

    print(f"Images asserted to be in consistent dimension {sd_dimension}")

    # pick the beatmap that is closest to DIFFICULTY_DESIRED
    target_game_definition: osu_parsed_data = pick_desired_difficulty_beatmap(
        f"./beatmaps/{id}", TARGET_DIFFICULTY
    )
    print(
        f"Using version={target_game_definition.version}, difficulty={target_game_definition.overall_difficulty}")

    total_length_second = get_audio_length(
        f"./beatmaps/{id}/{target_game_definition.audio_filename}")
    print(f"Length is {total_length_second} seconds.")

    # getting the frames in which the image should change
    img_change_frames = get_img_change_frames(
        target_game_definition, total_length_second, fps)
    print(f"Number of images required: {len(img_change_frames)+1}")

    # compute the delta_w to expand the canvas to nearly 16:9
    delta_w = math.floor((sd_dimension[1] * 16 / 9 - sd_dimension[0]) / 2)
    assert (delta_w >= 0)
    dimension = (sd_dimension[0] + 2 * delta_w, sd_dimension[1])

    """
    this is an implementation where velocity is a function of note
    TODO: research velocity as a function of note and frame
    """
    frame_to_note_location_dict = dict()
    for time in target_game_definition.hit_objects:
        frame_number_center = math.floor(time * fps)

        # add note at center to center frame
        center_position = math.floor(dimension[0] * 0.5)
        frame_to_note_location_dict.setdefault(frame_number_center, list())
        frame_to_note_location_dict[frame_number_center].append(
            center_position)

        """
        delta_position = how many pixel moved for a frame
        DW / 1 Frame = W / (FPS * T)
        """
        delta_position_per_frame = dimension[0] / (fps * BEAT_REACTION_TIME)

        # frame number increase, note position decreases
        beat_position = center_position
        counter = 0
        while beat_position / dimension[0] >= -0.1:
            counter += 1
            beat_position -= delta_position_per_frame
            frame_number = frame_number_center + counter
            frame_to_note_location_dict.setdefault(frame_number, list())
            frame_to_note_location_dict[frame_number].append(
                math.floor(beat_position))

        # frame number decrease, note position increasews
        beat_position = center_position
        counter = 0
        while beat_position / dimension[0] <= 1.1:
            counter += 1
            beat_position += delta_position_per_frame
            frame_number = frame_number_center - counter
            frame_to_note_location_dict.setdefault(frame_number, list())
            frame_to_note_location_dict[frame_number].append(
                math.floor(beat_position))

    video_writer = cv2.VideoWriter(
        OUTPUT_PATH_MP4_MUTE, cv2.VideoWriter_fourcc(*'mp4v'), fps, dimension)
    img_ptr = 0

    total_frames = math.ceil(total_length_second * fps)
    for frame_number in range(total_frames):
        if frame_number % 100 == 99:
            print(f"frame {frame_number} of {total_frames}")

        if frame_number in img_change_frames:
            img_ptr += 1
            img_ptr %= len(img_names)
        sd_img = cv2.imread(img_names[img_ptr])
        canvas = cv2.copyMakeBorder(sd_img, left=delta_w, right=delta_w, top=0,
                                    bottom=0, borderType=cv2.BORDER_CONSTANT, value=(218, 167, 229))

        # add main beatbar
        gameplay_painter.add_main_beatbar(canvas)

        # add beatmarks
        notes = frame_to_note_location_dict.get(frame_number)
        if notes is not None:
            gameplay_painter.add_beatmarks(canvas, notes)

        # early abort for preview
        if debug:
            if frame_number >= fps * 10:
                break

        # write the frame
        video_writer.write(canvas)

    video_writer.release()

    # attach audio
    video = mpe.VideoFileClip(OUTPUT_PATH_MP4_MUTE)
    audio = mpe.AudioFileClip(
        f"./beatmaps/{id}/{target_game_definition.audio_filename}")
    video = video.set_audio(audio)

    video.write_videofile(OUTPUT_PATH_MP4, fps=fps)

    # remove mute version
    os.remove(OUTPUT_PATH_MP4_MUTE)


if __name__ == "__main__":
    main()
