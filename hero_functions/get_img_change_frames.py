import math

from hero_functions.osu_parser import osu_parsed_data
def get_img_change_frames(game_definition: osu_parsed_data, game_length: float, fps: int):
    img_change_frames = set()

    beatlength = None
    for i in range(len(game_definition.timing_points)):
        time, beatlength_this, measure = game_definition.timing_points[i]
        if beatlength_this > 0:
            beatlength = beatlength_this
        next_time = game_length
        if i < len(game_definition.timing_points) - 1:
            next_time, _, _ = game_definition.timing_points[i+1]

        while time < next_time:
            img_change_frames.add(math.floor(time * fps))
            time += beatlength * measure

    return img_change_frames