import subprocess
import os
from django.conf import settings
from .models import Video

def convert_480p(source):
    target = source + '480p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd)

def convert_720p(source):
    target = source + '720p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd)

def convert_1080p(source):
    target = source + '1080p.mp4'
    cmd = 'ffmpeg -i "{}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source,target)
    subprocess.run(cmd)


def generate_thunbnail(source, time_frame=1):
    target = source + 'thumbnail.png'
    cmd = 'ffmpeg -i input.mp4 -ss 00:00:01.000 -vframes 1 output.png'.format(source, time_frame, target)
    subprocess.run(cmd)


#ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8 convert to hls format
# ffmpeg -i input_video.mp4 -c copy -hls_time 5 - hls_list_size 0 -f hls output.m3u8
def convert_hls(source):
    target = source + '.m3u8'
    cmd = 'ffmpeg -i "{}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{}"'.format(source,target)
    subprocess.run(cmd)


def process_video(video_id):
    pass
