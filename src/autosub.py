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

    def OnTimer(self,evt):
        super(MainFrame, self).OnTimer(self)

        if self.ohandle.has_data(1):            
            (start,self.end,text)=self.ohandle.read(1)[2][0][0]            
            self.player.video_set_subtitle_file(self.subtitle)
            
            


        # Set buffer time
        self.buffergauge.SetValue(self.end*self.buffergauge.GetRange()*1000/self.player.get_length())
        
        # Link with subtitle

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
    
