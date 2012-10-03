from common.processor_np import *
from common.data_stream import *
from core.spectrum import *
import numpy as np
import collections

class naive_vad_score(processor_np):
    def __init__(self, istream_handle):
        self.input_format = istream_handle.stream.data_format
        self.input_size = self.input_format['shape'][0]
        super(naive_vad_score, self).__init__(istream_handle, 100, 0, self.input_format['shape'], self.input_format['dtype'])
        
        self.ostream = data_stream(istream_handle.stream.sample_rate, data_format = {'dtype':self.input_format['dtype']})
        
        
    def work(self, buff, size, pos):
        data = np.concatenate((np.asarray([ self.process_frame(buff[i]) for i in xrange(size) ]).reshape((size,1)), buff[:size]), axis = 1)
        #data = np.asarray([ self.process_frame(buff[i]) for i in xrange(size) ])        
        self.ostream.write(data)
        
    def process_frame(self, frame):
        num_bands = 32
        band_len = self.input_size/num_bands
        Eb = frame.reshape((num_bands, band_len)).sum(axis = 1) + 0.0000001
        Pb = Eb/Eb.sum()
        Po = Pb.min()/Pb
        W = np.asarray([ Po[max(0,i-1):min(num_bands, i+1)].var() for i in xrange(num_bands) ])
        nminbe = -np.log2(Eb.min()/Eb.sum())
        num_useful = int(min(30,max(4, 36.5-nminbe*1.3)))
        #print nminbe, num_useful
        l = [ (Eb[i], i) for i in xrange(num_bands) ]
        l.sort(cmp = lambda x,y: cmp(x[0], y[0]), reverse = True)
        res = 0.0
        for i in xrange(num_bands-num_useful, num_bands):
            ind = l[i][1]
            res = res + W[ind]*Pb[ind]*np.log2(1.0/Pb[ind])
        return res
        
class naive_vad_decision(processor_np):
    def __init__(self, istream_handle):
        super(naive_vad_decision, self).__init__(istream_handle, 500, 0, (129,), istream_handle.stream.data_format['dtype'])
        self.ostream = data_stream(float('inf'))        
        self.Ts = None
        self.init_len = min(10, self.buff_size)
        self.mu = 0
        self.sigma = 0
        self.H = None
        self.alpha = 0.5
        self.beta = 0.99
        self.speech = False
        self.max_sep = int(0.2*istream_handle.stream.sample_rate)
        self.sep = 0
        self.min_seg = int(0.08*istream_handle.stream.sample_rate)
        self.start_point = None
        
        
        self.fout = open('demo2.srt','w')
        self.count = 0
        
    def work(self, buff, size, pos):
        """
        plt.subplot(211)
        plt.imshow(buff.T)
        plt.gray()
        plt.subplot(212)
        plt.plot(xrange(size), buff[:size,0])
        plt.show()
        return
        """
        if self.Ts is None:
            init = buff[:self.init_len]
            self.mu = init.mean()
            self.sigma = init.var()
            self.H = np.asarray(init)**2
            self.H_ind = 0
            self.Ts = self.mu + self.alpha*self.sigma

        for i in xrange(size):
            print pos + i, buff[i], self.Ts, self.sigma, self.mu
            if buff[i] > self.Ts:
                if not self.speech:
                    self.start_point = pos + i
                self.sep = 0
                self.speech = True
                
            else:
                if self.speech:
                    self.sep = self.sep + 1
                    if self.sep > self.max_sep:
                        self.speech = False
                        seg = (self.start_point, pos + i - self.sep)
                        if seg[1] - seg[0] > self.min_seg:
                            seg = (self.istream_handle.get_time(seg[0]), self.istream_handle.get_time(seg[1]))
                            self.ostream.write(seg)
                            
                            
                            print seg
                            self.count = self.count + 1
                            seg = (int(seg[0]*100), int(seg[1]*100))
                            self.fout.write("%d\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n%d\n\n" % (self.count, seg[0]/360000, (seg[0]%360000)/6000, (seg[0]%6000)/100, (seg[0]%100)*10, seg[1]/360000, (seg[1]%360000)/6000, (seg[1]%6000)/100, (seg[1]%100)*10, self.count))
                            
                            
                self.mu = self.beta*self.mu + (1-self.beta)*buff[i]
                H = self.beta*self.H.mean() + (1-self.beta)*(buff[i]**2)
                self.sigma = np.sqrt(abs(H**2-self.mu**2))
                self.H[self.H_ind] = buff[i]**2
                self.H_ind = (self.H_ind + 1)%self.init_len
                self.Ts = self.mu + self.alpha*self.sigma
        
        
        
        
        
        
        
        
        