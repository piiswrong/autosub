from common.processor import *
from common.data_stream import *
from pymedia import muxer as muxer
from pymedia.audio import acodec
from pymedia.audio import sound
import numpy as np

class audio_decoder(processor):
    """
    invode pymedia to decode an audio track
    """
    def __init__(self, file_name):
        super(audio_decoder, self).__init__()
        self.file_name = file_name
        ext = file_name.strip().split('.')[-1].lower()
        dm = muxer.Demuxer(ext)
        fin = open(file_name, 'rb')
        if not fin:
            raise "cannot find file %s" % file_name
        s = fin.read(300000)
        r = dm.parse(s)
        
        self.decoder = None
        for aindex in xrange( len( dm.streams )):
          if dm.streams[ aindex ] and dm.streams[ aindex ][ 'type' ]== muxer.CODEC_TYPE_AUDIO:
            self.decoder = acodec.Decoder( dm.streams[ aindex ] )
            self.aindex = aindex
            break
        if not self.decoder:
            raise "no audio track found in given media file!"
        
        self.resampler = sound.Resampler( (dm.streams[ aindex ][ 'sample_rate' ], dm.streams[ aindex ][ 'channels' ]), 
                                          (AUDIO_SAMPLE_RATE , 1) )
        self.ostream = data_stream(AUDIO_SAMPLE_RATE)
        self.odtype = np.int16
        self.demuxer = dm
        self.frames = r
        self.fin = fin
        
    def run(self):
        frames = self.frames
        while True:
            for frame in frames:
                if frame[0] == self.aindex:
                    r = self.decoder.decode(frame[1])
                    if r and r.data:
                        data = self.resampler.resample(r.data)
                        data = np.fromstring(data, dtype = self.odtype)
                        self.ostream.write(data)
                        
            s = self.fin.read(512)
            if len(s) == 0:
                break
            frames = self.demuxer.parse(s)
        