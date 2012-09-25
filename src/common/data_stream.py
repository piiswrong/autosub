import threading
import collections

class data_stream_handle(object):
    """
    subscriber's handle of data streams
    """
    def __init__(self, stream):
        self.stream = stream
        self.pos = 0
        self.i = 0
    
    def read(self, n = float('inf'), res = []):
        return self.stream.read(self, n, res)

    def write(self, data):
        return self.stream.write(data)

class data_stream(object):
    """
    Interface that holds and transfers data between processors.    
    """
    def __init__(self, sample_rate, total_samples = float('inf'), max_queue_count = float('inf')):
        self.sample_rate = sample_rate
        self.total_samples = total_samples
        
        self.lock = threading.Lock()
        self.write_event = threading.Event()
        self.read_event = threading.Event()
        self.queue = collections.deque()
        self.max_queue_count = max_queue_count
        self.head_pos = 0
        self.tail_pos = 0
        self.head_i = 0
        self.handles = []
        self.running = False        
        
    def get_handle(self):
        if self.running:
            return None
        handle = data_stream_handle(self)
        self.handles.append(handle)
        return handle
        
    def get_total_samples(self):
        return self.total_samples
    
    def read(self, handle, n = float('inf'), res = []):
        self.lock.acquire()
            
        while self.tail_pos - handle.pos < n:
            self.write_event.clear()
            self.lock.release()
            self.write_event.wait()
            self.lock.acquire()

        total_read = 0

        while handle.i - self.head_i < self.queue.count() and total_read < n:
            tmp = self.queue[handle.i - self.head_i]
            handle.i = handle.i + 1
            total_read = total_read + len(tmp)
            res.append(tmp)
        handle.pos = handle.pos + total_read
        
        min_i = min([ h.i for h in self.handles ])
        while self.head_i < min_i:
            self.queue.popleft()
            self.head_i = self.head_i + 1
            self.read_event.set()
            
        self.lock.release()
        return handle.pos - total_read, total_read, res
    
    def write(self, data):
        self.lock.acquire()
        self.running = True
        while self.queue.count() == self.max_queue_count:
            self.read_event.clear()
            self.lock.release()
            self.read_event.wait()
            self.lock.acquire()
            
        self.queue.append(data)
        self.tail_pos = self.tail_pos + len(data)
        self.write_event.set()
        self.lock.release()
        
        return
        