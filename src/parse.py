import os
import sys
from core.ffmpeg_decoder import ffmpeg_decoder
from core.spectrum import spectrum
from core.feature_extractor import feature_extractor
import matplotlib.pyplot as plt
import numpy
import random
import cPickle
import theano
import theano.tensor as T
import time
import sklearn
from sklearn import linear_model

theano.config.floatX = 'float64'
my_dtype = numpy.float64

SAMPLE_RATE = 8000

def parse_time(stime):
    stime = stime.split('.')
    res = float(stime[1])/100
    stime = stime[0].split(':')
    return res + float(stime[0])*3600 + float(stime[1])*60 + float(stime[2])

class SDA(object):
    def __init__(self, dimensions):
        self.dimensions = [ i for i in dimensions ]
        self.n_layers = len(dimensions)-1
        self.W = []
        self.b = []
        self.b_prime = []
        numpy_rng = numpy.random.RandomState(123)
        self.theano_rng = T.shared_randomstreams.RandomStreams(numpy_rng.randint(2**30))
        self.w_value = []
        for i in xrange(self.n_layers):
            initial_W = numpy.asarray( numpy_rng.uniform(
                                        low  = -4*numpy.sqrt(6./(dimensions[i]+dimensions[i+1])),
                                        high =  4*numpy.sqrt(6./(dimensions[i]+dimensions[i+1])),
                                        size = (dimensions[i], dimensions[i+1])), dtype = theano.config.floatX)
            self.w_value.append(initial_W)
            self.W.append( theano.shared(value = initial_W, name ='W'+str(i)) )
            self.b.append( theano.shared(value = numpy.zeros(dimensions[i+1], dtype = theano.config.floatX), name = 'b_hidden'+str(i)) )
            self.b_prime.append( theano.shared(value = numpy.zeros(dimensions[i], dtype = theano.config.floatX), name = 'b_visible'+str(i)) )
        
        
        self.params = []
        for i in xrange(self.n_layers):
            self.params.extend([self.W[i], self.b[i], self.b_prime[i]])
        self.moments = []
        for p in self.params:
            self.moments.append(theano.shared(value = numpy.zeros(p.get_value(borrow=True).shape, dtype = theano.config.floatX)))
        #self.params.append( theano.shared(value = numpy.zeros(dimensions[-1], dtype = theano.config.floatX), name = 'top') )
    def corruptInputBinominal(self, input, p):
        return self.theano_rng.binomial(input.shape, 1, p)*input
        
    def goThrough(self, input, s, t):
        for i in xrange(s, t):
            input = T.nnet.sigmoid( T.dot(input, self.params[i*3]) + self.params[i*3+1] )
        return input
        
    def goBack(self, input, t, s):
        for i in xrange(t-1,s-1,-1):
            input = T.nnet.sigmoid( T.dot(input, self.params[i*3].T) + self.params[i*3+2] )
        return input
    
    def getTestingFunc(self):
        input = T.dvector()        
        y = input
        for i in xrange(0, self.n_layers):
            y = T.maximum(0.0, T.dot(y, self.params[i*3]) + self.params[i*3+1] )
            if i != self.n_layers-1:
                y = y/2
        train_func = theano.function( inputs = [input], outputs=[y])
        return train_func
        
    def getTrainingFunc2(self):
        input = T.dmatrix()
        target = T.dvector()
        learning_rate = T.scalar()
        
        y = input
        for i in xrange(0, self.n_layers-1):
            y = T.maximum(0.0, T.dot(y, self.params[i*3]) + self.params[i*3+1] )
            y = y*self.theano_rng.binomial(y.shape, 1, 0.5)
        
        y = T.maximum(0, T.dot(y, self.params[(self.n_layers-1)*3]) + self.params[(self.n_layers-1)*3+1] )
        
        y = T.squeeze(y.T)
        #y = T.dot(y, self.params[-1])
        diff = y - target
        #regulator = theano.printing.Print('norm:')(T.sum(abs(y))*alpha)
        #L = theano.printing.Print('L:')(T.sum(diff*diff) + regulator)
        L = T.sum(diff*diff) #- target*T.log(y) - (1-target)*T.log(1-y)
        
        gparam = T.grad(L, [ self.params[i] for i in xrange(len(self.params)) if i%3 != 2 ])

        updates = {}
        for i,p,g,m in zip(xrange(len(gparam)),[ self.params[i] for i in xrange(len(self.params)) if i%3 != 2 ], gparam, [ self.moments[i] for i in xrange(len(self.moments)) if i%3 != 2 ]):
            if i%2 == 0:
                updates[m] = 0.9*m - learning_rate*0.0005*p - learning_rate*g        
            else:
                updates[m] = 0.9*m - learning_rate*g
            updates[p] = p + m

        train_func = theano.function( inputs = [input, target, learning_rate], outputs=[L,y], updates= updates)
        return train_func
        
    def getTrainingFunc(self, s, t):
        input = T.dvector()
        corrupt_input = T.dvector()
        learning_rate = T.scalar()
        alpha = T.scalar()
        
        tidle_x = corrupt_input
        y = self.goThrough(tidle_x, s, t)
        z = self.goBack(y, t, s)
        diff = input - z
        #regulator = theano.printing.Print('norm:')(T.sum(abs(y))*alpha)
        regulator = T.sum(abs(y))*alpha
        #L = theano.printing.Print('L:')(T.sum(diff*diff) + regulator)
        L = T.sum(diff*diff)
        
        gparam = T.grad(L, self.params[(s*3):(t*3)])

        updates = {}
        for p,g,m in zip(self.params[(s*3):(t*3)], gparam, self.moments[(s*3):(t*3)]):
            updates[m] = 0.9*m - learning_rate*g
            updates[p] = p + m

        train_func = theano.function( inputs = [input, corrupt_input, learning_rate, alpha], outputs=[L,regulator], updates= updates)
        return train_func

    def plotW(self , patch_shape, m,n, file = None):
        w = self.params[0].get_value()
        col = numpy.arange(self.dimensions[1])
        numpy.random.shuffle(col)
        k = 0
        for i in xrange(m):
            for j in xrange(n):
                k = k + 1
                plt.subplot(m,n,k)
                plt.imshow(w[:,col[k]].reshape(patch_shape))
        if file != None:
            plt.savefig(file)
            plt.clf()
        else:
            plt.show()
            plt.clf()
    
    
    def save(self,name):
        f = open(name, 'wb')
        cPickle.dump(self, f)
        f.close()
        
    @staticmethod
    def load(name):
        f = open(name, 'rb')
        sda = cPickle.load(f)
        f.close()
        return sda

