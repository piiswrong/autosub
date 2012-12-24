import theano
import theano.tensor as T
import numpy
import matplotlib.pyplot as plt
import matplotlib
import cPickle
from time import clock
from PIL import Image
theano.config.floatX = 'float64'
my_dtype = numpy.float64

def PSNR(x, y):
    z = x-y
    mse = numpy.sum(z*z)/numpy.prod(z.shape)
    return 10*numpy.log10(1/mse)
    

def LineCorrupt(x, level):
    rand = numpy.random.binomial(1,level,(x.shape[0],x.shape[1]/28)).astype(my_dtype)
    corrupt = numpy.zeros(x.shape, dtype = my_dtype)
    for i in xrange(corrupt.shape[0]):
        for j in xrange(corrupt.shape[1]):
            corrupt[i,j] = rand[i,j/28]
    return (x*corrupt)

def SaltPepperCorrupt(x, level):
    return x*numpy.random.binomial(1,level,x.shape)

def GausianCorrupt(x, level):
    return x + numpy.random.normal(0, level,x.shape)

class PatchSource(object):
    def __init__(self, image, patch_shape = (16,16), corrupt_image = None):
        self.im = Image.open(image).convert(mode='L')
        self.patch_shape = patch_shape
        self.length = numpy.prod(patch_shape)
        self.m = self.image2array(self.im).astype(my_dtype)/255.0
        if corrupt_image == None:
            self.m_corrupt = GausianCorrupt(self.m, 30/255.0)
        else:
            im = Image.open(corrupt_image).convert(mode='L')
            self.m_corrupt = self.image2array(im).astype(my_dtype)/255.0
        self.lx = self.m.shape[1] - patch_shape[1] + 1
        self.ly = self.m.shape[0] - patch_shape[0] + 1
        self.max = self.lx*self.ly
        self.reset()
        
    def reset(self):
        self.cur = 0
        self.seq = numpy.arange(self.max)
        numpy.random.shuffle(self.seq)
        
    def image2array(self, im):
        newArr = numpy.fromstring(im.tostring(),numpy.uint8)
        newArr = numpy.reshape(newArr,im.size)
        return newArr

    def array2image(self, a):
        #a=a/a.max()*255.0 #optional.
        im=Image.Image()
        im=Image.fromarray(numpy.uint8(a))
        return im
        
    def nextPatch(self, seek = None):
        if seek != None:
            x = seek%self.lx
            y = seek/self.lx
        else:
            x = self.seq[self.cur]%self.lx
            y = self.seq[self.cur]/self.lx
            self.cur = self.cur+1
        return (self.m[y:y+self.patch_shape[0], x:x+self.patch_shape[1]].reshape(self.length), 
             self.m_corrupt[y:y+self.patch_shape[0], x:x+self.patch_shape[1]].reshape(self.length))
             
def recover(data, func):
    m = numpy.zeros(data.m.shape, dtype = my_dtype)
    for i in xrange(data.max):
        if i%1000 == 0:
            print i
        x = i%data.lx
        y = i/data.lx
        m[y:y+data.patch_shape[0], x:x+data.patch_shape[1]] += func(data.m_corrupt[y:y+data.patch_shape[0], x:x+data.patch_shape[1]].reshape(data.length)).reshape(data.patch_shape)
    my = data.m.shape[0]
    mx = data.m.shape[1]
    for y in xrange(my):
        for x in xrange(mx):
            m[y,x] = m[y,x] / min(y+1, my-y, data.patch_shape[0]) / min(x+1, mx-x, data.patch_shape[1])
    return m

  
