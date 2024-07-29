import tkinter as tk
from tkinter import ttk
import os
import datetime
import subprocess
import json
import threading

APP_NAME = 'CodecFinderUtility'
VERSION_NUMBER = '2.0-dev'

VIDEO_EXTENSIONS = ['.mov', '.mp4', '.mkv', '.avi', '.m4v', '.mpg']

stop_flag = threading.Event()

### Setup functions -------------------------------------------------------------------------

def setup_window():
    window = tk.Tk()
    window.title(f'{APP_NAME} {VERSION_NUMBER}')
    return window

def setup_entry(window):
    tk.Label(window, text='Working Directory').pack()
    path_entry = tk.Entry(window, width=200)
    path_entry.pack()
    return path_entry

def setup_buttons(window):
    main_frame = tk.Frame(window)
    main_frame.pack(pady=10, padx=10, expand=True, anchor='center')

    frames = {
        'list': tk.Frame(main_frame),
        'edit': tk.Frame(main_frame),
        'meta': tk.Frame(main_frame)
    }

    for frame in frames.values():
        frame.pack(side='left', padx=10, fill='y')

    buttons = {
        'list': [
            ('List All Files', 'grey', lambda event: start_thread(list_all, path_entry.get(), 'File List Operation')),
            ('Find Video Files (list codec)', 'blue', lambda event: start_thread(find_videos, path_entry.get(), 'Video Search Operation')),
            ('Find non-HEVC', 'purple', lambda event: start_thread(find_nonHEVC, path_entry.get(), 'Non-HEVC Video Search Operation'))
        ],
        'edit': [
            ('Add Codec To Name', 'green', lambda event: start_thread(add_codec_to_name, path_entry.get(), 'Add Video Codec To File Name')),
            ('Remove Codec From Name', 'red', lambda event: start_thread(remove_codec_from_name, path_entry.get(), 'Remove Video Codec From File Name'))
        ],
        'meta': [
            ('Clear Output Display', 'orange', lambda event: clear_screen_pressed(event)),
            ('Stop Processing', 'red', lambda event: stop_processing_pressed(event))
        ]
    }

    def create_buttons(buttons_list, frame):
        for text, color, command in buttons_list:
            button = tk.Button(frame, text=text, width=20 if frame != frames['meta'] else 25, height=2, bg=color, fg='white')
            button.pack(pady=5)
            button.bind('<Button-1>', command)

    for key, button_list in buttons.items():
        create_buttons(button_list, frames[key])


def setup_output_box(window):
    tk.Label(window, text='Output').pack(fill='x')
    output_box = tk.Text(window, width=100, height=50)
    output_box.pack(fill='both', expand=True)
    output_box.tag_configure('bold', font=('Helvetica', 10, 'bold'))
    output_box.tag_configure('red', foreground='white', background='red')
    output_box.tag_configure('UI', foreground='white', background='gray')
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
    extension = os.path.splitext(file_name)[1].lower()
    return extension in VIDEO_EXTENSIONS

def get_all_files(path):
    return [os.path.join(r, file) for r, d, f in sorted(os.walk(path, topdown=True)) for file in f]

def stop_processing_pressed(event):
    stop_flag.set()
    output_box.insert('1.0', 'Processing stopped by user.', ('bold', 'red'), '\n')

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
    output_box.insert('1.0', f'{operation_name} Started: {start_time}\n{"-" * 20}\n', ('UI'))
    try:
        operation(*args)
    finally:
        end_time = datetime.datetime.now()
        runtime = end_time - start_time
        output_box.insert('1.0', f'{"-" * 20}\nTotal Runtime: {runtime}\n{operation_name} Completed: {end_time}\n', ('UI'))

def start_thread(operation, *args):
    global stop_flag
    stop_flag.clear()
    threading.Thread(target=perform_operation_with_timing, args=(args[-1], operation) + args[:-1]).start()

### Real functions -------------------------------------------------------------------------

def find_videos(path):
    total_count = 0

    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))

    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            break
        if is_video_file(file):
            total_count += 1
            codec = get_video_codec(file)
            output_box.insert('1.0', f'{file} - Codec: {codec}\n')
            output_box.update_idletasks()
        
        update_progress_bar(idx + 1, len(all_files))
    output_box.insert('1.0', f'Total Videos Found: {total_count}\n', ('bold', 'UI'))

