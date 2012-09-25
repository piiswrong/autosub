import core.audio_decoder as ad


a = ad.audio_decoder('../data/demo.wav')
h = a.ostream.get_handle()
a.start()