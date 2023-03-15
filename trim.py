from moviepy.editor import *
  
# uploading the video
video = VideoFileClip("./output/a.mp4")
  
video = video.subclip(0, 10)
video.write_videofile("./output/a-crop.mp4", fps=60)