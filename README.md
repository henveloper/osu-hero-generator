the resemblance of the output to a certain kind of video is merely a coincidence

# `./img_count.py`

This file gets the number of images required for a set of beatmaps queries with hardcoded values.

The console will return the csv containing rows of beatmap id and number of images.

```raw
py ./img_count.py --fps 120 --difficulty 4.5
1883852, 75
1934416, 47
338251, 76
1749541, 280
1876784, 48
```

# `./main.py`

This script generate the videos

```raw
py ./main.py
```