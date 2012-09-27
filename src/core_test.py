import core.audio_decoder as ad
import core.spectrum as spec
from core.naive_vad2 import *

__builtins__.AUDIO_SAMPLE_RATE = 44100

dec = ad.audio_decoder('../data/demo.wav')
vad = naive_vad(dec.ostream.get_handle())

dec.start()
vad.start()

vad.join()

