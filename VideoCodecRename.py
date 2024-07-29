import tkinter as tk
from tkinter import ttk
import os
import datetime
import subprocess
import json
import threading

VERSION_NUMBER = '1.2.0'

VIDEO_EXTENSIONS = ['.mov', '.mp4', '.mkv', '.avi', '.m4v', '.mpg']
VIDEO_CODECS = ['utvideo', 'dnxhd', 'h265', 'h264', 'xvid', 'mpeg4', 'msmpeg4v3', 'error']
VIDEO_CODEC_COUNTS = {codec: 0 for codec in VIDEO_CODECS}

# Global flag to control processing
stop_flag = threading.Event()

### Setup functions -------------------------------------------------------------------------

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
        ('Clear Output Display', 'orange', clear_screen_pressed, 25),
        ('Stop Processing', 'black', stop_processing_pressed)  
    ]
    
    button_frame = tk.Frame(window)  
    button_frame.pack(pady=10)  
    
    for text, color, command, *width in buttons:
        button = tk.Button(button_frame, text=text, width=width[0] if width else 20, height=2, bg=color, fg='white')
        button.pack(side='left', padx=5, pady=5)
        button.bind('<Button-1>', command)

def setup_output_box(window):
    tk.Label(window, text='Output').pack(fill='x')
    output_box = tk.Text(window, width=100, height=50)
    output_box.pack(fill='both', expand=True)
    return output_box

def setup_progress_bar(window):
    progress_bar = ttk.Progressbar(window, orient='horizontal', length=100, mode='determinate')
    progress_bar.pack(fill='x', padx=10, pady=5)
    return progress_bar

### Helper functions -------------------------------------------------------------------------

def clear_screen_pressed(event):
    output_box.delete(1.0, tk.END)
    progress_bar['value'] = 0

def update_progress_bar(current_index, total_files):
    progress_bar['maximum'] = total_files
    progress_bar['value'] = current_index
    window.update_idletasks()

def is_video_file(file_name):
    # Extract the file extension and check against VIDEO_EXTENSIONS
    extension = os.path.splitext(file_name)[1].lower()
    return extension in VIDEO_EXTENSIONS

def get_all_files(path):
    return [os.path.join(r, file) for r, d, f in sorted(os.walk(path, topdown=True)) for file in f]

def stop_processing_pressed(event):
    stop_flag.set()  # Signal to stop processing

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
    
def perform_operation_with_timing(operation_name, operation, *args):
    start_time = datetime.datetime.now()
    output_box.insert('1.0', f'{operation_name} Started: {start_time}\n{"-" * 20}\n')
    try:
        operation(*args)
    finally:
        end_time = datetime.datetime.now()
        runtime = end_time - start_time
        output_box.insert('1.0', f'{"-" * 20}\n{operation_name} Completed: {end_time}\nTotal Runtime: {runtime}\n{"-" * 20}\n')

### Real functions -------------------------------------------------------------------------

def find_videos(path):
    total_count = 0

    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))

    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            output_box.insert('1.0', 'Processing stopped by user.\n')
            break
        if is_video_file(file):
            total_count += 1
            codec = get_video_codec(file)
            output_box.insert('1.0', f'{file} - Codec: {codec}\n')
            output_box.update_idletasks()
        
        update_progress_bar(idx + 1, len(all_files))

def find_videos_pressed(event):
    global stop_flag
    stop_flag.clear()  # Reset the stop flag
    path = path_entry.get()
    threading.Thread(target=perform_operation_with_timing, args=('Video Search Operation', find_videos, path)).start()

