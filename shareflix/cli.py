from .model import *
import argparse
import sys
import subprocess
import time
import multiprocessing as mp
from shutil import which

banner = """\033[91m.▄▄ ·  ▄ .▄ ▄▄▄· ▄▄▄  ▄▄▄ .·▄▄▄▄▄▌  ▪  ▐▄• ▄ 
▐█ ▀. ██▪▐█▐█ ▀█ ▀▄ █·▀▄.▀·▐▄▄·██•  ██  █▌█▌▪
▄▀▀▀█▄██▀▐█▄█▀▀█ ▐▀▀▄ ▐▀▀▪▄██▪ ██▪  ▐█· ·██· 
▐█▄▪▐███▌▐▀▐█ ▪▐▌▐█•█▌▐█▄▄▌██▌.▐█▌▐▌▐█▌▪▐█·█▌
 ▀▀▀▀ ▀▀▀ · ▀  ▀ .▀  ▀ ▀▀▀ ▀▀▀ .▀▀▀ ▀▀▀•▀▀ ▀▀\033[00m"""

def main():
    print(banner)
    parser = argparse.ArgumentParser(
        prog='ShareFlix',
        description=f'Allows anyone to stream video with sound over VOIP',
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
        help='Define specific audio source for microphone. (pactl list sources short)')

    args = parser.parse_args()

    if setup_modprobe(args.loopback) != 0:
        sys.exit('Failed to setup v4l2loopback')
    stream = mp.Process(target=start_stream, args=(args.input, args.port)).start()
    time.sleep(1)
    video_loopback = mp.Process(target=direct_to_video, args=(args.port, args.width, args.loopback, args.flip)).start()
    time.sleep(3)
    player = mp.Process(target=view_stream, args=(args.loopback,)).start()
    clear = mp.Process(target=clear_audio).start()
    direct = mp.Process(target=direct_audio, args=(args.port, args.source, args.mic)).start()