from common.processor import processor
import subprocess
from common import constants
import time
import json
import os
import urllib2
import urllib

class sub_generator(processor):
    
    def __init__(self, istream_handle, infile, outfile):
        super(sub_generator, self).__init__()
        self.istream_handle = istream_handle
        self.infile = infile
        self.outfile = outfile
        
    def run(self):
        fout = open(self.outfile, 'w')
        count = 0
        while self.istream_handle.more_data():
            pos, n, seg = self.istream_handle.read(1)
            if not seg:
                break
            seg = seg[0][0]
            print 'sub', seg
            tmp_file = '%s/tmp_%d.flac' % (constants.TMP_PATH, time.clock())
            args = [constants.FFMPEG_PATH, '-v', '0', '-y', '-i', self.infile, '-ss', str(seg[0]-0.3), '-t', str(seg[1]-seg[0]+0.6), '-vn', '-ar', str(constants.GOOGLE_AUDIO_SAMPLE_RATE), '-ac', '1', '-f', 'flac', tmp_file]       
            ffmpeg = subprocess.Popen(args)
            ffmpeg.wait()
            args = [constants.CURL_PATH, '-k', '--data-binary', '@' + tmp_file, '--header', 'Content-type: audio/x-flac; rate=16000', 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=en-US&maxresults=6']
            curl = subprocess.Popen(args, stdout = subprocess.PIPE)           
            curl.wait()
            os.remove(tmp_file)
            data = curl.communicate()[0]
            try:
                obj = json.loads(data)
                text = obj['hypotheses'][0]['utterance']
            except:
                text = ''
            
            while True:
                try:
                    post_data = {'Authorization':'bearer '+token}
                    post_data = urllib.urlencode(post_data)
                    conn = urllib2.urlopen(url = 'http://api.microsofttranslator.com/V2/Http.svc/Translate?text=' + text +'&from=en&to=zh-CHS', data = post_data)
                    print conn.read()
                    break
                except:
                    post_data = {'grant_type':'client_credentials', 'client_id':'autosub','client_secret':'AIZj1/ONTvxxF2mv1IlvP6Bhsi/jpGOsQu/yVnWq1rI=', 'scope':'http://api.microsofttranslator.com'}
                    post_data = urllib.urlencode(post_data)
                    conn = urllib2.urlopen(url = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13?', data = post_data)
                    obj = json.loads(conn.read())
                    token = obj['access_token']
            
                                    
    
            seg = (int(seg[0]*100), int(seg[1]*100))
            count = count + 1
            fout.write("%d\n%02d:%02d:%02d,%03d --> %02d:%02d:%02d,%03d\n%s\n\n" % (count, seg[0]/360000, (seg[0]%360000)/6000, (seg[0]%6000)/100, (seg[0]%100)*10, seg[1]/360000, (seg[1]%360000)/6000, (seg[1]%6000)/100, (seg[1]%100)*10, text))
            fout.flush()            
            print count, text
        
        fout.close()
            