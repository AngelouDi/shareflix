# ShareFlix
`ShareFlix` is a python cli module which can be used to stream videos using VOiP applications.
It uses `v4l2loopback`, `pulseaudio` and `ffmpeg` to create virtual video and audio devices which can be used by any VOiP program.
## Requirements
- v4l2loopback
- pulse compatible drivers (pactl)
- ffmpeg
- python 3

Install python requirements with: `pip install -m requirements.txt`

## Usage
```
.▄▄ ·  ▄ .▄ ▄▄▄· ▄▄▄  ▄▄▄ .·▄▄▄▄▄▌  ▪  ▐▄• ▄ 
▐█ ▀. ██▪▐█▐█ ▀█ ▀▄ █·▀▄.▀·▐▄▄·██•  ██  █▌█▌▪
▄▀▀▀█▄██▀▐█▄█▀▀█ ▐▀▀▄ ▐▀▀▪▄██▪ ██▪  ▐█· ·██· 
▐█▄▪▐███▌▐▀▐█ ▪▐▌▐█•█▌▐█▄▄▌██▌.▐█▌▐▌▐█▌▪▐█·█▌
 ▀▀▀▀ ▀▀▀ · ▀  ▀ .▀  ▀ ▀▀▀ ▀▀▀ .▀▀▀ ▀▀▀•▀▀ ▀▀
usage: ShareFlix [-h] -i INPUT [-p PORT] [-w WIDTH] [-l LOOPBACK] [--flip] [--mic] [-s SOURCE]

Allows anyone to stream video with sound over VOIP

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path to video file
  -p PORT, --port PORT  Port of stream
  -w WIDTH, --width WIDTH
                        Width of video output. (Skype needs less than 720)
  -l LOOPBACK, --loopback LOOPBACK
                        Add more audio sources to stream (such as mic).
  --flip                Mirror the screen horizontally.
  --mic                 Pass sound from microphone.
  -s SOURCE, --source SOURCE
                        Define specific audio source for microphone. (pactl list source short)

Stream only legal linux.iso's!
```	

The simplest way of running ShareFlix is:
`python -m shareflix -i movie.mp4`

If you want to flip the screen you can use the `--flip` flag.

You can pass your microphone audio to the stream by using `--mic` and optionally select a different source as given by `pactl list source short` by passing it to `-s` argument.

If `/dev/video1` is already occupied you can select a different number using `-l` flag.

## Limitations
- The program has been tested only on arch-linux running pipewire.
- sudo is required to create the virtual video devices.
- The audio is delayed by a few milliseconds, pull requests solving this are more than welcome!
- If you hear artifacts, rerun it.
