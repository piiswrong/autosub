from common.processor_np import *
from common.data_stream import *
import numpy as np
from common import constants
import matplotlib.pyplot as plt
import random

class feature_extractor(processor_np):
    
    def __init__(self, istream_handle, intervels, speech, noise):
        self.intervels = intervels
        self.speech = speech
        self.noise = noise
        
        self.buff_size = 100
        self.feat_length = 5
        self.input_rate = istream_handle.stream.sample_rate
        super(feature_extractor, self).__init__(istream_handle, self.buff_size, self.feat_length-1, \
                istream_handle.stream.data_format['shape'], istream_handle.stream.data_format['dtype'])
        
        self.state = 0
        self.p_intervel = 0
        
    def work(self, buff, size, pos):
        
#        plt.imshow(np.log(abs(buff)**2+1))
#        plt.show()
        for i in xrange(size - self.feat_length + 1):
            if self.p_intervel == len(self.intervels):
                self.noise.append(buff[i:i+self.feat_length, :].copy().reshape(-1))
            else:
                if self.state == 0:
                    if (pos + i + self.feat_length)/self.input_rate >= self.intervels[self.p_intervel][0]:
                        self.state = 1
                    else:
                        self.noise.append(buff[i:i+self.feat_length, :].copy().reshape(-1))
#                        print 'noise:', (pos+i)/self.input_rate                    
                elif self.state == 1:
                    if (pos + i + 1)/self.input_rate >= self.intervels[self.p_intervel][0]:
                        self.state = 2
                elif self.state == 2:
                    if (pos + i + self.feat_length)/self.input_rate >= self.intervels[self.p_intervel][1]:
                        self.state = 3
                    elif self.intervels[self.p_intervel][2]:
                        self.speech.append(buff[i:i+self.feat_length, :].copy().reshape(-1))
#                        if random.randint(0,0) == 0:
#                            plt.subplot(121)
#                            plt.imshow(np.log(abs(buff[i-self.half_length:i+self.half_length+1, :])**2+1))
#                            plt.subplot(122)
#                            plt.imshow(np.log(abs(buff)**2+1))
#                            plt.show()
#                        print 'speech:', (pos + i)/self.input_rate
                    
                elif self.state == 3:
                    if (pos + i + 1)/self.input_rate >= self.intervels[self.p_intervel][1]:
                        self.state = 0
                        self.p_intervel = self.p_intervel + 1