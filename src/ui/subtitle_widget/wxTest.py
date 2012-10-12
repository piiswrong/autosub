# # -*- coding: utf-8 -*- 
# # import wx
# # class MyFrame(wx.Frame):
# # 	"""docstring for MyFrame"""
# # 	def __init__(self):
# # 		wx.Frame.__init__(self,None,-1,"My Frame", size=(300,300))
# # 		panel=wx.Panel(self,-1)
# # 		panel.Bind(wx.EVT_MOTION,self.OnMove)
# # 		wx.StaticText(panel,-1,"Pos:",pos=(10,12))
# # 		self.posCtrl=wx.TextCtrl(panel,-1,"",pos=(40,10))
# # 	def OnMove():
# # 			pos=event.GetPosition()
# # 			self.posCtrl.SetValue("%s, %s" % (pos.x,pos.y))

# # if __name__=='__main__' :
# # 	app=wx.PySimpleApp()
# # 	frame=MyFrame()
# # 	frame.Show(True)
# # 	app.MainLoop()
# # ss=raw_input();
# import 	wx
# import 	wx.grid 
# # import 	wx.py.images as images
# # class Frame(wx.Frame):
# # 	def __init__(self,image,parent=None,id=-1,
# # 			pos=wx.DefaultPosition,
# # 			title='Hello, wxPython!'):
# # 		temp=image.ConvertToBitmap()
# # 		size=temp.GetWidth(),temp.GetHeight();
# # 		wx.Frame.__init__(self,parent,id,title,pos,size)
# # 		self.bmp=wx.StaticBitmap(parent=self,bitmap=temp)





# # class App(wx.App):
# # 	"""doc string for  nothing"""
# # 	def OnInit(self):
# # 		image=wx.Image('C:\\Users\\v-liason\\Pictures\\Alienware\\AW1.jpg',wx.BITMAP_TYPE_JPEG)
# # 		self.frame=Frame(image)
# # 		self.frame.Show()
# # 		self.SetTopWindow(self.frame)
# # 		return True

# class ToolBarFrame(wx.Frame):
# 	"""docstring for ToolBarFrame"""
# 	def __init__(self):
# 		wx.Frame.__init__(self,None,id,title='Toolbars',
# 				size=(600,300))
# 		# self.Center()

# 		#grid 

# 		grid=wx.grid.Grid(self);
#         grid.CreateGrid(5,5);
#         for row in range(20):
#             for col in range(6):
#                 grid.SetCellValue(row, col,
#                 	"cell (%d,%d)" % (row, col))
# 		panel=wx.Panel(self)
# 		panel.SetBackgroundColour('White')
# 		statusbar=self.CreateStatusBar()
# 		toolbar=self.CreateToolBar()
# 		# toolbar.AddSimpleTool(wx.NewId(),images.getPyBitmap(),
# 		# 		"New","Long help for 'New'")
# 		toolbar.Realize()
# 		menuBar = wx.MenuBar()
# 		menu1=wx.Menu()
# 		menu1.Append(wx.NewId(),u"新字幕",u"新建一个字幕")
# 		menu1.Append(wx.NewId(),u"打开字幕",u"打开一个字幕")
# 		menu1.Append(wx.NewId(),u"保存字幕",u"保存一个字幕")
# 		menuBar.Append(menu1,u"文件")
# 		menu2=wx.Menu()
# 		menu2.Append(wx.NewId()," ","Copy in status bar")
# 		menu2.Append(wx.NewId(),"C ","")
# 		menu2.Append(wx.NewId(),"Paste","")
# 		menu2.AppendSeparator()
# 		menu2.Append(wx.NewId()," ","Display Options")
# 		menuBar.Append(menu2, u"编辑")
# 		self.SetMenuBar(menuBar)
       

# def main():
# 	app=App()
# 	app.MainLoop()

# def PopaSingleChoiceDialog():
# 	dlg=wx.SingleChoiceDialog(None,'Which version of Python are you using?',
# 					'Single Choice',['1.0','2.2','2.7','3.2'])
# 	if(dlg.ShowModal()==mx.ID_OK):
# 		response=dlg.GetStringSelection()

# if __name__=='__main__':
# 	app=wx.PySimpleApp()
# 	frame=ToolBarFrame()
# 	frame.Show()
# 	app.MainLoop()
# -*- coding: utf-8 -*-

# absolute.py

import wx
from SubtitleUI import TestFrame
class Example(wx.Frame):
    colLabels = ["homer", "marge", "bart", "lisa", "maggie"]
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(280, 300))
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):
    
        panel = wx.Panel(self, -1)
        self.TextCtrl=wx.TextCtrl(panel, pos=(3, 3), size=(250, 100))
        samplelist=['zero|ds','one |ds','two','three','four','five','six','seven','eight','nine','ten']
        self.listBox=wx.ListBox(panel,-1,(0,120),(250,120),samplelist,wx.LB_SINGLE)
        self.listBox.SetSelection(1)
        menubar = wx.MenuBar()
        filem = wx.Menu()
        editm = wx.Menu()
        helpm = wx.Menu()
        menubar.Append(filem, '&File')
        menubar.Append(editm, '&Edit')
        menubar.Append(helpm, '&Help')
        filem.Append(wx.NewId(),u"Open","Open a File")
        self.Bind(wx.EVT_LISTBOX_DCLICK,self.ChooseOneItem,self.listBox);
        self.SetMenuBar(menubar)
        statusbar=self.CreateStatusBar()
        # hbox.Add(frid, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
    def ChooseOneItem(self,event):
    	index=self.listBox.GetSelection()
    	self.TextCtrl.SetValue(self.listBox.GetString(index))
    	
        


if __name__ == '__main__':
	app = wx.App()
	Example(None, title='')
	app.MainLoop()