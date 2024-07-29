import tkinter as tk
import os
from ffprobe3 import FFProbe
import datetime
import re
import subprocess
import json
import threading

VERSION_NUMBER = '1.2.0'

VIDEO_EXTENSIONS = ['.mov', '.mp4', '.mkv', '.avi', '.m4v', '.mpg']
VIDEO_CODECS = ['utvideo', 'dnxhd', 'h265', 'h264', 'xvid', 'mpeg4', 'msmpeg4v3', 'error']
VIDEO_CODEC_COUNTS = {codec: 0 for codec in VIDEO_CODECS}

def setup_window():
    window = tk.Tk()
    greeting = tk.Label(window, text=f'CodecRenameUtility {VERSION_NUMBER}', fg='white', bg='purple')
    greeting.pack()
    return window

def setup_entry(window):
    tk.Label(window, text='Working Directory').pack()
    path_entry = tk.Entry(window, width=350)
    path_entry.pack()
    return path_entry

def setup_buttons(window):
    buttons = [
        ('List All Files', 'grey', list_all_pressed),
        ('Find Video Files (list codec)', 'blue', find_videos_pressed),
        ('Find non-HEVC', 'red', find_nonHEVC_pressed),
        #('Add Video Codec To File Name', 'green', add_pressed),
        #('Remove Video Codec From File Name', 'red', remove_pressed),
        ('Clear Output Display', 'orange', clear_screen_pressed, 25)
    ]
    
    for text, color, command, *width in buttons:
        button = tk.Button(window, text=text, width=width[0] if width else 50, height=2, bg=color, fg='white')
        button.pack()
        button.bind('<Button-1>', command)

def setup_output_box(window):
    tk.Label(window, text='Output').pack(fill='x')
    output_box = tk.Text(window, width=100, height=50)
    output_box.pack(fill='both', expand=True)
    return output_box

def clear_screen_pressed(event):
    output_box.delete(1.0, tk.END)

def add_pressed(event):
    path = path_entry.get()
    total_count = 0
    video_count = 0
    files = []

    output_box.insert('1.0', f'Add Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            total_count += 1
            extension = os.path.splitext(file)[1].lower()
            if '[' not in file and extension in VIDEO_EXTENSIONS:
                current = os.path.join(r, file)
                try:
                    metadata = FFProbe(str(current))
                    for stream in metadata.streams:
                        codec = stream.codec()
                        if codec in VIDEO_CODECS:
                            video_count += 1
                            VIDEO_CODEC_COUNTS[codec] += 1
                            new_name = f'{current[:-len(extension)]}[{codec}]{extension}'
                            os.rename(current, new_name)
                            output_box.insert('1.0', f'New name: {new_name}\n')
                except:
                    VIDEO_CODEC_COUNTS['error'] += 1
                    error_name = f'{current[:-4]}[ERROR]{current[-4:]}'
                    os.rename(current, error_name)
                    output_box.insert('1.0', f'Error renaming: {error_name}\n')

    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {video_count}\nFiles Scanned: {total_count}\nErrors Encountered: {VIDEO_CODEC_COUNTS["error"]}\nVideo Rename Operation Completed: {datetime.datetime.now()}\n{"-" * 20}\n')

def get_video_codec(file_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'json', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return info['streams'][0]['codec_name'] if info['streams'] else 'unknown'
        else:
            raise Exception(result.stderr)
    except Exception as e:
        return f'Error: {str(e)}'

def find_videos(path):
    total_count = 0

    start_time = datetime.datetime.now()  # Record start time
    output_box.insert('1.0', f'Video Search Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            extension = os.path.splitext(file)[1].lower()
            if extension in VIDEO_EXTENSIONS:
                current = os.path.join(r, file)
                total_count += 1
                codec = get_video_codec(current)
                output_box.insert('1.0', f'{current} - Codec: {codec}\n')
                output_box.update_idletasks()
    
    end_time = datetime.datetime.now()  # Record end time
    runtime = end_time - start_time  # Calculate runtime
    output_box.insert('1.0', f'{"-" * 20}\nVideos Found: {total_count}\nVideo Search Operation Completed: {datetime.datetime.now()}\nTotal Runtime: {runtime}\n{"-" * 20}\n')

def find_videos_pressed(event):
    path = path_entry.get()
    threading.Thread(target=find_videos, args=(path,)).start()

def find_nonHEVC(path):
    total_count = 0

    start_time = datetime.datetime.now()
    output_box.insert('1.0', f'Video Search Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            extension = os.path.splitext(file)[1].lower()
            if extension in VIDEO_EXTENSIONS:
                current = os.path.join(r, file)
                codec = get_video_codec(current)
                if codec != "hevc":
                    total_count += 1
                    output_box.insert('1.0', f'{current} - Codec: {codec}\n')
                    output_box.update_idletasks()
    if total_count == 0:
        output_box.insert('1.0', f'\n █████  ██      ██          ███████ ██ ██      ███████ ███████     ██   ██ ███████ ██    ██  ██████ \n██   ██ ██      ██          ██      ██ ██      ██      ██          ██   ██ ██      ██    ██ ██      \n███████ ██      ██          █████   ██ ██      █████   ███████     ███████ █████   ██    ██ ██      \n██   ██ ██      ██          ██      ██ ██      ██           ██     ██   ██ ██       ██  ██  ██      \n██   ██ ███████ ███████     ██      ██ ███████ ███████ ███████     ██   ██ ███████   ████    ██████ \n\n')

    end_time = datetime.datetime.now()  # Record end time
    runtime = end_time - start_time  # Calculate runtime
    output_box.insert('1.0', f'{"-" * 20}\nVideos Found: {total_count}\nVideo Search Operation Completed: {datetime.datetime.now()}\nTotal Runtime: {runtime}\n{"-" * 20}\n')

def find_nonHEVC_pressed(event):
    path = path_entry.get()
    threading.Thread(target=find_nonHEVC, args=(path,)).start()

def list_all(path):
    total_count = 0

    start_time = datetime.datetime.now()
    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            current = os.path.join(r, file)
            total_count += 1
            output_box.insert('1.0', f'{current}\n')
    
    end_time = datetime.datetime.now()  # Record end time
    runtime = end_time - start_time  # Calculate runtime
    output_box.insert('1.0', f'{"-" * 20}\nFiles Found: {total_count}\nFile List Operation Completed: {datetime.datetime.now()}\nTotal Runtime: {runtime}\n{"-" * 20}\n')

def list_all_pressed(event):
    path = path_entry.get()
    threading.Thread(target=list_all, args=(path,)).start()

def remove_pressed(event):
    path = path_entry.get()
    total_count = 0

    output_box.insert('1.0', f'Remove Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            current = os.path.join(r, file)
            if '[' in file:
                base_name = re.sub(r'\[.*?\]', '', current)
                final_name = f'{base_name[:-4]}{base_name[-4:]}'
                os.rename(current, final_name)
                total_count += 1
                output_box.insert('1.0', f'New Name: {final_name}\n')

    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {total_count}\nCodec Remove Operation Completed: {datetime.datetime.now()}\n{"-" * 20}\n')

window = setup_window()
path_entry = setup_entry(window)
setup_buttons(window)
output_box = setup_output_box(window)

window.mainloop()
