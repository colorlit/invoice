import os
import subprocess

# directories
root_dir = os.getcwd()
input_dir = root_dir + r'\data\ffmpeg\inputs'
output_dir = root_dir + r'\data\ffmpeg\outputs'
executable_dir = root_dir + r'\libraries\ffmpeg\ffmpeg.exe'

files_list = []

for path in os.listdir(input_dir):
    if os.path.isfile(os.path.join(input_dir, path)):
        files_list.append(path)

# usage : ffmpeg -i input_filename output_filename
# edit2 : ext detection with split n sliding
for file_name in files_list:
    print(file_name)
    name_no_ext = file_name.split('.')[:-1]
    name_no_ext = "".join(name_no_ext)
    print(str(name_no_ext))
    subprocess.call([executable_dir, '-i', os.path.join(input_dir, file_name), os.path.join(output_dir, name_no_ext + ".wav")])

print("FFMPEG CONVERSION COMPLETE")