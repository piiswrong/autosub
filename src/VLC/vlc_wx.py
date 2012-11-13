# import external libraries
import wx # 2.8
import wx.lib.platebtn as pbtn
import sys
import myvlc.vlc as vlc

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
                self.icon=wx.Icon('./VLC/autosub.ico',wx.wx.BITMAP_TYPE_ICO);
                self.SetIcon(self.icon);
                self.file_menu=wx.Menu()
                self.file_menu.Append(1,"&Open \tCtrl+O")
                self.file_menu.AppendSeparator()
                self.file_menu.Append(2,"&Close \tCtrl+C")
                self.Bind(wx.EVT_MENU, self.OnOpen, id=1)
                self.Bind(wx.EVT_MENU, self.OnExit, id=2)
                self.frame_menubar.Append(self.file_menu, "&File")


                #  Edit Menu
                self.edit_menu=wx.Menu()
                self.edit_menu.Append(3,"&Play \tCtrl+P")
                self.edit_menu.AppendSeparator()
                self.edit_menu.Append(4,"P&ause \tCtrl+A")
                self.edit_menu.AppendSeparator()
                self.edit_menu.Append(5,"&Stop \tCtrl+S")
                self.edit_menu.AppendSeparator()
                self.edit_menu.Append(6,"&FullScreen \tCtrl+F")
                self.edit_menu.AppendSeparator()
                self.edit_menu.Append(7,"&Volume \tCtrl+V")
                self.edit_menu.AppendSeparator()

                self.Bind(wx.EVT_MENU, self.OnPlay, id=3);
                self.Bind(wx.EVT_MENU, self.OnPause, id=4);
                self.Bind(wx.EVT_MENU, self.OnStop, id=5);
                self.Bind(wx.EVT_MENU, self.OnToggleFullScreen, id=6);
                self.Bind(wx.EVT_MENU, self.OnToggleVolume, id=7);
                self.frame_menubar.Append(self.edit_menu, "&Edit")

                #  Audio Menu
                self.audio_menu=wx.Menu()
                self.audio_menu.Append(-1,"NULL")
                self.audio_menu.AppendSeparator()
                self.audio_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.audio_menu, "Audio")

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
                self.help_menu.Append(-1,"NULL")
                self.help_menu.AppendSeparator()
                self.help_menu.Append(-1,"NULL")
                self.frame_menubar.Append(self.help_menu, "Help")


                self.SetMenuBar(self.frame_menubar)
 
                #Panels
                # This is the subtitlepanel
                self.subtitlepanel=wx.Panel(self, -1);
                # The first panel of the video
                self.videopanel = wx.Panel(self, -1)
                self.videopanel.SetBackgroundColour(wx.BLACK)

                # The second panel holds controls
                ctrlpanel = wx.Panel(self, -1 )
                self.timeslider = wx.Slider(ctrlpanel, -1, 0, 0, 1000,size=(500,20)) #timeline
                self.timeslider.SetRange(0, 1000)
                self.buffergauge = wx.Gauge(ctrlpanel, -1,1000,size=(500,10)) 
                self.buffergauge.SetRange(1000)
                                                                          
                self.displaytime=wx.StaticText(ctrlpanel, -1, "00:00/00:00", size=(10,15))
                self.buffertime=wx.StaticText(ctrlpanel, -1, "00:00/00:00", size=(10,15))
                
                pause  = pbtn.PlateButton(ctrlpanel, label="Pause")
                play   = pbtn.PlateButton(ctrlpanel, label="Play")
                stop   = pbtn.PlateButton(ctrlpanel, label="Stop")
                volume = pbtn.PlateButton(ctrlpanel, label="Volume")        
                fullscreen = pbtn.PlateButton(ctrlpanel, label="FullScreen")
                self.volslider = wx.Slider(ctrlpanel, -1, 0, 0, 100, size=(100, -1))

                self.feedback=pbtn.PlateButton(ctrlpanel,label="Feedback")


                # Add the picture to the button
                feedbackbmp=wx.Bitmap("./VLC/smile.gif",wx.BITMAP_TYPE_GIF)
                feedbackbmp.SetSize(size=(15,15))
                self.feedback.SetBitmap(bmp=feedbackbmp)


                
                ''' this is the Subtitle Editor'''
                # pos=wx.Frame.GetPosition();

                
                """Bind Control to Events"""
                self.Bind(wx.EVT_BUTTON, self.OnPlay, play)
                self.Bind(wx.EVT_BUTTON, self.OnPause, pause)
                self.Bind(wx.EVT_BUTTON, self.OnStop, stop)
                self.Bind(wx.EVT_BUTTON, self.OnToggleVolume, volume)
                self.Bind(wx.EVT_SLIDER, self.OnSetVolume, self.volslider)
                self.Bind(wx.EVT_SLIDER, self.OnSetPlayTime, self.timeslider)
                self.Bind(wx.EVT_BUTTON, self.OnToggleFullScreen, fullscreen)
                self.Bind(wx.EVT_BUTTON, self.OnFeedBack, self.feedback)


                # Give a pretty layout to the controls
                ctrlbox = wx.BoxSizer(wx.VERTICAL)
                box1 = wx.BoxSizer(wx.HORIZONTAL)
                box2 = wx.BoxSizer(wx.HORIZONTAL)
                box3 = wx.BoxSizer(wx.HORIZONTAL)
                box4 = wx.BoxSizer(wx.HORIZONTAL)
                box5 = wx.BoxSizer(wx.HORIZONTAL)
                # box1 contains the timeslider         
                box1.Add(self.timeslider,1)
                # box2 contains the bufferslider
                box2.Add(self.buffergauge,1)
                # box3 contains some buttons and the volume controls
                box3.Add(play, flag=wx.RIGHT, border=5)
                box3.Add(pause,flag=wx.RIGHT,border=5)
                box3.Add(stop,flag=wx.RIGHT,border=5)
                box3.Add((-1, -1), 1)
                box3.Add(self.feedback,flag=wx.RIGHT,border=3)
                box3.Add(fullscreen,flag=wx.RIGHT,border=5)
                box3.Add(volume,flag=wx.RIGHT,border=5)
                box3.Add(self.volslider, flag=wx.TOP | wx.LEFT, border=5)

                # box4 contains the playtime
                box4.Add(self.displaytime,1)
                # box5 contains the buffertime
                box5.Add(self.buffertime, 1)

                
                # Merge box to the ctrlsizer
                ctrlbox.Add(box4, flag=wx.EXPAND | wx.BOTTOM, border=0)
                
                ctrlbox.Add(box1, flag=wx.EXPAND | wx.BOTTOM, border=0)
                ctrlbox.Add(box5, flag=wx.EXPAND | wx.BOTTOM, border=0)
                ctrlbox.Add(box2, flag=wx.EXPAND | wx.BOTTOM, border=5)

                
                ctrlbox.Add(box3, 1, wx.EXPAND)
                ctrlpanel.SetSizer(ctrlbox)
                # Put everything togheter
                sizer = wx.BoxSizer(wx.VERTICAL)


                BigSizer = wx.BoxSizer(wx.HORIZONTAL)

                sizer.Add(self.videopanel, 1, flag=wx.EXPAND)
                sizer.Add(ctrlpanel, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)
                sizer.SetMinSize((400, 400))
                subsizer=wx.BoxSizer(wx.VERTICAL);
                subsizer.SetMinSize((400,400));
                BigSizer.Add(sizer,flag=wx.EXPAND)

                ####################################CUTTING LINE######################################
                
                splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)

                # subpanelf=wx.Panel(self,-1);
                # BigSizer.Add(subpanelf,flag=wx.EXPAND|wx.RIGHT);
                ####################################END Here##########################################
                subpanel=Subtitle(self,-1);
                subpanel.SetSizer(subsizer);
                BigSizer.Add(splitter,flag=wx.EXPAND)
                BigSizer.Add(subpanel,flag=wx.EXPAND|wx.RIGHT);
                BigSizer.SetMinSize((900, 400))

                self.SetSizer(BigSizer)
                self.SetMinSize((900, 400))

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

                # update the buffertime
                
                # update the bufferslder
                self.OnSetBuffer(None)
                # update the subtitle
                

        def OnToggleVolume(self, evt):
                """Mute/Unmute according to the audio button.
                """
                is_mute = self.player.audio_get_mute()

                self.player.audio_set_mute(not is_mute)
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


