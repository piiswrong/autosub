import core.ffmpeg_decoder as fd
import core.sub_generator as sg
from core.naive_vad2 import *
import VLC.vlc_wx as vlc_wx
import sys
import wx


class MainFrame(vlc_wx.MyFrame):
    def __init__(self,title):
        fram=vlc_wx.MyFrame.__init__(self,title)
        self.subtitle=None
        self.ohandle=None
        # variable
        self.end=0

        
    def OnOpen(self, evt):
        super(MainFrame, self).OnOpen(self)
        lan={"English":"en" ,"Chinese":"zh-cn" ,"Japanese":"ja"}
        lang_from = None
        lang_to = None
        source = None
        target = None
        if self.select_dialog.isrecognize==True:            
            # Set recognize parameter
            lang_from=lan[self.select_dialog.sorcelan]
            
        if self.select_dialog.istranslate==True:
            # Set translation parameter
            lang_to=lan[self.select_dialog.targetlan]

        source=self.mediapath
        # Set target name
        if not target:
            target = source[:source.rfind('.')] + '.srt'
        self.subtitle=target       
        
        self.currentfile=None
        
        dec = fd.ffmpeg_decoder(source)
        vad = naive_vad(dec.ostream.get_handle())
        sub = sg.sub_generator(vad.ostream.get_handle(), source, target, lang_from = lang_from, lang_to = lang_to)
        self.ohandle = sub.ostream.get_handle()
        dec.start()
        vad.start()
        sub.start()

    # float second to time string 
    def OnFormatTime(self,floattime):
        time=int(floattime)
        str_decimaltime=str(int((floattime-time)*1000))
        sec=time%60
        all_min=time/60
        hour=all_min/60
        mini=all_min%60
        if sec<9:
            str_sec='0'+str(sec)
        else:
            str_sec=str(sec)
        if mini<9:
            str_min='0'+str(mini)
        else:
            str_min=str(mini)
        if hour<9:
            str_hour='0'+str(hour)
        else:
            str_hour=str(hour)

        string_time=str_hour+':'+str_min+':'+str_sec+'.'+str_decimaltime
        return string_time

    def OnTimer(self,evt):
        super(MainFrame, self).OnTimer(self)
        if self.ohandle.has_data(1):            
            (start,self.end,text)=self.ohandle.read(1)[2][0][0]            
            self.player.video_set_subtitle_file(self.subtitle)
            str_start=self.OnFormatTime(start)
            str_end=self.OnFormatTime(self.end)
            self.subpanel.AddSub(self.subpanel,str_start,str_end,text)
        # Set buffer time
        if self.player.get_length()!=0:
            self.buffergauge.SetValue(self.end*self.buffergauge.GetRange()*1000/self.player.get_length())        
        # Link with subtitle
        #self.subpanel.OpenFile(self.subtitle)

 
        
if __name__ == '__main__':
        # Create a wx.App(), which handles the windowing system event loop
        app = wx.PySimpleApp()
        # Create the window containing our small media player
        PlayerFrame = MainFrame("AutoSub")
        # Subtitle(PlayerFrame, title='Subtitle',positon=(1100,300))
        PlayerFrame.SetPosition((0,0))
        app.SetTopWindow(PlayerFrame)
        # show the player window centred and run the application
        PlayerFrame.Centre()
        PlayerFrame.Show()
        app.MainLoop()
    