def find_nonHEVC(path):
    total_count = 0
    folder_stats = {}
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))
    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            break
        if is_video_file(file):
            codec = get_video_codec(file)
            if codec != "hevc":
                total_count += 1
                output_box.insert('1.0', f'{file} - Codec: {codec}\n')
                output_box.update_idletasks()
                parent_folder = os.path.basename(os.path.dirname(file))
                folder = os.path.join(os.path.basename(path), parent_folder)
                if folder not in folder_stats:
                    folder_stats[folder] = 0
                folder_stats[folder] += 1
        update_progress_bar(idx + 1, len(all_files))

    if total_count != 0:
        for folder, count in folder_stats.items():
            output_box.insert('1.0', f'  Non-HEVC Videos Count: {count}\n\n')
            output_box.insert('1.0', f'Folder: {folder}\n')
            output_box.update_idletasks()
        output_box.insert('1.0', f'Total non-HEVC Found: {total_count}\n', ('bold', 'UI'))
        
    if total_count == 0 and not stop_flag.is_set():
        output_box.insert('1.0', f'\n █████  ██      ██          ███████ ██ ██      ███████ ███████     ██   ██ ███████ ██    ██  ██████ \n██   ██ ██      ██          ██      ██ ██      ██      ██          ██   ██ ██      ██    ██ ██      \n███████ ██      ██          █████   ██ ██      █████   ███████     ███████ █████   ██    ██ ██      \n██   ██ ██      ██          ██      ██ ██      ██           ██     ██   ██ ██       ██  ██  ██      \n██   ██ ███████ ███████     ██      ██ ███████ ███████ ███████     ██   ██ ███████   ████    ██████ \n\n')

def list_all(path):
    total_count = 0
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))
    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            break
        total_count += 1
        output_box.insert('1.0', f'{file}\n')
        update_progress_bar(idx + 1, len(all_files))

    output_box.insert('1.0', f'Total Files Found: {total_count}\n', ('bold', 'UI'))

def add_codec_to_name(path):
    errors = 0
    total_count = 0
    video_count = 0
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))

    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            break
        total_count += 1
        if is_video_file(file):
            extension = os.path.splitext(file)[1]
            try:
                codec = get_video_codec(file)
                base_name = os.path.splitext(file)[0]
                if f'[{codec}]' not in base_name:
                    new_name = f'{base_name}[{codec}]{extension}'
                    os.rename(file, new_name)
                    video_count += 1
                    output_box.insert('1.0', f'Renamed: {new_name}\n')
                else:
                    output_box.insert('1.0', f'Skipped (codec already in name): {file}\n')
            except Exception as e:
                errors += 1
                error_name = f'{base_name}[ERROR]{extension}'
                os.rename(file, error_name)
                output_box.insert('1.0', f'Error renaming: {error_name}\n')
        update_progress_bar(idx + 1, len(all_files))

    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {video_count}\nFiles Scanned: {total_count}\nErrors Encountered: {errors}\n', ('UI'))


def remove_codec_from_name(path):
    total_count = 0
    errors = 0
    all_files = get_all_files(path)
    update_progress_bar(0, len(all_files))

    for idx, file in enumerate(all_files):
        if stop_flag.is_set():
            break
        if is_video_file(file):
            codec = get_video_codec(file)
            if codec:
                base_name = os.path.splitext(file)[0]
                extension = os.path.splitext(file)[1]
                if f'[{codec}]' in base_name:
                    final_name = f'{base_name.split(f"[{codec}]")[0]}{extension}'
                    try:
                        os.rename(file, final_name)
                        total_count += 1
                        output_box.insert('1.0', f'Renamed: {final_name}\n')
                    except Exception as e:
                        errors += 1
                        output_box.insert('1.0', f'Error renaming: {file} - {str(e)}\n')
        update_progress_bar(idx + 1, len(all_files))

    output_box.insert('1.0', f'{"-" * 20}\nFiles Renamed: {total_count}\nErrors Encountered: {errors}\nCodec Remove Operation Completed.\n', ('UI'))



window = setup_window()
path_entry = setup_entry(window)
setup_buttons(window)
progress_bar = setup_progress_bar(window)
output_box = setup_output_box(window)

window.mainloop()
