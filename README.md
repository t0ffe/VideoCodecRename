# VideoCodecRename
Python program using ffprobe3 to recursively search all files in a directory, identify video files, and add their codec to the file name for easy filtering in any system. Easily modified to find, rename, move, and sort all kinds of files using ffmpeg. This is just the video specific program.

![VideoCodecRename_Main](https://github.com/user-attachments/assets/cbfbc240-d185-44e0-b82e-7a34cda73a3d)

It requires ffprobe3, which can be pip installed. 

## Some instructions:

Start the program, and paste or type in the directory you'd like to work with in the "Working Directory" field at the top. 
Press the "List All Files" button to see all files in the directory and all the directories it contains(recursive lookup). 
Use the "Clear Output Display" button to clear the screen, if needed. 

## Descriptions of buttons and features:

### "List All Files":

Show all files of all types found in the directory(recursive lookup).
No changes are made to files using this opti

### "Find Video Files (list codec)": 

Attempts to open every file with ffmpeg and read its stream data and determine the codec used for stream 0(usually the main video stream for video files). 
Prints the file directory and name, as well as the video codec to the output box in the main window.
No changes are made to files using this option.

### "Find non-HEVC or non-AV1": 

Prints all non HEVC or AV1 files, their location and codec.
Gives a summary of how many such files are found in each directory under the "Working Directory".
No changes are made to files using this opti

### "Add Codec To Name":
  
This renames the file by adding [<codec>] before the file extension. Example: cats.mp4, encoded with h265/HEVC becomes cats[hevc].mp4. 
The square brackets([]) were chosen as media software such as Plex, EMby, and Jellyfin will ignore anything in brackets in the file name. 

"Remove Codec From Name":
  
This button "undoes" the "Add Video Codec To File Name" actions. 
It doesn't simply reverse the changes like "undo", it checks the files names for "[<codec>]" and removes any that match with the file's codec.

"Clear Output Display":
  
This button just wipes the screen, so you can start fresh. I find it helpful as the output can become a bit messy.
