from common.processor_np import *
from common.data_stream import *
import numpy as np
from scipy.cluster.vq import kmeans



class naive_vad(processor_np):
    def __init__(self, istream_handle):
        self.Fs = istream_handle.stream.sample_rate
        self.segment_len = 2000
        self.segment_reserve = 40
        self.low_freq = 20
        self.high_freq = 2
        self.frame_len = 10
        self.frame_shift = 10
        self.min_segment_len = 75
        self.breath_len = 20
        self.max_word_pause = 400
        self.max_clust_try = 100
        self.min_syllable_len = 100
        
        self.b = 3.5
        self.lambda_P = 1.0
        self.kmeans_error_threshold = 0.3
        self.preset_SNR = 10
        self.iframe_per_segment = (self.segment_len - self.frame_len)/self.frame_shift + 1
        self.isample_per_frame = self.frame_len * self.Fs / 1000
        
        self.MCR_low = 0.03
        self.MCR_high = 0.4
        self.bcheck_prosody = False
        
        self.last_fragment = []
        self.bcircle_done = False
        self.istate = 1
        self.A = [ -2147483648 for i in xrange(4+1)]
        self.peak_E = -1.0
        
        self.segment_E = np.zeros(self.iframe_per_segment, dtype = np.float)
        self.bin_speech = False
        self.icur_frame = 0
        
        self.start_end = []
        
        super(naive_vad, self).__init__(istream_handle, self.isample_per_frame*self.iframe_per_segment, 0, (), istream_handle.stream.data_format['dtype'])
        self.ostream = data_stream(0)        
        
        #self.count = 0
        #self.fout = open('../data/social.srt', 'w')
        
    def work(self, buff, size, pos):
        iframe_loaded = self.load_frame_energy(buff, size)
        m1, m2, clust_dis = self.kmeans_clustering(iframe_loaded)
        k = self.get_k4(m1, m2, clust_dis)
        self.apply_lamel_rules(iframe_loaded, self.icur_frame, k)
        self.icur_frame = self.icur_frame + iframe_loaded
        
        while len(self.start_end) > 1:
            #print self.start_end[0], self.start_end[1]
            seg = ((self.start_end[0]*self.frame_shift + self.frame_len/2)/1000.0, (self.start_end[1]*self.frame_shift + self.frame_len/2)/1000.0)
            #print 'vad', seg            
            self.ostream.write([seg])
            self.start_end = self.start_end[2:]

