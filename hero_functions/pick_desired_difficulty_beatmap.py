import os
from hero_functions.osu_parser import osu_parser


def pick_desired_difficulty_beatmap(beatmap_asset_folder_path: str, desired_difficulty: float):
    """
    TODO: comments
    """
    target_game_definition = None
    min_target_delta = None
    for file in os.listdir(beatmap_asset_folder_path):
        if file == "a.osu" or not file.endswith(".osu"):
            continue
        game_definition = osu_parser(f"{beatmap_asset_folder_path}/{file}")
        difficulty_delta_abs = abs(
            game_definition.overall_difficulty - desired_difficulty)
        if target_game_definition is None:
            target_game_definition = game_definition
            min_target_delta = difficulty_delta_abs
            continue
        if difficulty_delta_abs <= min_target_delta:
            target_game_definition = game_definition
            min_target_delta = difficulty_delta_abs

    return target_game_definition
