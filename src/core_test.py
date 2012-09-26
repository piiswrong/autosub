import core.audio_decoder as ad
import core.spectrum as spec
from core.naive_vad import *

__builtins__.AUDIO_SAMPLE_RATE = 8000

dec = ad.audio_decoder('../data/demo.wav')
s = spec.spectrum(dec.ostream.get_handle())
score = naive_vad_score(s.ostream.get_handle())
decision = naive_vad_decision(score.ostream.get_handle())
dec.start()
s.start()
score.start()
decision.start()

decision.join()