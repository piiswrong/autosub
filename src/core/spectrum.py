from common.processor_np import *
from common.data_stream import *
import numpy as np
from common import constants

class spectrum(processor_np):
    def __init__(self, istream_handle, squared = True, window_size = 256):
        self.window_size = window_size
        self.shift_dist = window_size/2
        self.batch_size = 100
        self.squared = squared
        buff_size = self.window_size + (self.batch_size - 1) * self.shift_dist
        super(spectrum, self).__init__(istream_handle, buff_size, self.window_size - self.shift_dist, (), istream_handle.stream.data_format['dtype'])
        
        if squared:        
            self.ostream = data_stream(istream_handle.stream.sample_rate/float(self.shift_dist), data_format = {'shape':(self.window_size/2,), 'dtype':np.double})
        else:
            self.ostream = data_stream(istream_handle.stream.sample_rate/float(self.shift_dist), data_format = {'shape':(self.window_size/2,), 'dtype':np.complex128})
        self.w = np.hamming(self.window_size)
        
    def work(self, buff, size, pos):
        if self.squared:
            data = np.asarray([ abs(np.fft.fft(buff[i:i+self.window_size]*self.w)[:self.window_size/2])**2 \
                                for i in xrange(0, size - self.window_size + 1, self.shift_dist) ])
        else:
            data = np.asarray([ np.fft.fft(buff[i:i+self.window_size]*self.w)[:self.window_size/2] \
                                for i in xrange(0, size - self.window_size + 1, self.shift_dist) ])
        self.ostream.write(data)
        #plt.imshow(data.T)
        #plt.show()