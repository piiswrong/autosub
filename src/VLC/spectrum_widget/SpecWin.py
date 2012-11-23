# -*- coding: cp936 -*-
import wx
from pylab import *

import core.ffmpeg_decoder as fd
import core.spectrum as sp
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.cm as cm



class ImageWindow(wx.ScrolledWindow):


    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(5,5)
        self.LeftClickFlag=0
        self.RightClickFlag=0
        self.CurrPos=0
        #self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnScroll)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        #ADD MOUSE DRAG EVENT TO REPLACE SCROLLING
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.timer = wx.Timer(self)
        self.timer.Start(100)
        self.overlay=wx.Overlay()
        #ruler=RC.RulerCtrl(self, -1, pos=(0, np.size(specW, axis=0)), size=(np.size(specW , axis = 1),1),orient=wx.HORIZONTAL, style=wx.NO_BORDER)
        #ruler.SetFlip(flip=True)
        #ruler.SetRange(0, np.size(specW , axis = 1))

    def SetBitmap(self, bitmap):
        self.bitmap = bitmap
        #self.buffer = wx.EmptyBitmap(bitmap.GetWidth(), bitmap.GetHeight()+15)
        self.buffer = self.bitmap
        self.SetScrollbars(1,0, self.bitmap.GetWidth(), 200)


    def OnPaint(self, event):
        #dc = wx.BufferedPaintDC(self, self.bitmap)
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        #dc.DrawBitmap(self.bitmap, 0, 0)
        odc=wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        if self.LeftClickFlag==1:
            dc.SetPen(wx.Pen('red', 1))
            dc.DrawLine(self.LeX,0,
                        self.LeX, 150)
        if self.RightClickFlag==1:
            dc.SetPen(wx.Pen('blue',1))
            dc.DrawLine(self.RiX,0,
                        self.RiX, 150)
        #Draw a transparent rectangle to emphasize the selected area
        if(self.LeftClickFlag == 1 and self.RightClickFlag == 1 and self.LeX!=self.RiX):
            Colour = wx.Colour(139, 0, 255, 100) #notice the alpha channel
            brush = wx.Brush(Colour)
            if self.RiX > self.LeX:
                width = self.RiX - self.LeX
                x = self.LeX
            else:
                width = self.LeX- self.RiX
                x = self.RiX
            height  = self.bitmap.GetHeight()
            pdc = wx.GCDC(dc)
            pdc.SetBrush(brush)
            pdc.DrawRectangle(x, 0, width, height)
        dc.SetPen(wx.Pen('white',1))
        dc.DrawLine(-self.CalcScrolledPosition(0,0)[0] + 150, 0, -self.CalcScrolledPosition(0,0)[0] + 150, 150)
        dc.SetPen(wx.Pen('green',1))
        dc.DrawLine(self.CurrPos, 0, self.CurrPos, 150)
        del odc
        #SKIP THE DRAWING OF RULER WHICH SEVERELY STUCK THE RENDERING
        event.Skip()



    def OnMouseClick(self, event):
        #print event.GetLogicalPosition(self.cdc)
        self.LeftClickFlag = 1
        self.OLeX=event.X -self.CalcScrolledPosition(0,0)[0]
        self.LeX = self.OLeX
        self.Startx = self.LeX
        self.Refresh()
        #self.CaptureMouse()
        #del odc
        event.Skip()

    def OnLeftUp(self, event):
        self.Endx = event.X - self.CalcScrolledPosition(0,0)[0]
        if self.Endx != self.Startx:
            self.Scroll(-self.CalcScrolledPosition(0,0)[0] + self.Endx - self.Startx, 0)
        event.Skip()

    def OnRightClick(self, event):
        self.RightClickFlag = 1
        self.ORiX=event.X - self.CalcScrolledPosition(0,0)[0]
        self.RiX = self.ORiX
        self.Refresh()
        event.Skip()



class SimFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,None,-1,"Frame")
        self.panel=SpecPanel(self)
        self.SetSize((500,200))


