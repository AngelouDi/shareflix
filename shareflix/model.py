import os
import shlex

def setup_modprobe(video_nr):
    return os.system(f'sudo modprobe -r v4l2loopback && sudo modprobe v4l2loopback devices=1 video_nr={video_nr} card_label=ShareFlix exclusive_caps=1')


def start_stream(path, port):
    path = shlex.quote(path)
    return os.system(f'vlc {path} --sout="#rtp{{sdp=rtsp://:{port}/}}"')


def view_stream(video_nr):
    return os.system(f'ffplay /dev/video{video_nr}')


def direct_to_video(port, width, video_nr, flip):
    return os.system(f'ffmpeg -i rtsp://localhost:{port}/ -f v4l2 -vf "{"hflip," if flip else ""}format=yuv420p,scale=-1:{width}" /dev/video{video_nr}')


def clear_audio():
    interfaces = [x.split('\t')[0] for x in os.popen('pactl list short | grep ShareFlix').read().split('\n')][:-1]
    for interface in interfaces:
        os.system(f'pactl unload-module {interface}')


def direct_audio(port, audio_source, mic):
    os.system(f'pactl load-module module-null-sink sink_name="ShareFlix_combined_sink" sink_properties=device.description="ShareFlix_combined_sink_desc"')
    os.system(f'pactl load-module module-null-sink sink_name="ShareFlix_movie_sink" sink_properties=device.description="ShareFlix_movie_sink_desc"')
    if mic:
        os.system(f'pactl load-module module-loopback source={audio_source} sink=ShareFlix_combined_sink latency_msec=4 sink_properties=device.description="ShareFlix_mic_loopback"')
    os.system(f'pactl load-module module-loopback source=ShareFlix_movie_sink.monitor sink=ShareFlix_combined_sink latency_msec=5 sink_properties=device.description="ShareFlix_movie_loopback"')
    os.system(f'pactl load-module module-loopback source=ShareFlix_movie_sink.monitor sink=@DEFAULT_SINK@ latency_msec=10 sink_properties=device.description="ShareFlix_local_playback"')
    os.system(f'pactl load-module module-remap-source master="ShareFlix_combined_sink.monitor" source_name="ShareFlix_source" source_properties=device.description="ShareFlix"')
    os.system(f'PULSE_SINK=ShareFlix_movie_sink ffmpeg -i rtsp://:{port}/ -f pulse "ShareFlix-audio"')
