from common.processor import *
from common.data_stream import *
from pymedia import muxer as muxer
from pymedia.audio import acodec

class audio_decoder(processor):
    """
    invode pymedia to decode an audio track
    """
    def __init__(self, file_name):
        self.file_name = file_name
        ext = file_name.strip().split('.')[-1].lower()
        dm = muxer.Demuxer(ext)
        fin = open(file_name, 'rb')
        s = fin.read(300000)
        r = dm.parse(s)
        
        ac = None
        for aindex in xrange( len( dm.streams )):
          if dm.streams[ aindex ] and dm.streams[ aindex ][ 'type' ]== muxer.CODEC_TYPE_AUDIO:
            ac = acodec.Decoder( dm.streams[ aindex ] )
            break
        if not ac:
            raise "no audio track found in given media file!"
        
        print ac
        self.ac = ac