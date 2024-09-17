import subprocess
import os
import json
import tempfile

def get_stream_info(file_path):
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def process_video(video_path, crop_start, crop_end, temp_dir):
    output_path = os.path.join(temp_dir, "processed_video.mp4")
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(crop_start),
        '-to', str(float(get_stream_info(video_path)['format']['duration']) - crop_end),
        '-c:v', 'libx264',
        '-an',
        '-y',
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

def process_audio(audio_path, audio_start, video_duration, temp_dir):
    output_path = os.path.join(temp_dir, "processed_audio.aac")
    cmd = [
        'ffmpeg',
        '-i', audio_path,
        '-ss', str(audio_start),
        '-t', str(video_duration),
        '-c:a', 'aac',
        '-y',
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

def combine_video_audio(video_path, audio_path, output_path):
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-shortest',
        '-y',
        output_path
    ]
    subprocess.run(cmd, check=True)

def merge_video_audio(video_path, audio_path, audio_start, crop_start, crop_end):
    with tempfile.TemporaryDirectory() as temp_dir:
        processed_video = process_video(video_path, crop_start, crop_end, temp_dir)
        video_info = get_stream_info(processed_video)
        video_duration = float(video_info['format']['duration'])
        
        processed_audio = process_audio(audio_path, audio_start, video_duration, temp_dir)
        
        output_path = "final_output.mp4"
        combine_video_audio(processed_video, processed_audio, output_path)
    
    return output_path

def main():
    video_path = input("Enter the path to the MKV video file: ")
    audio_path = input("Enter the path to the MP3 audio file: ")

    if not os.path.exists(video_path):
        print("Error: Video file not found.")
        return
    if not os.path.exists(audio_path):
        print("Error: Audio file not found.")
        return

    video_info = get_stream_info(video_path)
    original_duration = float(video_info['format']['duration'])
    print(f"Original video duration: {original_duration:.2f} seconds")

    crop_start = float(input("Enter the number of seconds to crop from the start of the video (0 for no cropping): "))
    crop_end = float(input("Enter the number of seconds to crop from the end of the video (0 for no cropping): "))

    new_duration = original_duration - crop_start - crop_end
    if new_duration <= 0:
        print("Error: Invalid cropping values. The resulting video would have no duration.")
        return

    print(f"New video duration after cropping: {new_duration:.2f} seconds")

    audio_start = float(input("Enter the start time for the audio (in seconds): "))

    try:
        output_path = merge_video_audio(video_path, audio_path, audio_start, crop_start, crop_end)
        print(f"Successfully created: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        print(f"FFmpeg error output:\n{e.stderr.decode('utf-8')}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
