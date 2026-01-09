import subprocess

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