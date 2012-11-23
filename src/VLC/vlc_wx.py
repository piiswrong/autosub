# import external libraries
import wx # 2.8
import wx.lib.platebtn as pbtn
import wx.lib.stattext as stattext
import sys
import myvlc.vlc as vlc
from spectrum_widget.SpecWin import *
# import standard libraries
import os
import user
from subtitle_widget.SubtitleEditor import * 

class MyFrame(wx.Frame):
        """The main window
        """

        def __init__(self,title):
                frame=wx.Frame.__init__(self, None, -1, title)               
                
                #Menu Bar
                self.frame_menubar=wx.MenuBar()
                #  File Menu
                self.icon=wx.Icon('./VLC/Icons/autosub.ico',wx.wx.BITMAP_TYPE_ICO);
                self.SetIcon(self.icon);
                self.file_menu=wx.Menu()
                menu_open=self.file_menu.Append(-1,"&Open \tCtrl+O")
                self.file_menu.AppendSeparator()
                menu_close=self.file_menu.Append(-1,"&Close \tCtrl+C")
                self.Bind(wx.EVT_MENU, self.OnOpen, menu_open)
                self.Bind(wx.EVT_MENU, self.OnExit, menu_close)
                self.frame_menubar.Append(self.file_menu, "&File")


                #  Edit Menu
                self.edit_menu=wx.Menu()
                menu_play=self.edit_menu.Append(-1,"&Play \tCtrl+P")
                self.edit_menu.AppendSeparator()
                menu_pause=self.edit_menu.Append(-1,"P&ause \tCtrl+A")
                self.edit_menu.AppendSeparator()
                menu_stop=self.edit_menu.Append(-1,"&Stop \tCtrl+S")
                self.edit_menu.AppendSeparator()
                menu_fullscreen=self.edit_menu.Append(-1,"&FullScreen \tCtrl+F")
                self.edit_menu.AppendSeparator()
                menu_volume=self.edit_menu.Append(-1,"&Volume \tCtrl+V")
                self.edit_menu.AppendSeparator()

                self.Bind(wx.EVT_MENU, self.OnPlay, menu_play);
                self.Bind(wx.EVT_MENU, self.OnPause, menu_pause);
                self.Bind(wx.EVT_MENU, self.OnStop, menu_stop);
                self.Bind(wx.EVT_MENU, self.OnToggleFullScreen, menu_fullscreen);
                self.Bind(wx.EVT_MENU, self.OnToggleVolume, menu_volume);
                self.frame_menubar.Append(self.edit_menu, "&Edit")

                #  Audio Menu
                self.sub=wx.Menu()
                op=self.sub.Append(-1,"Open Subtitle")
                self.sub.AppendSeparator()
                sa=self.sub.Append(-1,"Save Subtitle")

                self.frame_menubar.Append(self.sub, "Subtitle")

                #  Video Menu
                self.video_menu=wx.Menu()
                self.video_menu.Append(-1,"NULL")
                self.video_menu.AppendSeparator()
                self.video_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.video_menu, "Video")


                #  Tools Menu
                self.tools_menu=wx.Menu()
                self.tools_menu.Append(-1,"NULL")
                self.tools_menu.AppendSeparator()
                self.tools_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.tools_menu, "Tools")

                #  View Menu
                self.view_menu=wx.Menu()
                self.view_menu.Append(-1,"NULL")
                self.view_menu.AppendSeparator()
                self.view_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.view_menu, "View")

                #  Help Menu
                self.help_menu=wx.Menu()                
                menu_feedback=self.help_menu.Append(-1,"&FeedBack")
                self.help_menu.AppendSeparator()
                self.help_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.help_menu, "Help")
                self.SetMenuBar(self.frame_menubar)
                
                self.Bind(wx.EVT_MENU, self.OnFeedBack, menu_feedback);
                # common attributes in the screen
                myfont=wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL,False, u'Segoe UI')
                Backgroud=(57,59,66)
                Fontcolor=(229,229,229)
                bback=(77,77,77);
                self.SetBackgroundColour(Backgroud)
 
                #Panels
                # This is the subtitlepanel
                self.subtitlepanel=wx.Panel(self, -1);

                # The first panel of the video
                self.videopanel = wx.Panel(self, -1)
                self.videopanel.SetBackgroundColour(wx.BLACK)

                # The second panel holds controls
                ctrlpanel = wx.Panel(self, -1 )

                #  timeslider
                self.timeslider = wx.Slider(ctrlpanel, -1, 0, 0, 1000,size=(598,20)) #timeline
                self.timeslider.SetRange(0, 1000)
                self.timeslider.SetBackgroundColour(Backgroud)
                #  buffergauge
                self.buffergauge = wx.Gauge(ctrlpanel, -1,1000,size=(590,5)) 
                self.buffergauge.SetRange(1000)
                self.buffergauge.SetBackgroundColour(Backgroud)
                #  display time                                                                          
                self.displaytime=stattext.GenStaticText(ctrlpanel, -1, "00:00/00:00",style=wx.ALIGN_RIGHT)
                self.displaytime.SetBackgroundColour(Backgroud)
                self.displaytime.SetFont(myfont)

                #  pause button
                pause  = pbtn.PlateButton(ctrlpanel)
                pause.SetBackgroundColour(Backgroud)
                pausebmp=wx.Bitmap("./VLC/Icons/pause.png",wx.BITMAP_TYPE_PNG)
                pausebmp.SetSize(size=(35,35))
                pause.SetBitmap(bmp=pausebmp)
                #  play button
                play   = pbtn.PlateButton(ctrlpanel)
                play.SetBackgroundColour(Backgroud)
                playbmp=wx.Bitmap("./VLC/Icons/play.png",wx.BITMAP_TYPE_PNG)
                playbmp.SetSize(size=(40,40))
                play.SetBitmap(bmp=playbmp)
                #  stop button
                #stop   = pbtn.PlateButton(ctrlpanel, label="Stop")
                #stop.SetBackgroundColour(Backgroud)
                #  volume button
                self.volume = pbtn.PlateButton(ctrlpanel)
                self.volume.SetBackgroundColour(Backgroud)
                volumebmp=wx.Bitmap("./VLC/Icons/volume.png",wx.BITMAP_TYPE_PNG)
                self.volume.SetSize((20,20))
                self.volume.SetBitmap(bmp=volumebmp)
                #  fullscreen button
                fullscreen = pbtn.PlateButton(ctrlpanel)
                fullscreen.SetBackgroundColour(Backgroud)
                fullscreenbmp=wx.Bitmap("./VLC/Icons/fullscreen.png", wx.BITMAP_TYPE_PNG)
                fullscreen.SetSize(size=(20,20))
                fullscreen.SetBitmap(bmp=fullscreenbmp)
                #  right button
                right=pbtn.PlateButton(ctrlpanel)
                right.SetBackgroundColour(Backgroud)
                rightbmp=wx.Bitmap("./VLC/Icons/right.png",wx.BITMAP_TYPE_PNG)
                right.SetSize(size=(20,20))
                right.SetBitmap(bmp=rightbmp)
                #  left button
                left=pbtn.PlateButton(ctrlpanel)
                left.SetBackgroundColour(Backgroud)
                leftbmp=wx.Bitmap("./VLC/Icons/left.png",wx.BITMAP_TYPE_PNG)
                left.SetSize(size=(20,20))
                left.SetBitmap(bmp=leftbmp)
                #  voice slider
                self.volslider = wx.Slider(ctrlpanel, -1, 0, 0, 100, size=(83, -1))
                self.volslider.SetBackgroundColour(Backgroud)
                                
                ''' this is the Subtitle Editor'''
                # pos=wx.Frame.GetPosition();                
                """Bind Control to Events"""
                self.Bind(wx.EVT_BUTTON, self.OnPlay, play)
                self.Bind(wx.EVT_BUTTON, self.OnPause, pause)
                #self.Bind(wx.EVT_BUTTON, self.OnStop, stop)
                self.Bind(wx.EVT_BUTTON, self.OnToggleVolume, self.volume)
                self.Bind(wx.EVT_SLIDER, self.OnSetVolume, self.volslider)
                self.Bind(wx.EVT_SLIDER, self.OnSetPlayTime, self.timeslider)
                self.Bind(wx.EVT_BUTTON, self.OnToggleFullScreen, fullscreen)                
                self.Bind(wx.EVT_BUTTON, self.OnRight,right)
                self.Bind(wx.EVT_BUTTON, self.OnLeft, left)
                # Give a pretty layout to the controls                
                ctrlbox=wx.GridBagSizer(vgap=0, hgap=0)
                ctrlbox.Add(self.displaytime,(0,1))                
                ctrlbox.Add(self.volume,(0,8))                
                ctrlbox.Add(self.volslider,(0,9))
                ctrlbox.Add(self.timeslider,(1,0),span=(1,10))
                ctrlbox.Add(self.buffergauge,(2,0),span=(1,10))                
                ctrlbox.Add(left,(4,5))
                ctrlbox.Add(play,(4,6))
                ctrlbox.Add(pause,(4,8))
                ctrlbox.Add(right,(4,7))
                ctrlbox.Add(fullscreen,(4,9),flag=wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
                ctrlpanel.SetSizer(ctrlbox)
                # Put everything togheter
                sizer = wx.BoxSizer(wx.VERTICAL)


                BigSizer = wx.BoxSizer(wx.HORIZONTAL)
                
                sizer.Add(self.videopanel, 1, flag=wx.EXPAND)
                sizer.Add(ctrlpanel, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)
                sizer.SetMinSize((400, 450))
                subsizer=wx.BoxSizer(wx.VERTICAL);
                subsizer.SetMinSize((400,450));
                #####################################Subtitle Panel###################################
                self.subpanel=Subtitle(self,-1);
                self.Bind(wx.EVT_MENU, self.subpanel.OpenFile, op);
                self.Bind(wx.EVT_MENU, self.subpanel.SaveFile, sa);
                self.subpanel.SetSizer(subsizer);
                ####################################CUTTING LINE######################################
                
                splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)

                # subpanelf=wx.Panel(self,-1);
                # BigSizer.Add(subpanelf,flag=wx.EXPAND|wx.RIGHT);
                ####################################END Here##########################################
                
                BigSizer.Add(self.subpanel,flag=wx.EXPAND);
                BigSizer.Add(splitter,flag=wx.EXPAND)
                BigSizer.Add(sizer,flag=wx.EXPAND|wx.RIGHT)
                #######################################SpectrumPanel##################################
                Spec=SpecPanel(self,"VLC/spectrum_widget/Icon/speceg.jpg");
                specsizer=wx.BoxSizer(wx.VERTICAL)
                Spec.SetSizer(specsizer);
                specsizer.SetMinSize((400,300))
                BigSizer.Add(specsizer,flag=wx.EXPAND)

                ####################################################################################
                BigSizer.SetMinSize((1510, 450))

                self.SetSizer(BigSizer)
                self.SetMinSize((1510, 450))

                # finally create the timer, which updates the timeslider
                self.timer = wx.Timer(self)
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

                # VLC player controls
                self.Instance = vlc.Instance('--subsdec-encoding=UTF-8','--freetype-font=PMingLiU')
                self.player = self.Instance.media_player_new()

                self.Bind(wx.EVT_CLOSE,self.OnExit)

                # Set the Fast Key
                acceltbl=wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('O'),1),(wx.ACCEL_CTRL,ord('C'),2),(wx.ACCEL_CTRL,ord('P'),3),(wx.ACCEL_CTRL,ord('A'),4),(wx.ACCEL_CTRL,ord('S'),5),(wx.ACCEL_CTRL,ord('F'),6),(wx.ACCEL_CTRL,ord('V'),7)])
                self.SetAcceleratorTable(acceltbl)
        def SetTheSpec(self,evt):
                return 


        def OnExit(self, evt):
                self.player.stop()
                self.Close()
                evt.Skip()

        def OnOpen(self, evt):
                """Pop up a new dialow window to choose a file, then play the selected file.
                """
                # if a file is already running, then stop it.
                self.OnStop(None)

                # Create a file dialog opened in the current home directory, where
                # you can display all kind of files, having as title "Choose a file".
                dlg = wx.FileDialog(self, "Choose a file", user.home, "","*.*", wx.OPEN)
                if dlg.ShowModal() == wx.ID_OK:
                        dirname = dlg.GetDirectory()
                        filename = dlg.GetFilename()
                        # Creation
                        self.mediapath=unicode(os.path.join(dirname, filename))
                        self.Media = self.Instance.media_new(self.mediapath)
                        #m=self.Instance.media_new(r'D:\shiyan\number3\New folder\1.rmvb')
                        self.player.set_media(self.Media)
                        # Report the title of the file chosen
                        title = self.player.get_title()
                        #  if an error was encountred while retriving the title, then use
                        #  filename
                        if title == -1:
                                title = filename
                        self.SetTitle("%s - AutoSub" % title)

                        # set the window id where to render VLC's video output
                        self.player.set_hwnd(self.videopanel.GetHandle())
                        # set the volume slider to the current volume
                        self.volslider.SetValue(self.player.audio_get_volume() / 2)                        
                        self.title=title             

                        # finally destroy the dialog
                        dlg.Destroy()
                
                        # create the new dialog to choose the recognization and translation
                        self.select_dialog=SelectDialog(None,"Choice")
                        self.select_dialog.ShowModal()
                        # Finally Play~FIXME: this should be made cross-platform
                        self.OnPlay(None)
                else:
                        dlg.Destroy()

        def OnPlay(self, evt):
                """Toggle the status to Play/Pause.

                If no file is loaded, open the dialog window.
                """
                # check if there is a file to play, otherwise open a
                # wx.FileDialog to select a file
                if not self.player.get_media():
                        self.OnOpen(None)
                else:
                        # Try to launch the media, if this fails display an error message
                        if self.player.play() == -1:
                                self.errorDialog("Unable to play.")
                        else:
                                self.timer.Start(100)
                                

        def OnPause(self, evt):
                """Pause the player.
                """
                self.player.pause()

        def OnStop(self, evt):
                """Stop the player.
                """
                self.player.stop()
                # reset the time slider
                self.timeslider.SetValue(0)
                self.timer.Stop()

        def OnTimer(self, evt):
                """Update the time slider according to the current movie time.
                """
                # since the self.player.get_length can change while playing,
                # re-set the timeslider to the correct range.
                length = self.player.get_length()
                self.timeslider.SetRange(-1, length)
                self.buffergauge.SetRange(length)
                
                length_second=length/1000
                self.length_min=length_second/60
                self.length_sec=length_second-self.length_min*60

                # update the time on the slider
                time = self.player.get_time()
                self.timeslider.SetValue(time)

                # update the displaytime 
                second=time/1000
                self.current_min=second/60
                self.current_second=second-self.current_min*60
                if self.current_min<10:
                        str_min="0"+str(self.current_min)
                else:
                        str_min=str(self.current_min)
                if self.current_second<10:
                        str_sec="0"+str(self.current_second)
                else:
                        str_sec=str(self.current_second)
                        
                if self.length_min<10:
                        str_length_min="0"+str(self.length_min)
                else:
                        str_length_min=str(self.length_min)
                if self.length_sec<10:
                        str_length_sec="0"+str(self.length_sec)
                else:
                        str_length_sec=str(self.length_sec)
                self.displaytime.SetLabel(str_min+":"+str_sec+"/"+str_length_min+":"+str_length_sec)

                

        def OnToggleVolume(self, evt):
                """Mute/Unmute according to the audio button.
                """
                is_mute = self.player.audio_get_mute()
                self.player.audio_set_mute(not is_mute)
                if is_mute==True:
                        mutebmp=wx.Bitmap("./VLC/Icons/volume.png",wx.BITMAP_TYPE_PNG)
                        self.volume.SetSize((20,20))
                        self.volume.SetBitmap(bmp=mutebmp)
                else:
                        notmutebmp=wx.Bitmap("./VLC/Icons/no_volume.png",wx.BITMAP_TYPE_PNG)
                        self.volume.SetSize((20,20))
                        self.volume.SetBitmap(bmp=notmutebmp)
                # update the volume slider;
                # since vlc volume range is in [0, 200],
                # and our volume slider has range [0, 100], just divide by 2.
                self.volslider.SetValue(self.player.audio_get_volume() / 2)

        def OnSetVolume(self, evt):
                """Set the volume according to the volume sider.
                """
                volume = self.volslider.GetValue() * 2
                # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
                if self.player.audio_set_volume(volume) == -1:
                        self.errorDialog("Failed to set volume")


        def OnSetPlayTime(self, evt):
                """Set the progress of the movie.
                """
                settime = self.timeslider.GetValue()
                self.player.set_time(settime)
                

        def OnSetBuffer(self, evt):                
                self.buffergauge.SetValue(self.timeslider.GetValue())
                pass


        def OnToggleFullScreen(self, evt):
                is_fullscreen=self.IsFullScreen()
                self.ShowFullScreen(show= not is_fullscreen)               


        def errorDialog(self, errormessage):
                """Display a simple error dialog.
                """
                edialog = wx.MessageDialog(self, errormessage, 'Error', wx.OK|wx.ICON_ERROR)
                edialog.ShowModal()
        def OnFeedBack(self, evt):
                feedbackdialog=FeedBackDialog(None,"FeedBack")
                feedbackdialog.ShowModal()

        def OnRight(self, evt):                
                self.player.set_position(self.player.get_position()+0.03)
                evt.Skip()
        
        def OnLeft(self, evt):
                self.player.set_position(self.player.get_position()-0.03)
                evt.Skip()


