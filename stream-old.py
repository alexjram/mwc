import ffmpeg
import os

video = 'files/UAV.mp4'
rtsp_url = 'rtsp://localhost:8554/uav'

def stream():
    #ffmpeg
    comm = ffmpeg.input(
        video, format='mp4', stream_loop=-1).output(
            rtsp_url, c='copy', preset='fast', f='rtsp', rtsp_transport='tcp', bitrate='2M').global_args('-re').run_async()
    print (comm)

    # string = 'ffmpeg -re -stream_loop -1 -i ' + video + ' -c:v copy -rtpflags latm -f rtsp -rtsp_transport tcp ' + rtsp_url

    # os.popen(string)

if __name__ == '__main__':
    stream()