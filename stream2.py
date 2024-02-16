import subprocess

videos = ['files/uav.mp4', 'files/ugv.mp4']
rtsp_urls = ['rtsp://172.17.0.1:8554/uav', 'rtsp://172.17.0.1:8554/ugv'] 

def stream():

    for video, rtsp_url in zip(videos, rtsp_urls):

        command = 'ffmpeg -re -stream_loop -1 -i ' + video + ' -c:v copy -rtpflags latm -f rtsp -rtsp_transport tcp ' + rtsp_url
        res = subprocess.Popen(command, shell=True)
        result = subprocess.run(command, shell=True)

        # Check the result
        if result.returncode == 0:
            print("Command executed successfully.")
        else:
            print(f"Command failed with return code {result.returncode}.")


if __name__ == '__main__':
    stream()