class SelectDialog(wx.Dialog):
        def __init__(self,parent,title=""):
                super(SelectDialog,self).__init__(parent,title=title)

                # Attributes
                self.checkbox1=wx.CheckBox(self,label="Need Recognization")
                self.checkbox2=wx.CheckBox(self,label="Need Translation")
                src_lan=["English","Japanese"]
                tran_lan=["Chinese","Japanese","English"]
                self.recg_box=wx.ComboBox(self,-1,value="English",choices=src_lan,style=wx.CB_READONLY)
                self.tran_box=wx.ComboBox(self,-1,value="Chinese",choices=tran_lan,style=wx.CB_READONLY)
                self.button=wx.Button(self,wx.ID_OK)                
                self.button.SetDefault()
                self.isrecognize=False
                self.istranslate=False

                # Layout
                self.__DoLayout()
                self.SetInitialSize()

                # Bind Event  
                self.Bind(wx.EVT_BUTTON,self.OnDecide,self.button)                

        def __DoLayout(self):
                sizer=wx.GridBagSizer(vgap=8,hgap=8)                
                sizer.Add(self.checkbox1,(1,1))
                sizer.Add(self.checkbox2,(3,1))
                sizer.Add(wx.StaticText(self,-1,"Source Language:"),(1,2))
                sizer.Add(wx.StaticText(self,-1,"Target Language:"),(3,2))
                sizer.Add(self.recg_box,(1,3))
                sizer.Add(self.tran_box,(3,3))
                sizer.Add((1,4),(1,5))
                sizer.Add((3,4),(3,5))
                sizer.Add(self.button,(5,2))                
                self.SetSizer(sizer)

        
        def OnDecide(self,evt):
                self.sorcelan=self.recg_box.GetValue()
                self.targetlan=self.tran_box.GetValue()        
                if self.checkbox1.GetValue()==True:
                        self.isrecognize=True                
                if self.checkbox2.GetValue()==True:
                        self.istranslate=True
                self.Destroy()
                             
        
                
