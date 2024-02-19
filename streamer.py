

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
        command = f"ffmpeg -v quiet -re -stream_loop -1 -i {self.input} -c copy -f rtsp -rtsp_transport tcp {self.output}"
        
        self.process = Popen(command, shell=True)
        print('stream started')

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.kill()
        print('stream stopped')