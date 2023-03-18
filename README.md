# osu-hero-generator

I got a ██████ addiction.

## Generation Workflow

### Step 1: Invoke `py ./order.py`.

This script downloads a bunch of osu beatmapset by the parameters,
choose the appropriate beat map and computes the number of images required for that beatmap.

| arg                	| description                                       |
|--------------------	|-------------------------------------------------	|
| count                 | how much songs, positive int eg 10                |
| fps                   | output video fps, positive int eg 120             |

TODO: expose more args

The console will return a csv table containing rows of beatmap id and number of images.

```raw
py ./order.py --fps 120
1883852, 75
1934416, 47
338251, 76
1749541, 280
1876784, 48
```

### Step 2: Generate some images

By any means, make a folder with the following structure and nothing else.

```raw
/your_folder
├── 1883852
│   ├── whatever.png
│   ├── ...
├── 1934416
│   ├── ...
├── ...
```

### Step 3: Invoke `./main.py`

This script generate the videos.

```raw
py ./main.py --gallery_path "C:\Users\Private\Desktop\stable_diffusion\gallery" --dump_path "C:\Users\Private\Desktop\stable_diffusion\hero"
```

## Literally 1984

Yo wtf this looks exactly like f-

![shocked](https://i.scdn.co/image/ab67616d00001e0269e59225913928f4155dd022)