class SDA(object):
    def __init__(self, dimensions):
        self.dimensions = [ i for i in dimensions ]
        self.n_layers = len(dimensions)-1
        self.W = []
        self.b = []
        self.b_prime = []
        numpy_rng = numpy.random.RandomState(123)
        self.theano_rng = T.RandomStreams(numpy_rng.randint(2**30))
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
        for p,g in zip(self.params[(s*3):(t*3)], gparam):
            updates[p] = p - learning_rate*g

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
    for lvl in xrange(sda.n_layers):
        train = sda.getTrainingFunc(lvl,lvl+1)
        for loop in xrange(loops):  
            data.reset()
            sda.plotW(data.patch_shape, 4, 4, str(lvl)+str(loop))
            for i in xrange(data.max):
                patch = data.nextPatch()
                l,r = train(through(patch[0]), through(patch[1]), rate/(1+loop), 0.05)
                L = L + l
                R = R + r
                if i%500 == 499:
                    print lvl, i, ':', 10*numpy.log10(1/(L/500.0/data.length)), R/500.0
                    L = 0
                    R = 0
            
        input = T.dvector()
        through = theano.function( inputs = [input], outputs = sda.goThrough(input, 0, lvl+1) )

def FineTuning(sda, data, loops, rate):
    L = 0
    R = 0
    train = sda.getTrainingFunc(0,sda.n_layers)
    for loop in xrange(loops):
        data.reset()
        for i in xrange(data.max):
            patch = data.nextPatch()
            l,r = train(patch[0], patch[1], rate/(1+loop), 0.05)
            L = L + l
            R = R + r
            if i%500 == 499:
                print i, ':', 10*numpy.log10(1/(L/500.0/data.length)), R/500.0
                L = 0
                R = 0
                
                
if __name__ == "__main__":
    #x = numpy.load('b_train.npy').astype(my_dtype)
    #x_corrupt = SaltPepperCorrupt(x)
    data = PatchSource('test_images/lena.png', (6,6) , 'test_images/1.bmp')
    dimensions = [ data.length, 5*data.length, 5*data.length ]
    sda = SDA(dimensions)
    #sda = SDA.load('sda_line')
    Pretrain(sda, data, 2, 0.004)
    FineTuning(sda, data, 2, 0.0005)
    
    
    input = T.dvector()
    f = theano.function( inputs = [input], outputs = sda.goBack(sda.goThrough(input,0,sda.n_layers), sda.n_layers, 0) )
    
    m = recover(data, f)
    plt.subplot(131)
    plt.imshow(m, cmap=matplotlib.cm.gray)
    plt.subplot(132)
    plt.imshow(data.m, cmap=matplotlib.cm.gray)
    plt.subplot(133)
    plt.imshow(data.m_corrupt, cmap=matplotlib.cm.gray)
    plt.show()
    print PSNR(m, data.m)
    
    p = data.nextPatch(numpy.random.randint(data.max))
    plt.subplot(131)
    plt.imshow(numpy.reshape(f(p[1]).tolist(), data.patch_shape), cmap=matplotlib.cm.gray)
    plt.subplot(132)
    plt.imshow(numpy.reshape(p[1].tolist(), data.patch_shape), cmap=matplotlib.cm.gray)
    plt.subplot(133)
    plt.imshow(numpy.reshape(p[0].tolist(), data.patch_shape), cmap=matplotlib.cm.gray)
    plt.show()
    
    sda.save('lenaL1gaussian-no-regulator24')
    """
    f = open('sda_salt_pepper','wb')
    cPickle.dump(sda, f)
    f.close()
    """
    """
    train = sda.getTrainingFunc(0,1)
    
        
    xx = T.dmatrix()
    level = T.dscalar()
    f = theano.function([xx],da.get_reconstructed_input(da.get_hidden_values(xx)))
    corrupt = theano.function([xx, level], da.get_corrupted_input(xx, level))
    fout = open("t.txt","w");
    r = numpy.reshape(f(corrupt(x, 0.5)).tolist(), (28, 28))
    plt.imshow(r)
    plt.show()
    plt.imshow(numpy.reshape(corrupt(x, 0.5).tolist(), (28, 28)))
    plt.show()
    
    r = numpy.reshape(x[1000].tolist(), (28, 28))
    plt.imshow(r)
    
    """