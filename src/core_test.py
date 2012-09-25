import core.audio_decoder as ad
import core.spectrum as spec


__builtins__.AUDIO_SAMPLE_RATE = 8000

dec = ad.audio_decoder('../data/demo.wav')
s = spec.spectrum(dec.ostream.get_handle())

dec.start()
s.start()

s.join()