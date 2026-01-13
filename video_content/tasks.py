import subprocess
import os
from django.conf import settings
from .models import Video


"""Dein Server speichert Videos als Dateien.
Die DB sagt, wo sie liegen.
Der Browser lädt URLs.
HLS setzt die Dateien wieder zu einem Video zusammen."""






#ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8 convert to hls format
# ffmpeg -i input_video.mp4 -c copy -hls_time 5 - hls_list_size 0 -f hls output.m3u8



def process_video(video_id):
    """gets video by id and process it into different resolutions"""
    print(f"Proccesing video id: {video_id}")
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'processing'
        video.save()

        source_path = video.video_file.path
        print(f"Source path: {source_path}")

        convert_hls(video_id, source_path)
        video.status = 'completed'
        video.hls_480p_path =f'videos/hls/{video.id}/480p'
        video.hls_720p_path = f'videos/hls/{video.id}/720p'
        video.hls_1080p_path = f'videos/hls/{video.id}/1080p'
        video.save()

        print(f"video id: {video_id} proccessed successfully")
    except Exception as error:
        print(f"{error}")
        video.status = 'failed'
        video.save()




def convert_hls(video_id, source_path):
    """converte video to hls format in 3 different resolutions
    creates folders and files in media/videos/hls/<video_id>/<resolution>/
    and runs ffmpeg command to convert the video"""
    resolutions = {
        '480p': '854:480',
        '720p': '1280:720',
        '1080p': '1920:1080'
    }
    for res_name, scale in resolutions.items():
        print(f"converting to {res_name}")
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos','hls',str(video_id),res_name)
        os.makedirs(output_dir, exist_ok=True)
        os.chmod(output_dir, 0o777)
        print(f" Output dir: {output_dir}")

        playlist_path = os.path.join(output_dir,'index.m3u8')
        segment_pattern = os.path.join(output_dir, 'segment%03d.ts')

        cmd = [
            'ffmpeg',
            '-y'
            '-i', source_path,
            '-vf', f'scale={scale}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-c:a', 'aac',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_segment_filename', segment_pattern,
            '-f', 'hls',
            playlist_path
        ]
        print(f" Running FFMPEG command...")
        print(f"Command: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True,  capture_output=True, text=True, timeout=120)
            print(f"{res_name} Done")
            files = os.listdir(output_dir)
            print(f"Created{files}")
        except subprocess.CalledProcessError as error:
            print(f"Error converting to {res_name}: {error.stderr}")
            print(f"Return code: {error.returncode}")
            print(f"STDERR: {error.stderr}")
            print(f"STDOUT: {error.stdout}")



