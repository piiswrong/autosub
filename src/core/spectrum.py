from common.processor_np import *
from common.data_stream import *
import numpy as np
import scipy
import matplotlib.pyplot as plt
from common import constants
class spectrum(processor_np):
    def __init__(self, istream_handle):
        self.window_size = 256
        self.shift_dist = 128
        self.batch_size = 100
        buff_size = self.window_size + (self.batch_size - 1) * self.shift_dist
        super(spectrum, self).__init__(istream_handle, buff_size, self.window_size - self.shift_dist, (), istream_handle.stream.data_format['dtype'])
        
        self.ostream = data_stream(constants.AUDIO_SAMPLE_RATE/float(self.shift_dist), data_format = {'shape':(self.window_size/2,), 'dtype':np.double})
        self.w = scipy.hamming(self.window_size)
        
    def work(self, buff, size, pos):
        data = np.asarray([ abs(scipy.fft(buff[i:i+self.window_size]*self.w)[:self.window_size/2])**2 \
                            for i in xrange(0, size - self.window_size + 1, self.shift_dist) ])
        self.ostream.write(data)
        #plt.imshow(data.T)
        #plt.show()