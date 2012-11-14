# -*- coding: cp936 -*-
import wx
from pylab import *

import core.ffmpeg_decoder as fd
import core.spectrum as sp
import matplotlib.pyplot as plt
import numpy as np
import RulerCtrl as RC

import matplotlib.cm as cm

dec = fd.ffmpeg_decoder('../data/demo.mp4')
spec = sp.spectrum(dec.ostream.get_handle())
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
        #vector = vector/np.amax(vector) * 255.0
        vector = vector * 10
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
        



class ImageWindow(wx.ScrolledWindow):


    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.SetScrollRate(5,5)
        self.LeftClickFlag=0
        self.RightClickFlag=0
        self.ScrollFlag=1
        #self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.OnScroll
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.overlay=wx.Overlay()
        #ruler=RC.RulerCtrl(self, -1, pos=(0, np.size(specW, axis=0)), size=(np.size(specW , axis = 1),1),orient=wx.HORIZONTAL, style=wx.NO_BORDER)
        #ruler.SetFlip(flip=True)
        #ruler.SetRange(0, np.size(specW , axis = 1))

    def SetBitmap(self, bitmap):
        self.bitmap = bitmap
        self.buffer = wx.EmptyBitmap(bitmap.GetWidth(), bitmap.GetHeight()+15)
        
        
    def OnPaint(self, event):
        #dc = wx.BufferedPaintDC(self, self.bitmap)
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        dc.DrawBitmap(self.bitmap, 0, 0)
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
                #rect = wx.Rect(x, 0, width, height)
                pdc = wx.GCDC(dc)
                pdc.SetBrush(brush)
                pdc.DrawRectangle(x, 0, width, height)
        del odc
        dc.SetPen(wx.Pen('white',1))
        dc.SetTextForeground('white')
        for i in range(-self.CalcScrolledPosition(0,0)[0], self.bitmap.GetWidth(), 10):
                dc.DrawLine(i, self.bitmap.GetHeight(), i, self.bitmap.GetHeight()+5)
                font = wx.Font(7, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
                dc.SetFont(font)
                dc.DrawText(str(i), i, self.bitmap.GetHeight()+5)
        event.Skip()
            
    def OnScroll(self, evt):
        self.ScrollFlag = 1
        evt.Skip()

    def OnMouseClick(self, event):
        #print event.GetLogicalPosition(self.cdc)
        self.LeftClickFlag = 1
        self.LeX=event.X -self.CalcScrolledPosition(0,0)[0]
        self.Refresh()
        #self.CaptureMouse()
        #del odc
        event.Skip()

    def OnRightClick(self, event):
        self.RightClickFlag = 1
        self.RiX=event.X - self.CalcScrolledPosition(0,0)[0]
        self.Refresh()
        event.Skip()
            
class Panel1(wx.Frame):
    def __init__(self):

        wx.Frame.__init__(self, None, -1, ' spectrum widget')
        self.orim = wx.ImageFromBuffer(int(np.size(specW , axis = 1)), int(np.size(specW, axis = 0)), np.uint8(specW))
        #self.orim = Image.fromarray(specW)
        self.im = self.orim
        self.bm = self.im.ConvertToBitmap()
        self.wind = ImageWindow(self)

        panel = wx.Panel(self, -1)
        
        self.sld = wx.Slider(panel, value = 200, minValue = 150, maxValue =500,pos = (10,10),
                        size=(55, 150), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.sld.SetTickFreq(20, 1)
        self.sld1 = wx.Slider(panel, value = 200, minValue = 150, maxValue =500,pos = (70,10),
                        size=(50, 150), style=wx.SL_VERTICAL| wx.SL_AUTOTICKS | wx.SL_LABELS )
        self.sld1.SetTickFreq(20, 1)


        #ADD TWO BUTTONS TO MANIPULATE THE LEFT AND RIGHT BORDER
        self.button1 = wx.Button(panel, id=1, label='left', pos = (120,10), size = (70,25))
        self.button2 = wx.Button(panel, id=2, label='right', pos=(120, 40), size = (70,25))
        self.button1.Bind(wx.EVT_BUTTON, self.LeftButton)
        self.button2.Bind(wx.EVT_BUTTON, self.RightButton)
        
        self.wind.SetSize((300,150))
        self.wind.SetBitmap(self.im.ConvertToBitmap())
        wx.EVT_SLIDER(self.sld, self.sld.GetId(),self.sliderUpdate1)
        wx.EVT_SLIDER(self.sld1, self.sld1.GetId(),self.sliderUpdate2)
        self.wind.FitInside()
        self.wind.SetScrollbars(1,0, self.im.GetWidth(), 400)
        

        
        sizer = wx.BoxSizer ()
        sizer.Add(self.wind, 1, wx.EXPAND, 0)
        sizer.Add(panel, wx.ALIGN_LEFT)
        #sizer.Add(self.ruler)
        self.SetSizer(sizer)
        self.SetSize((500,200))
        #self.Fit()
        
    def sliderUpdate1(self, event):
        self.pos = self.sld.GetValue()
        #str = "pos = %f" % (self.pos/150.0)
        self.Refresh()
        self.orim = wx.ImageFromBuffer(int(np.size(specW , axis = 1)), int(np.size(specW, axis = 0)), np.uint8(specW))
        NWID = round(self.bm.GetWidth() * self.pos/200.0)
        NHET = round(self.im.GetHeight())
        self.im = self.orim.Rescale(NWID ,NHET)
        self.wind.SetBitmap(self.im.ConvertToBitmap())

    def sliderUpdate2(self, event):
        pass

    def LeftButton(self, event):
        self.wind.LeX = self.wind.LeX -1
        self.wind.Refresh()
        event.Skip()

    def RightButton(self, event):
        self.wind.RiX = self.wind.RiX +1
        self.wind.Refresh()
        event.Skip()

if __name__=='__main__':
    app = wx.PySimpleApp()
    f = Panel1()
    f.Show()
    app.MainLoop()
        
