

from subprocess import Popen, DEVNULL, STDOUT


class Streamer:
    process: Popen
    input: str
    output: str
    
    def __init__(self, input: str, output: str) -> None:
        self.input = input
        self.output = output
        
    def start(self) -> None:
        print (f"{self.input} {self.output}")
        command = f"ffmpeg -re -stream_loop -1 -i {self.input} -c:v libx264 -f rtsp -rtsp_transport tcp {self.output}"
        
        self.process = Popen(command, shell=True, stdout=DEVNULL, stderr=STDOUT)
        print('stream started')

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.kill()
        print('stream stopped')