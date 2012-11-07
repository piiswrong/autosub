from common.processor import *
from common.data_stream import *
import numpy as np
import subprocess
from common import constants

class ffmpeg_decoder(processor):
    
    def __init__(self, file_name, output_rate = constants.AUDIO_SAMPLE_RATE):
        super(ffmpeg_decoder, self).__init__()
        self.file_name = file_name
        self.ostream = data_stream(output_rate, data_format = {'dtype':np.int16})
        self.odtype = np.int16
        self.output_rate = output_rate
        
    def run(self):
        ffmpeg = subprocess.Popen([constants.FFMPEG_PATH, '-v', '0', '-i', self.file_name, '-vn', '-ar', str(self.output_rate), '-ac', '1', '-f', 's16le', '-'], stdout = subprocess.PIPE)
        while True:
            s = ffmpeg.stdout.read(512)
            if not s:
                break
            self.ostream.write(np.fromstring(s, dtype = self.odtype))
        self.ostream.finish_writing()
        if constants.DEBUG:
            print 'dec finish'