import os
import sys
from core.ffmpeg_decoder import ffmpeg_decoder
from core.spectrum import spectrum
from core.feature_extractor import feature_extractor
import matplotlib.pyplot as plt
import numpy as np
import random

SAMPLE_RATE = 8000
N = 1
sub_names = [ '../data/raw/sub (%d).ass'%i for i in xrange(1, N+1) ]
mov_names = [ '../data/raw/mov (%d).mkv'%i for i in xrange(1, N+1)]

def parse_time(stime):
    stime = stime.split('.')
    res = float(stime[1])/100
    stime = stime[0].split(':')
    return res + float(stime[0])*3600 + float(stime[1])*60 + float(stime[2])
    
speech = []
noise = []

for sub_name, mov_name in zip(sub_names, mov_names):
    fsub = open(sub_name)
    intervels = []
    while True:
        if fsub.readline().strip() == '[Events]':
            break
    for line in fsub:
        if line.startswith('Dialogue:'):
            line = line.strip().split(',')
            
            if line[3] != 'Default' or line[9].startswith('{\\an8'):
                intervels.append( (parse_time(line[1]), parse_time(line[2]), False) )
            else:
                intervels.append( (parse_time(line[1]), parse_time(line[2]), True) )

    intervels.sort(cmp=lambda x,y: cmp(x[0], y[0]))
    
    i = 0
    while i < len(intervels)-1:
        if intervels[i][1] > intervels[i+1][0]:
            intervels[i] = (intervels[i][0], intervels[i+1][1], intervels[i][2] and intervels[i+1][2])
            del intervels[i+1]
        else:
            i = i + 1
    
    dec = ffmpeg_decoder(mov_name, SAMPLE_RATE)
    spec = spectrum(dec.ostream.get_handle(), squared = False)
    feat = feature_extractor(spec.ostream.get_handle(), intervels, speech, noise)
    dec.start()
    spec.start()
    feat.start()
    
    feat.join()
    
random.shuffle(speech)
random.shuffle(noise)
for f in speech:
    plt.imshow(np.log(abs(f)**2).reshape((5, 128)))
    plt.show()
    