from moviepy.editor import *
  
# uploading the video
video = VideoFileClip("./output/b.mp4")
  
video = video.subclip(0, 15)
video.write_videofile("./output/c.mp4", fps=60)