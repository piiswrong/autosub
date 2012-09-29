import core.ffmpeg_decoder as fd
import core.sub_generator as sg
from core.naive_vad2 import *
import sys

if __name__ == '__main__':
    try:
        source = sys.argv[1]
        target = sys.argv[2]
    except:
        print 'usage:   autosub source.avi target.srt'
        exit()
    dec = fd.ffmpeg_decoder(source)
    vad = naive_vad(dec.ostream.get_handle())
    sub = sg.sub_generator(vad.ostream.get_handle(), source, target)
    dec.start()
    vad.start()
    sub.start()
    
    sub.join()