def find_nonHEVC(path):
    total_count = 0
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))
    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            output_box.insert('1.0', 'Processing stopped by user.\n')
            break
        if is_video_file(file):
            codec = get_video_codec(file)
            if codec != "hevc":
                total_count += 1
                output_box.insert('1.0', f'{file} - Codec: {codec}\n')
                output_box.update_idletasks()
        update_progress_bar(idx + 1, len(all_files))

    if total_count == 0 and not stop_flag.is_set():
        output_box.insert('1.0', f'\n █████  ██      ██          ███████ ██ ██      ███████ ███████     ██   ██ ███████ ██    ██  ██████ \n██   ██ ██      ██          ██      ██ ██      ██      ██          ██   ██ ██      ██    ██ ██      \n███████ ██      ██          █████   ██ ██      █████   ███████     ███████ █████   ██    ██ ██      \n██   ██ ██      ██          ██      ██ ██      ██           ██     ██   ██ ██       ██  ██  ██      \n██   ██ ███████ ███████     ██      ██ ███████ ███████ ███████     ██   ██ ███████   ████    ██████ \n\n')

def find_nonHEVC_pressed(event):
    global stop_flag
    stop_flag.clear()  # Reset the stop flag
    path = path_entry.get()
    threading.Thread(target=perform_operation_with_timing, args=('Non-HEVC Video Search Operation', find_nonHEVC, path)).start()

def list_all(path):
    total_count = 0
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))
    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            output_box.insert('1.0', 'Processing stopped by user.\n')
            break
        total_count += 1
        output_box.insert('1.0', f'{file}\n')
        update_progress_bar(idx + 1, len(all_files))

def list_all_pressed(event):
    global stop_flag
    stop_flag.clear()  # Reset the stop flag
    path = path_entry.get()
    threading.Thread(target=perform_operation_with_timing, args=('File List Operation', list_all, path)).start()


#def add_pressed(event):
#    path = path_entry.get()
#    total_count = 0
#    video_count = 0
#    files = []
#
#    output_box.insert('1.0', f'Add Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')
#
#    for r, d, f in sorted(os.walk(path, topdown=True)):
#        for file in f:
#            total_count += 1
#            if is_video_file(file) and '[' not in file:
#                current = os.path.join(r, file)
#                try:
#                    metadata = FFProbe(str(current))
#                    for stream in metadata.streams:
#                        codec = stream.codec()
#                        if codec in VIDEO_CODECS:
#                            video_count += 1
#                            VIDEO_CODEC_COUNTS[codec] += 1
#                            new_name = f'{current[:-len(extension)]}[{codec}]{extension}'
#                            os.rename(current, new_name)
#                            output_box.insert('1.0', f'New name: {new_name}\n')
#                except:
#                    VIDEO_CODEC_COUNTS['error'] += 1
#                    error_name = f'{current[:-4]}[ERROR]{current[-4:]}'
#                    os.rename(current, error_name)
#                    output_box.insert('1.0', f'Error renaming: {error_name}\n')
#
#    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {video_count}\nFiles Scanned: {total_count}\nErrors Encountered: {VIDEO_CODEC_COUNTS["error"]}\nVideo Rename Operation Completed: {datetime.datetime.now()}\n{"-" * 20}\n')

#def remove_pressed(event):
#    path = path_entry.get()
#    total_count = 0
#
#    output_box.insert('1.0', f'Remove Operation Started: {datetime.datetime.now()}\n{"-" * 20}\n')
#
#    for r, d, f in sorted(os.walk(path, topdown=True)):
#        for file in f:
#            current = os.path.join(r, file)
#            if '[' in file:
#                base_name = re.sub(r'\[.*?\]', '', current)
#                final_name = f'{base_name[:-4]}{base_name[-4:]}'
#                os.rename(current, final_name)
#                total_count += 1
#                output_box.insert('1.0', f'New Name: {final_name}\n')
#
#    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {total_count}\nCodec Remove Operation Completed: {datetime.datetime.now()}\n{"-" * 20}\n')

window = setup_window()
path_entry = setup_entry(window)
setup_buttons(window)
progress_bar = setup_progress_bar(window)
output_box = setup_output_box(window)

window.mainloop()
