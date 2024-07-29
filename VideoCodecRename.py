"""
Release Notes: 1.2

- Removed import serial line.
- Updated version number.
- Replaced <'{}'.format(stream.codec())> with <stream.codec()>.
- Replaced " with ' for consistency.
- Updated version number in window.
- Replaced <if ex in file.lower()> with <if ex in file.lower().lower()> to ensure that extensions of any case will be read properly.
- Created a dictionary for the video codec counts to clean up the code: VideoCodecCounts[].
- Function check_pressed renamed to find_videos_pressed.
- Changed how extensions are handled. Can now handle extensions of any length, such as .m2ts.
- Added file counts to all operations.
- Standardized all output formatting for all operations.
- Set each operation to reset variable TotalCount after it ran to ensure accurate counts between operations.
- Replaced <path = path_entry.get()> with <path = path_entry.get()>.
"""

import tkinter as tk
import os
from ffprobe3 import FFProbe
import datetime
import re

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
    path_entry = tk.Entry(window, width=100)
    path_entry.pack()
    return path_entry

def setup_buttons(window):
    buttons = [
        ('List All Files', 'grey', list_all_pressed),
        ('Find Video Files', 'blue', find_videos_pressed),
        ('Add Video Codec To File Name', 'green', add_pressed),
        ('Remove Video Codec From File Name', 'red', remove_pressed),
        ('Clear Output Display', 'orange', clear_screen_pressed, 25)
    ]
    
    for text, color, command, *width in buttons:
        button = tk.Button(window, text=text, width=width[0] if width else 50, height=2, bg=color, fg='white')
        button.pack()
        button.bind('<Button-1>', command)

def setup_output_box(window):
    tk.Label(window, text='Output').pack()
    output_box = tk.Text(window, width=100, height=50)
    output_box.pack()
    return output_box

def clear_screen_pressed(event):
    output_box.delete(1.0, tk.END)

def add_pressed(event):
    path = path_entry.get()
    total_count = 0
    video_count = 0
    files = []

    output_box.insert('1.0', 'Add Operation Started: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

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
                            output_box.insert('1.0', 'New name: ' + new_name + '\n')
                except:
                    VIDEO_CODEC_COUNTS['error'] += 1
                    error_name = current[:-4] + '[ERROR]' + current[-4:]
                    os.rename(current, error_name)
                    output_box.insert('1.0', 'Error renaming: ' + error_name + '\n')

    output_box.insert('1.0', '-' * 20 + '\n' + f'Files Renamed: {video_count}\nFiles Scanned: {total_count}\nErrors Encountered: {VIDEO_CODEC_COUNTS["error"]}\n' + 'Video Rename Operation Completed: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

def find_videos_pressed(event):
    path = path_entry.get()
    total_count = 0

    output_box.insert('1.0', 'Video Search Operation Started: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            extension = os.path.splitext(file)[1].lower()
            if extension in [ext.lower() for ext in VIDEO_EXTENSIONS]:
                current = os.path.join(r, file)
                total_count += 1
                output_box.insert('1.0', current + '\n')

    output_box.insert('1.0', '-' * 20 + '\n' + f'Videos Found: {total_count}\n' + 'Video Search Operation Completed: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

def list_all_pressed(event):
    path = path_entry.get()
    total_count = 0

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            current = os.path.join(r, file)
            total_count += 1
            output_box.insert('1.0', current + '\n')

    output_box.insert('1.0', '-' * 20 + '\n' + f'Files Found: {total_count}\n' + 'File List Operation Completed: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

def remove_pressed(event):
    path = path_entry.get()
    total_count = 0

    output_box.insert('1.0', 'Remove Operation Started: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

    for r, d, f in sorted(os.walk(path, topdown=True)):
        for file in f:
            current = os.path.join(r, file)
            if '[' in file:
                base_name = re.sub(r'\[.*?\]', '', current)
                final_name = base_name[:-4] + base_name[-4:]
                os.rename(current, final_name)
                total_count += 1
                output_box.insert('1.0', 'New Name: ' + final_name + '\n')

    output_box.insert('1.0', '-' * 20 + '\n' + f'Files Renamed: {total_count}\n' + 'Codec Remove Operation Completed: ' + str(datetime.datetime.now()) + '\n' + '-' * 20 + '\n')

window = setup_window()
path_entry = setup_entry(window)
setup_buttons(window)
output_box = setup_output_box(window)
window.mainloop()
