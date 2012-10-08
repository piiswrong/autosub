import core.ffmpeg_decoder as fd
import core.sub_generator as sg
from core.naive_vad2 import *
import sys

if __name__ == '__main__':
    try:
        i = 1
        lang_from = None
        lang_to = None
        source = None
        target = None
        while i < len(sys.argv):
            if sys.argv[i].startswith('-'):
                
                if sys.argv[i] == '-r':
                    lang_from = sys.argv[i+1]
                    i = i + 2
                elif sys.argv[i] == '-t':
                    lang_to = sys.argv[i+1]
                    i = i + 2
                elif sys.argv[i] == '-o':
                    target = sys.argv[i+1]
                    i = i + 2
                else:
                    raise ValueError()
                
            else:
                print sys.argv[i]
                source = sys.argv[i]
                i = i + 1
                
        if not source:
            raise ValueError()
        if not target:
            target = source[:source.rfind('.')] + '.srt'
    except:
        print 'Usage: autosub [options...] <input video>'
        print 'Example: autosub -r ja -t zh-cn demo.mp4'
        print 'Options:'
        print ' -r <language code> enable speech recognition and set source language to <language code>'
        print ' -t <language code> enable translation and set target language to <language code>'
        print ' -o <output>.srt specify output subtitle file name (default: same as input)'
        print 'Language codes:'
        print ' Chinese     zh-cn'
        print ' English     en'
        print ' Japanese    ja'
        exit()
    dec = fd.ffmpeg_decoder(source)
    vad = naive_vad(dec.ostream.get_handle())
    sub = sg.sub_generator(vad.ostream.get_handle(), source, target, lang_from = lang_from, lang_to = lang_to)
    dec.start()
    vad.start()
    sub.start()
    
    sub.join()

