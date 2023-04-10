import argparse
import os
import sys
import subprocess
import shlex
import time
import multiprocessing as mp
from shutil import which

parser = argparse.ArgumentParser(
    prog='ShareFlix',
    description='Allows anyone to stream video with sound over VOIP',
    epilog="Stream only legal linux.iso's!")


if not which('vlc'):
    parser.exit(1, message='vlc is not installed')
if not which('ffmpeg'):
    parser.exit(1, message='ffmpeg is not installed')
if not which('pactl'):
    parser.exit(1, message='pactl is not installed')


parser.add_argument(
    '-i',
    '--input',
    required=True, 
    type=str,
    help='Path to video file')
parser.add_argument(
    '-p',
    '--port',
    type=int,
    help='Port of stream',
    default=8554)
parser.add_argument(
    '-n',
    '--name',
    default='ShareFlix',
    type=str,
    help='Name of virtual camera')
parser.add_argument(
    '-w',
    '--width',
    default=720,
    type=int,
    help='Width of video output. (Skype needs less than 720)')
parser.add_argument(
    '-l', 
    '--loopback', 
    default=1, 
    type=int,
    help='Add more audio sources to stream (such as mic).')
parser.add_argument(
    '--flip',
    action='store_true',
    help='Mirror the screen horizontally.')
parser.add_argument(
    '--mic',
    action='store_true',
    help='Pass sound from microphone.')
parser.add_argument(
    '-s', 
    '--source', 
    default="@DEFAULT_SOURCE@", 
    type=str,
    help='Define specific audio source for microphone. (pactl list source short)')

args = parser.parse_args()

def setup_modprobe(video_nr, label):
    label = shlex.quote(label)
    return os.system(f'sudo modprobe -r v4l2loopback && sudo modprobe v4l2loopback devices=1 video_nr={video_nr} card_label={label} exclusive_caps=1')
def start_stream(path, port):
    path = shlex.quote(path)
    return os.system(f'vlc {path} --sout="#rtp{{sdp=rtsp://:{port}/}}"')
def view_stream(video_nr):
    return os.system(f'ffplay /dev/video{video_nr}')
def direct_to_video(port, width, video_nr):
    return os.system(f'ffmpeg -i rtsp://localhost:{port}/ -f v4l2 -vf "hflip,format=yuv420p,scale=-1:{width}" /dev/video{video_nr}')
def clear_audio():
    interfaces = [x.split('\t')[0] for x in os.popen('pactl list short | grep ShareFlix').read().split('\n')][:-1]
    for interface in interfaces:
        print(interface)
        os.system(f'pactl unload-module {interface}')


def direct_audio(port, audio_source):
    os.system(f'pactl load-module module-null-sink sink_name="ShareFlix_combined_sink" sink_properties=device.description="ShareFlix_combined_sink_desc"')
    os.system(f'pactl load-module module-null-sink sink_name="ShareFlix_movie_sink" sink_properties=device.description="ShareFlix_movie_sink_desc"')
    if args.mic:
        os.system(f'pactl load-module module-loopback source={audio_source} sink=ShareFlix_combined_sink latency_msec=4 sink_properties=device.description="ShareFlix_mic_loopback"')
    os.system(f'pactl load-module module-loopback source=ShareFlix_movie_sink.monitor sink=ShareFlix_combined_sink latency_msec=10 sink_properties=device.description="ShareFlix_movie_loopback"')
    os.system(f'pactl load-module module-remap-source master="ShareFlix_combined_sink.monitor" source_name="ShareFlix_source" source_properties=device.description="ShareFlix"')
    os.system(f'PULSE_SINK=ShareFlix_movie_sink ffmpeg -i rtsp://:{port}/ -f pulse "ShareFlix-audio"')


if setup_modprobe(args.loopback, args.name) != 0:
    sys.exit('Failed to setup v4l2loopback')
stream = mp.Process(target=start_stream, args=(args.input, args.port)).start()
time.sleep(1)
video_loopback = mp.Process(target=direct_to_video, args=(args.port, args.width, args.loopback)).start()
clear_audio()
direct_audio = mp.Process(target=direct_audio, args=(args.port, args.source)).start()
player = mp.Process(target=view_stream, args=(args.video_nr,)).start()

#TODO: check if path exists
#TODO: if stream fails exit

#stream.join()
#player.join()
#kkkvideo_loopback.join()

#https://askubuntu.com/questions/1295430/how-do-i-mix-together-a-real-microphone-input-and-a-virtual-microphone-using-pul

# -i --input input.mov
# -s --size 1920 1080
# -n --name NameOfStream #Defaul ShareFlix
# -h --help
# -l --loopback 2
# -c --combine_audio
#https://askubuntu.com/questions/1295430/how-do-i-mix-together-a-real-microphone-input-and-a-virtual-microphone-using-pul
#https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-remap-source
#https://stackoverflow.com/questions/59150186/pulseaudio-set-check-default-source
#https://unix.stackexchange.com/questions/263263/remove-pulseaudio-device
#https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Modules/#module-combine-sink
#https://stackoverflow.com/questions/61990828/how-to-redirect-an-audio-stream-to-a-virtual-pulseaudio-microphone-with-ffmpeg