import core.ffmpeg_decoder as fd
import core.sub_generator as sg
from core.naive_vad2 import *
import VLC.vlc_wx as vlc_wx
import sys
import wx

class MainFrame(vlc_wx.MyFrame):
    def __init__(self,title):
        fram=vlc_wx.MyFrame.__init__(self,title)

    def OnOpen(self, evt):
        super(MainFrame, self).OnOpen(self)
        lan={"English":"en" ,"Chinese":"zh-cn" ,"Janpanese":"ja"}
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
        print source
        print lang_from
        print lang_to
        # Set target name
        if not target:
            target = source[:source.rfind('.')] + '.srt'
            
        dec = fd.ffmpeg_decoder(source)
        vad = naive_vad(dec.ostream.get_handle())
        sub = sg.sub_generator(vad.ostream.get_handle(), source, target, lang_from = lang_from, lang_to = lang_to)
        ohandle = sub.ostream.get_handle()
        dec.start()
        vad.start()
        sub.start()            

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
    
