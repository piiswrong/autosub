import core.audio_decoder as ad
import core.ffmpeg_decoder as fd
import core.sub_generator as sg
import core.spectrum as spec
from core.naive_vad2 import *


dec = fd.ffmpeg_decoder('../data/demo.mp4')
vad = naive_vad(dec.ostream.get_handle())
sub = sg.sub_generator(vad.ostream.get_handle(), '../data/demo.mp4', '../data/demo.srt')
dec.start()
vad.start()
sub.start()

sub.join()

