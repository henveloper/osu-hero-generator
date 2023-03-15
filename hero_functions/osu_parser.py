from typing import Tuple
from dataclasses import dataclass

@dataclass
class osu_parsed_data:
    """
    [GENERAL]
    """
    audio_filename: str
    # time of silence before audio plays
    audio_lead_in: float

    """
    [METADATA]
    """
    # difficulty
    version: str

    """
    [DIFFICULTY]
    """
    # 0-10
    overall_difficulty: float

    # 0-10, need research
    approach_rate: float

    """
    [TIMING POINTS]
    """
    # timing points - (time, beatlength, number of beats in a measure)
    timing_points: list[Tuple[float, float, int]]

    """
    [HIT OBJECTS]
    """
    # hit objects - time
    hit_objects: list[float]

# https://osu.ppy.sh/wiki/en/Client/File_formats/Osu_%28file_format%29
def osu_parser(osu_file_path: str) -> osu_parsed_data:
    # for now, just get the milliseconds
    lines = None
    with open(osu_file_path, "r", encoding="UTF-8") as fd:
        lines = fd.read().split("\n")
    

    section = None
    data = osu_parsed_data(None, None, None, None, None, None, None)

    for line in lines:
        if line == "":
            # ignore empty line
            continue

        # header line
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue

        if section == "General":
            if line.startswith("AudioFilename: "):
                data.audio_filename = line.replace("AudioFilename: ", "")
            if line.startswith("AudioLeadIn: "):
                data.audio_lead_in = int(line.replace("AudioLeadIn: ", ""))

        if section == "Metadata":
            if line.startswith("Version:"):
                data.version = line.replace("Version:", "")
        
        if section == "Difficulty":
            if line.startswith("ApproachRate:"):
                data.approach_rate = float(line.replace("ApproachRate:", ""))

            if line.startswith("OverallDifficulty:"):
                data.overall_difficulty = float(line.replace("OverallDifficulty:", ""))

        if section == "TimingPoints":
            if data.timing_points is None:
                data.timing_points = list()
            time_ms, beat_length_ms, measure_beat_number, *_ = line.split(",")
            data.timing_points.append((float(time_ms) / 1000.0, float(beat_length_ms) / 1000.0, int(measure_beat_number)))

        if section == "HitObjects":
            if data.hit_objects is None:
                data.hit_objects = list()
            x, y, time, *_ = line.split(",")
            data.hit_objects.append(int(time) / 1000)

    return data