def Pretrain(sda, data, loops, rate):
    L = 0
    R = 0
    input = T.dvector()
    through = theano.function( inputs = [input], outputs = input)
    for lvl in xrange(sda.n_layers-1):
        train = sda.getTrainingFunc(lvl,lvl+1)
        for loop in xrange(loops*len(data[0])):
            p0 = random.randint(0, len(data[0])-1)
            p1 = random.randint(0, len(data[1])-1)
            patch0 = numpy.log(abs(0.7*data[0][p0] + 0.3*data[1][p1])**2+1)/20.0*0.8+0.1
            patch1 = numpy.log(abs(data[0][p0])**2+1)/20.0*0.8+0.1
            patch1 /= numpy.dot(patch1, patch1)
#            plt.subplot(211)
#            plt.imshow(patch0.reshape((5,128)))
#            plt.subplot(212)
#            plt.imshow(patch1.reshape((5,128)))
#            plt.show()
            l,r = train(through(patch1), through(patch1), rate, 0.05)
            L = L + l 
            R = R + r
            if loop%500 == 499:
                print lvl, loop, ':', 10*numpy.log10(0.75**2/(L/500.0/len(data[0][0]))), R/500.0
                L = 0
                R = 0
            
        input = T.dvector()
        through = theano.function( inputs = [input], outputs = sda.goThrough(input, 0, lvl+1) )

