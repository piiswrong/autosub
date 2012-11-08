from common.processor import processor
from common.data_stream import data_stream
import subprocess
from common import constants
import time
import json
import os
import tempfile
import urllib2
import urllib

class sub_generator(processor):
    
    def __init__(self, istream_handle, infile, outfile, lang_from = None, lang_to = None):
        super(sub_generator, self).__init__()
        self.istream_handle = istream_handle
        self.infile = infile
        self.outfile = outfile
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.ostream = data_stream(0)
        
    def run(self):
        fout = open(self.outfile, 'w')
        count = 0
        while self.istream_handle.more_data():
            pos, n, seg = self.istream_handle.read(1)
            if not seg:
                break
            seg = seg[0][0]
            print 'sub', seg
            
            sub_text = ''
            if self.lang_from:
                tmp_file = tempfile.mktemp('.flac')
                args = [constants.FFMPEG_PATH, '-v', '0', '-y', '-i', self.infile, '-ss', str(seg[0]-0.3), '-t', str(seg[1]-seg[0]+0.6), '-vn', '-ar', str(constants.GOOGLE_AUDIO_SAMPLE_RATE), '-ac', '1', '-f', 'flac', tmp_file]       
                ffmpeg = subprocess.Popen(args)
                ffmpeg.wait()
                url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=' + self.lang_from + '&maxresults=6'
                length = os.path.getsize(tmp_file)
                flac = open(tmp_file, 'rb')
                req = urllib2.Request(url, data = flac)
                req.add_header('Content-length', '%d' % length)
                req.add_header('Content-type', 'audio/x-flac; rate=16000')
                try:
                    data = urllib2.urlopen(req).read().strip()
                except :
                    pass
                flac.close()
                os.remove(tmp_file)
                try:
                    obj = json.loads(data)
                    recog_text = obj['hypotheses'][0]['utterance']
                except:
                    recog_text = 'Recognition service error.'
                
                print 'recognition:', recog_text
                sub_text = recog_text
            
                if self.lang_to:
                    trans_text = 'Translation service error.'
                    for retry in xrange(5):
                        try:
                            url = 'http://api.microsofttranslator.com/V2/Http.svc/Translate?text=' + urllib2.quote(recog_text.encode('utf-8')) +'&from=' + self.lang_from + '&to=' + self.lang_to
                            req = urllib2.Request(url)
                            req.add_header('Authorization', 'bearer '+token)
                            conn = urllib2.urlopen(req)
                            trans_text = conn.read()[68:-9].decode('utf-8').encode('gbk')
                            break
                        except:
                            post_data = {'grant_type':'client_credentials', 'client_id':'autosub','client_secret':'autosubautosubautosub', 'scope':'http://api.microsofttranslator.com'}
                            post_data = urllib.urlencode(post_data)
                            conn = urllib2.urlopen(url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13?', data = post_data)
                            obj = json.loads(conn.read())
                            token = obj['access_token']
                    print 'translation:', trans_text
                    sub_text = trans_text
            
            self.ostream.write([(seg[0], seg[1], sub_text)])            
            
            seg = (int(seg[0]*100), int(seg[1]*100))
            count = count + 1  
            if not sub_text:
                sub_text = '%d' % count    
            fout.write("%d\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n%s\n\n" % (count, seg[0]/360000, (seg[0]%360000)/6000, (seg[0]%6000)/100, (seg[0]%100)*10, seg[1]/360000, (seg[1]%360000)/6000, (seg[1]%6000)/100, (seg[1]%100)*10, sub_text))
            fout.flush()
            print count, sub_text
        
        fout.close()
            