

from subprocess import Popen, PIPE


class Streamer:
    process: Popen
    input: str
    output: str
    
    def __init__(self, input: str, output: str) -> None:
        self.input = input
        self.output = output
        
    def start(self) -> None:
        print (f"{self.input} {self.output}")
        command = f"ffmpeg -re -stream_loop -1 -i {self.input} -c:v copy -rtpflags latm -f rtsp -rtsp_transport tcp {self.output}"
        
        self.process = Popen(command,shell=True, stdout=PIPE,stderr=PIPE)
        print('stream started')
    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.kill()
        print('stream stopped')