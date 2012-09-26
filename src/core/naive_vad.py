from common.processor_np import *
from common.data_stream import *
from core.spectrum import *
import numpy as np
import matplotlib.pyplot as plt

class naive_vad_score(processor_np):
    def __init__(self, istream_handle):
        self.input_format = istream_handle.stream.data_format
        self.input_size = self.input_format['shape'][0]
        super(naive_vad_score, self).__init__(istream_handle, 100, 0, self.input_format['shape'], self.input_format['dtype'])
        
        self.ostream = data_stream(istream_handle.stream.sample_rate, data_format = {'dtype':self.input_format['dtype']})
        
        
    def work(self, buff, size, pos):
        print size
        data = np.concatenate((np.asarray([ self.process_frame(buff[i]) for i in xrange(size) ]).reshape((size,1)), buff[:size]), axis = 1)
        self.ostream.write(data)
        
    def process_frame(self, frame):
        num_bands = 32
        band_len = self.input_size/num_bands
        Eb = frame.reshape((num_bands, band_len)).sum(axis = 1)
        Pb = Eb/Eb.sum()
        Po = Pb.min()/Pb
        W = np.asarray([ Po[max(0,i-1):min(num_bands, i+1)].var() for i in xrange(num_bands) ])
        nminbe = -np.log2(Eb.min()/Eb.sum())
        num_useful = int(min(30,max(4, 36.5-nminbe*1.3)))
        #print nminbe, num_useful
        return W[:num_useful].dot(Pb[:num_useful]*np.log2(1/Pb[:num_useful]))
        
class naive_vad_decision(processor_np):
    def __init__(self, istream_handle):
        super(naive_vad_decision, self).__init__(istream_handle, 100, 0, (129,), istream_handle.stream.data_format['dtype'])

    def work(self, buff, size, pos):
        return        
        plt.subplot(211)
        plt.imshow(buff.T)
        plt.subplot(212)
        plt.plot(xrange(size), buff[:,0])
        plt.show()
        
        
        
        
        
        
        
        
        
        