class SelectDialog(wx.Dialog):
        def __init__(self,parent,title=""):
                super(SelectDialog,self).__init__(parent,title=title)

                # Attributes
                self.notrecg_radio=wx.RadioButton(self,label="Not Need Recognized",style=wx.RB_GROUP)
                self.isrecg_radio=wx.RadioButton(self,label="Need Recognized")
                self.nottran_radio=wx.RadioButton(self,label="Not Need Translation",style=wx.RB_GROUP)
                self.istran_radio=wx.RadioButton(self,label="Need Translation")
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
                sizer.Add(wx.StaticText(self, label="Recognization:"),(1,0))
                sizer.Add(self.isrecg_radio,(1,3))
                sizer.Add(self.notrecg_radio,(1,1))
                sizer.Add(wx.StaticText(self, label="Translation:"),(3,0))
                sizer.Add(self.istran_radio,(3,3))
                sizer.Add(self.nottran_radio,(3,1))
                sizer.Add(self.recg_box,(1,4))
                sizer.Add(self.tran_box,(3,4))
                sizer.Add((1,2),(3,2))
                sizer.Add(self.button,(5,2))                
                self.SetSizer(sizer)

        
        def OnDecide(self,evt):
                self.sorcelan=self.recg_box.GetValue()
                self.targetlan=self.tran_box.GetValue()        
                if self.isrecg_radio.GetValue()==True:
                        self.isrecognize=True                
                if self.istran_radio.GetValue()==True:
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