class FeedBackDialog(wx.Dialog):
        def __init__(self,parent,title=""):
                super(FeedBackDialog,self).__init__(parent,title=title)

                # Attributes
                self.mail=wx.TextCtrl(self)
                self.suggestion=wx.TextCtrl(self,style=wx.TE_MULTILINE)
                self.button=wx.Button(self,wx.ID_OK)
                self.button.SetDefault()

                # Layout
                self.__DoLayout()
                self.SetInitialSize()
                
        def __DoLayout(self):
                sizer = wx.GridBagSizer(vgap=8, hgap=8)
                mail_lbl = wx.StaticText(self, label="ContactMail:")
                suggestion_lbl = wx.StaticText(self, label="Suggestions:")
                # Add the event type fields
                sizer.Add(mail_lbl, (1, 1))
                sizer.Add(self.mail, (1, 2), (1, 15), wx.EXPAND)
                # Add the details field
                sizer.Add(suggestion_lbl, (2, 1))
                sizer.Add(self.suggestion, (2, 2), (5, 15), wx.EXPAND)
                # Add a spacer to pad out the right side
                sizer.Add((5, 5), (2, 17))
                # And another to the pad out the bottom
                sizer.Add((5, 5), (7, 0))
                sizer.Add(self.button,(7,7))
                self.SetSizer(sizer)
        def GetMail(self):
                return self.mail.GetValue()
        def GetSuggestion(self):
                return self.suggestion.GetValue()