def FineTuning(sda, data, loops, rate):
    L = 0
    L2 = 0
    R = 0
    train = sda.getTrainingFunc2()
    batchsize = 128
    batch = numpy.zeros((batchsize, len(data[0][0])))
    target = numpy.asarray([ 1-(i%2) for i in xrange(batchsize) ])
    for loop in xrange(loops*len(data[0])):
        
        for i in xrange(batchsize/2):
            p0 = random.randint(0, len(data[0])-1)
            p1 = random.randint(0, len(data[1])-1)
            patch0 = numpy.log(abs(data[0][p0])**2+1)/20.0*0.8+0.1
            patch1 = numpy.log(abs(data[1][p1])**2+1)/20.0*0.8+0.1
    
            patch1 /= numpy.dot(patch1, patch1)
            patch0 /= numpy.dot(patch0, patch0)        
            batch[2*i] = patch1
            batch[2*i+1] = patch0
            
        l,r = train(batch, target, rate/batchsize)
        L = L + (abs(r-target) < 0.5).mean()
        
        L2+= l/batchsize
        R = R + r.mean()
        if loop%50 == 49:
            print loop, ':', L/50.0, R/50.0, L2/50.0
            L = 0
            R = 0
            L2 = 0

def Testing(sda, data):
    L, R = [], []
    test = sda.getTestingFunc()
    for f in data[0]:
        f = numpy.log(abs(f)**2+1)/20.0*0.8+0.1
        f /= numpy.dot(f, f)   
        y = test(f)
        L.append(y)
    for f in data[1]:
        f = numpy.log(abs(f)**2+1)/20.0*0.8+0.1
        f /= numpy.dot(f, f)   
        y = test(f)
        R.append(y)
    return numpy.array(L).squeeze(), numpy.array(R).squeeze()
    
def generate_data(sub_names, mov_names):
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
                
                if line[3] != 'Default' or line[9].startswith('{'):
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
    
    return speech, noise
       
    
if __name__ == '__main__':    
    #random.seed()
    #random.shuffle(speech)
    #random.shuffle(noise)
    #for f in speech:
    #    plt.imshow(numpy.log(abs(f)**2+1).reshape((5, 128)))
    #    plt.show()
    N = 10
    sub_names = [ '../data/raw/sub (%d).ass'%i for i in xrange(1, N+1) ]
    mov_names = [ '../data/raw/mov (%d).mkv'%i for i in xrange(1, N+1)]

    speech, noise = generate_data(sub_names[:3], mov_names[:3])
    tspeech, tnoise = generate_data(sub_names[3:4], mov_names[3:4])
    dimensions = [ len(speech[0]), len(speech[0]), len(speech[0]), 1]
    sda = SDA(dimensions)
    #sda = SDA.load('sda_line')
    #Pretrain(sda, [speech, noise], 1, 0.0001)
    for checkpoint in xrange(100):
        FineTuning(sda, [speech, noise], 1, 0.001/(checkpoint+1.0))
        sda.save('LeRU-NNN1-'+time.strftime('%Y-%m-%d_%H.%M.%S')+'.net')
        L, R = Testing(sda, [tspeech, tnoise])
        a,b,c=sklearn.metrics.roc_curve([1 for i in L ]+[0 for i in R], L.tolist() + R.tolist())
        plt.hold(True)
        plt.plot(a,b)
        plt.plot([0,1],[0,1])
        plt.savefig('LeRU-NNN1-'+time.strftime('%Y-%m-%d_%H.%M.%S')+'.png')
        plt.close()
    #model = linear_model.LogisticRegression()
    #X = numpy.log(abs(numpy.asarray(speech+noise))**2+1)
    #y = [1 for i in xrange(len(speech))]+[0 for i in xrange(len(noise))]
    #model.fit(X, y)
    #print model.score(X,y)


