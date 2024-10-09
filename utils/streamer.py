from typing import Union
from subprocess import Popen
import ffmpeg


class Streamer:
    process: Union[Popen, None]
    input: str
    output: str
    
    def __init__(self, input: str, output: str) -> None:
        self.input = input
        self.output = output
        self.process = None
        
    def start(self) -> None:
        if self.has_started():
            return
        self.process = (
            ffmpeg.input(self.input, **{'readrate': '1', 'stream_loop': '-1'})
                .output(self.output, **{'c:v': 'copy', 'f': 'rtsp', 'rtsp_transport': 'tcp'})
                .run_async(pipe_stdout=True, pipe_stderr=True)
        )
        print('stream started')
        
    def has_started(self) -> bool:
        
        return self.process is not None and self.process.poll() is None
    def stop(self) -> None:

        if self.process is not None and self.process.poll() is None:
            self.process.kill()
        print('stream stopped')