#            seg = (int(seg[0]*100), int(seg[1]*100))
#            self.count = self.count + 1
#            self.fout.write("%d\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n%d\n\n" % (self.count, seg[0]/360000, (seg[0]%360000)/6000, (seg[0]%6000)/100, (seg[0]%100)*10, seg[1]/360000, (seg[1]%360000)/6000, (seg[1]%6000)/100, (seg[1]%100)*10, self.count))
#    
    def apply_lamel_rules(self, iframe_loaded, pos, k):
        istate = self.istate
        peak_E = self.peak_E
        A = self.A
        bcircle_done = self.bcircle_done
        fragment = self.last_fragment
        
        for i in xrange(iframe_loaded):
            E = self.segment_E[i]
            
            if istate == 1:
                if bcircle_done:
                    assert A[1] >= -self.iframe_per_segment and A[2] >= A[1] and A[3] >= A[2] and A[4] >= A[3] and peak_E > 0
                    if A[2]-A[1] > self.breath_len:
                        start = A[2]
                    else:
                        start = A[1]
                    if A[4]-A[3] > self.breath_len:
                        end = A[3]
                    else:
                        end = A[4]
                    if end - start > (self.min_segment_len / self.frame_len) and peak_E > k[4]:
                        fragment.append(start)
                        fragment.append(end)
                    A = [ -2147483648 for j in xrange(4+1)]
                    peak_E = -1
                    bcircle_done = False
                    
                if E > k[1]:
                    istate = 2
                    A[1] = i
                    peak_E = E
                                
            elif istate == 2:
                peak_E = max(peak_E, E)
                if E < k[1]:
                    istate = 1
                    A[1] = -2147483648
                    peak_E = -1
                elif E > k[2]:
                    istate = 3
                    A[2] = i
                    
            elif istate == 3:
                peak_E = max(peak_E, E)
                if E < k[2]:
                    istate = 4
                    A[3] = i
                    
            elif istate == 4:
                if E > k[2]:
                    istate = 3
                    A[3] = -2147483648
                elif E < k[3]:
                    istate = 1
                    A[4] = i
                    bcircle_done = True
        
        
        bmerge = True
        while bmerge:
            bmerge = False
            for i in xrange(1, len(fragment)-1, 2):
                if fragment[i+1]-fragment[i] < self.max_word_pause / self.frame_shift:
                    fragment = fragment[:i] + fragment[i+2:]
                    bmerge = True
                    break
                
        if not self.bin_speech:
            if len(fragment) != 0:
                while len(fragment) > 2:
                    if not self.bcheck_prosody:
                        self.start_end.append(pos + fragment[0])
                        self.start_end.append(pos + fragment[1])
                    fragment = fragment[2:]
                
                if (istate == 1 and iframe_loaded - fragment[1] > self.max_word_pause / self.frame_shift) or (istate != 1 and A[1] - fragment[1] > self.max_word_pause / self.frame_shift):
                    if not self.bcheck_prosody:
                        self.start_end.append(pos + fragment[0])
                        self.start_end.append(pos + fragment[1])
                    fragment = []
                else:
                    self.start_end.append(pos + fragment[0])
                    self.bin_speech = True
        else:
            while len(fragment) > 2:
                if not self.bcheck_prosody:
                    self.start_end.append(pos + fragment[1])
                else:
                    self.start_end.pop()
                self.start_end.append(pos + fragment[2])
                fragment = fragment[2:]
            
            assert len(fragment) > 0
            
            if (istate == 1 and iframe_loaded - fragment[1] > self.max_word_pause / self.frame_shift) or (istate != 1 and A[1] - fragment[1] > self.max_word_pause / self.frame_shift):
                if not self.bcheck_prosody:
                    self.start_end.append(pos + fragment[1])
                else:
                    self.start_end.pop()
                fragment = []
                self.bin_speech = False
                
        
        self.istate = istate
        self.peak_E = peak_E
        self.A = [ a - iframe_loaded for a in A ]
        self.bcircle_done = bcircle_done
        if len(fragment) == 0:
            self.last_fragment = []
        else:
            self.last_fragment = [ f - iframe_loaded for f in fragment[-2:] ]
            
    
    def get_k4(self, m1, m2, clust_dis):
        if clust_dis[0] < clust_dis[1] + self.kmeans_error_threshold and m2[1] - m2[0] < self.preset_SNR / 2:
            k = (0, m1 + 5, m1 + 8, m1 + 6, m1 + 10)
        elif clust_dis[0] > clust_dis[1] + self.kmeans_error_threshold and m2[1] - m2[0] > self.preset_SNR:
            k = (0, m2[0] + (m2[1]-m2[0])*0.1,m2[0] + (m2[1]-m2[0])*0.3,m2[0] + (m2[1]-m2[0])*0.2,m2[0] + (m2[1]-m2[0])*0.6)
        elif m1 > 0.6 * (m2[1]-m2[0]) + m2[0]:
            k = (0, m2[0] + self.preset_SNR/2, m2[0] + self.preset_SNR, m2[0] + self.preset_SNR/2, m2[0] + self.preset_SNR*2)
        else:
            k = (0, m1 + self.preset_SNR/2, m1 + self.preset_SNR, m1 + self.preset_SNR/2, m1 + self.preset_SNR*2)
        
        return k
        
    def load_frame_energy(self, buff, size):
        mean = buff.mean()       
        iframe_loaded = 0
        icur_sample = 0
        while icur_sample + self.isample_per_frame <= size and iframe_loaded < self.iframe_per_segment:
            E = ((buff[icur_sample:icur_sample+self.isample_per_frame] - mean)**2).sum()
            self.segment_E[iframe_loaded] = 10*np.log10(E+500000.0)
            icur_sample = icur_sample + self.frame_shift * self.Fs / 1000
            iframe_loaded = iframe_loaded + 1
        self.resid_size = size - icur_sample
        return iframe_loaded
            
    
    def kmeans_clustering(self, iframe_loaded):
        m1 = self.segment_E.mean()
        gstd = self.segment_E.std()
        clust_dis1 = abs(self.segment_E - m1).sum()/(iframe_loaded*gstd)
        
        l = self.segment_E[:iframe_loaded].tolist()
        l.sort()
        
        m2_old = np.asarray([[sum(l[:iframe_loaded/2])/(iframe_loaded/2)], [sum(l[iframe_loaded/2:])/(iframe_loaded - iframe_loaded/2)]])
        
        while True:
            dist = abs(self.segment_E - m2_old)
            c0 = 0
            c1 = 0
            m2_0 = 0.0
            m2_1 = 0.0
            for i in xrange(iframe_loaded):
                if dist[0, i] < dist[1, i]:
                    c0 = c0 + 1
                    m2_0 = m2_0 + self.segment_E[i]
                else:
                    c1 = c1 + 1
                    m2_1 = m2_1 + self.segment_E[i]
            clust_dis2 = dist.min(axis = 0).sum()
            m2 = np.asarray([[m2_0/c0], [m2_1/c1]])
            if abs(m2[0, 0] - m2_old[0, 0]) < 1e-5 and abs(m2[1, 0] - m2_old[1, 0]) < 1e-5:
                break
            m2_old = m2
        return m1, (min(m2[0, 0], m2[1, 0]), max(m2[0, 0], m2[1, 0])), (clust_dis1, clust_dis2/(iframe_loaded*gstd))
    
        
        
        
        