class SpecPanel(wx.Panel):
    def __init__(self,parent):

        wx.Panel.__init__(self,parent,-1)
        self.specW=self.OpenData(self)
        #self.orim = Image.fromarray(specW)
        self.spec = self.specW*255.0
        #SET THE DEFAULT VALUE OF THE SLIDER POS
        self.pos = 200

        panel = wx.Panel(self, -1)

        self.ratio = 15.69565217391304

        self.sld = wx.Slider(panel, value = 200, minValue = 150, maxValue =500,pos = (0,10),
            size=(55, 150), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS, name='width')
        self.sld.SetTickFreq(20, 1)
        self.sld1 = wx.Slider(panel, value = 200, minValue = 150, maxValue =500,pos = (55,10),
            size=(55, 150), style=wx.SL_VERTICAL| wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.sld1.SetTickFreq(20, 1)

        self.Bind(wx.EVT_MENU, self.LeftButton, id=1)
        self.Bind(wx.EVT_MENU, self.RightButton, id=2)
        self.Bind(wx.EVT_MENU, self.LeftText, id=1)
        acceltbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('Z'),1),(wx.ACCEL_CTRL,ord('X'),2)])
        self.SetAcceleratorTable(acceltbl)

        #ADD TWO BUTTONS TO MANIPULATE THE LEFT AND RIGHT BORDER
        self.button1 = wx.Button(panel, id=1, label='left', pos = (115,5), size = (30,25))
        self.button2 = wx.Button(panel, id=2, label='right', pos=(150,5), size = (30,25))
        self.button1.Bind(wx.EVT_BUTTON, self.LeftButton)
        self.button2.Bind(wx.EVT_BUTTON, self.RightButton)
        self.button1.Bind(wx.EVT_BUTTON, self.LeftText)
        self.button2.Bind(wx.EVT_BUTTON, self.RightText)
        self.textleft = wx.TextCtrl(panel, id=3, pos=(115, 40), size=(70, 25))
        self.textright = wx.TextCtrl(panel, id=4, pos=(115, 70), size=(70, 25))
        self.textmid = wx.TextCtrl(panel, id=5, pos=(115, 100), size=(70,25))
        self.textcurr = wx.TextCtrl(panel, id=6, pos=(115, 130), size=(70,25))

        #IF THE SPEC_FLAG IS TRUE, SHOW THE SPEC, OTHERWISE DISPLAY THE EXAMPLE
        self.Spec_Flag = self.DisplaySpec(self)
        if self.Spec_Flag == 1:
            self.orim = wx.ImageFromBuffer(int(np.size(self.spec , axis = 1)), int(np.size(self.spec, axis = 0)), np.uint8(self.spec))
            self.orim = self.orim.Rescale(self.orim.GetWidth(), 140)
        else:
            self.orim = wx.Image('../Icons/speceg.jpg', wx.BITMAP_TYPE_JPEG)
        self.im = self.orim
        self.bm = self.im.ConvertToBitmap()


        self.wind = ImageWindow(self)
        self.wind.timer.Start(100)
        self.wind.SetBitmap(self.im.ConvertToBitmap())
        self.wind.SetScrollbars(1,0, self.im.GetWidth(), 200)
        wx.EVT_SLIDER(self.sld, self.sld.GetId(),self.sliderUpdate1)
        wx.EVT_SLIDER(self.sld1, self.sld1.GetId(),self.sliderUpdate2)
        #UPDATE THE TEXT ON LEFT CLICKING
        self.wind.Bind(wx.EVT_LEFT_UP, self.LeftText)
        self.wind.Bind(wx.EVT_RIGHT_UP, self.RightText)
        self.wind.Bind(wx.EVT_SCROLLWIN, self.MidText)
        self.sld1.Bind(wx.EVT_SLIDER, self.sliderUpdate2)
        self.wind.Bind(wx.EVT_TIMER, self.CurrText, self.wind.timer)
        self.wind.Bind(wx.EVT_TIMER, self.OnTimer, self.wind.timer)
        self.wind.FitInside()
        #self.wind.SetScrollbars(1,0, self.im.GetWidth(), 200)


        sizer = wx.BoxSizer (wx.HORIZONTAL)
        sizer.Add(self.wind, 1, wx.EXPAND, 0)
        sizer.Add(panel, wx.ALIGN_LEFT)
        #sizer.SetSize((500,200))
        #sizer.Add(self.ruler)
        self.SetSizer(sizer)
        self.SetSize((500,200))
        #self.Fit()

    def OpenData(self,event):
        file_wildcard = "All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "Open file...",
            os.getcwd(),
            style = wx.OPEN,
            wildcard = file_wildcard)
        if(dlg.ShowModal() == wx.ID_OK):
            self.addr=dlg.GetPath()
        dec = fd.ffmpeg_decoder(self.addr, output_rate = 8000)
        spec = sp.spectrum(dec.ostream.get_handle(), window_size = 1024)
        handle = spec.ostream.get_handle()

        dec.start()
        spec.start()
        Num = 0

        while handle.more_data():
            iter = 0
            q = []
            pos, n, q = handle.read(1000, q)
            for p in q:
                if iter == 0:
                    temp = p.T[::-1]
                    vector = np.log(temp + 1)
                else:
                    temp = p.T[::-1]
                    vector = np.append(vector, np.log(temp + 1), axis =1)
                iter = iter +1
                #plt.imshow(np.log(p.T+1))
                #plt.show()
            vector = vector/np.amax(vector)
            vector = [vector, vector, vector]
            vector = np.dstack(vector)
            #plt.imsave(path, vector, cmap = cm.gray)
            im = wx.ImageFromBuffer(int(np.size(vector, axis = 1)), int(np.size(vector, axis = 0)), np.uint8(vector))
            if Num == 0:
                specW = vector
                list = [vector]
            else:
                specW = np.append(specW, vector, axis = 1)
                list.append(vector)
            Num = Num + 1
        return specW


    def DisplaySpec(self, event):
        #RECEIVE A SIGNAL AS THE DISPLAY FLAG
        Spec_Flag = 1
        return Spec_Flag
    
    def sliderUpdate1(self, event):
        self.pos = self.sld.GetValue()
        self.wind.overlay.Reset()
        if self.Spec_Flag == 1:
            self.orim = wx.ImageFromBuffer(int(np.size(self.spec , axis = 1)), int(np.size(self.spec, axis = 0)), np.uint8(self.spec))
        else:
            self.orim = wx.Image('../Icons/speceg.jpg', wx.BITMAP_TYPE_JPEG)
        NWID = round(self.bm.GetWidth() * self.pos/200.0)
        NHET = round(self.im.GetHeight())
        self.im = self.orim.Rescale(NWID ,NHET)
        self.wind.SetBitmap(self.im.ConvertToBitmap())
        if self.wind.LeftClickFlag == 1:
            self.wind.LeX = self.wind.OLeX*self.pos/200.0
            self.LeftText(self)
        if self.wind.RightClickFlag == 1:
            self.wind.RiX = self.wind.ORiX*self.pos/200.0
            self.RightText(self)
        self.wind.Refresh()

    def sliderUpdate2(self, event):
        self.pos = self.sld1.GetValue()
        self.wind.Refresh()
        if self.Spec_Flag ==  1:
            self.wind.overlay.Reset()
            self.spec = self.specW*self.pos
            self.im = wx.ImageFromBuffer(int(np.size(self.spec, axis = 1)), int(np.size(self.spec, axis = 0)), np.uint8(self.spec))
            self.im=self.im.Rescale(self.im.GetWidth(), 140)
            self.wind.SetBitmap(self.im.ConvertToBitmap())
        else:
            pass


    def LeftButton(self, event):
        if self.wind.LeftClickFlag == 1:
            self.wind.LeX = self.wind.LeX -self.pos/200.0
            self.wind.Refresh()
        event.Skip()

    def RightButton(self, event):
        if self.wind.RightClickFlag == 1:
            self.wind.RiX = self.wind.RiX +self.pos/200.0
            self.wind.Refresh()
        event.Skip()

    def LeftText(self, event):
        self.textleft.Clear()
        if self.wind.LeftClickFlag ==1:
            time = self.wind.LeX * self.pos/200/self.ratio
            self.textleft.WriteText(str(int(time/60/60))+":"+str(int(time/60))+":"+str(int(time%60)) + ":"+str(int(((round(time, 2) - int(time))*100))))
        event.Skip()

    def RightText(self, event):
        self.textright.Clear()
        if self.wind.RightClickFlag==1:
            time = self.wind.RiX * self.pos/200/self.ratio
            self.textright.WriteText(str(int(time/60/60))+":"+str(int(time/60))+":"+str(int(time%60)) + ":"+str(int(((round(time, 2) - int(time))*100))))
        event.Skip()

    def MidText(self, event):
        self.textmid.Clear()
        time = (-self.wind.CalcScrolledPosition(0,0)[0] + 150)/self.ratio
        self.textmid.WriteText(str(int(time/60/60))+":"+str(int(time/60))+":"+str(int(time%60))+ ":"+str(int(((round(time, 2) - int(time))*100))))
        event.Skip()

    def CurrText(self, event):
        self.textcurr.Clear()
        time = (self.wind.CurrPos+50)/self.ratio
        self.textcurr.WriteText(str(int(time/60/60))+":"+str(int(time/60))+":"+str(int(time%60))+ ":"+str(int(((round(time, 2) - int(time))*100))))
        event.Skip()

    def OnTimer(self, event):
        self.wind.CurrPos = self.wind.CurrPos + 1.5
        self.Refresh()
        event.Skip()

if __name__=='__main__':
        app = wx.PySimpleApp()
        f = SimFrame()
        f.Show()
        app.MainLoop()

