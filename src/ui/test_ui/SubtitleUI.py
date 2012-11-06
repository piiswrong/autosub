# -*- coding: utf-8 -*- 
import wx
import wx.grid
import  wx.py.images as images


class LineTable(wx.grid.PyGridTableBase):
    rowLabels = ["uno", "dos", "tres", "quatro", "cinco"]
    colLabels = ["homer", "marge", "bart", "lisa", "maggie"]
    def __init__(self):
        wx.Frame.__init__(self,None,title="Grid Headers",
            size=(500,200))
        grid = wx.grid.Grid(self)
        grid.CreateGrid(5,5)
        for row in range(5):
            #1 start
            grid.SetRowLabelValue(row,self.rowLabels[row])
            grid.SetColLabelValue(row,self.colLabels[row])
            #1 end
        for col in range(5):
            grid.SetCellValue(row,col,
                "(%s,%s)" % (self.rowLabels[row], self.colLabels[col]))
    def GetNumberRows(self):
        return len(self.entries)

    def GetNumberCols(self):
        return 4

    def GetColLabelValue(self, col):
        return self.colLabels[col] #读列标签

    def GetRowLabelValue(self, col):
        return self.entries[row].pos #3 读行标签

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        entry = self.entries[row]
        return getattr(entry, self.colAttrs[col]) #4读属性值

    def SetValue(self, row, col, value):
        pass

class TestFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, title="Grid Headers",
            size=(500,200))
        grid = wx.grid.Grid(self)
        grid.CreateGrid(5,5)
        for row in range(5):
            #1 start
            grid.SetColLabelValue(row, self.colLabels[row])
            #1 end
        grid.AppendRows();
                
        # panel=wx.Panel(self)
        # panel.SetBackgroundColour('White')
        # statusbar=self.CreateStatusBar()
        # # toolbar=self.CreateToolBar()
        # # toolbar.AddSimpleTool(wx.NewId(),images.getPyBitmap(),
        # #       "New","Long help for 'New'")
        # # toolbar.Realize()
        # menuBar = wx.MenuBar()
        # menu1=wx.Menu()
        # menu1.Append(wx.NewId(),u"新字幕",u"新建一个字幕")
        # menu1.Append(wx.NewId(),u"打开字幕",u"打开一个字幕")
        # menu1.Append(wx.NewId(),u"保存字幕",u"保存一个字幕")
        # menuBar.Append(menu1,u"文件")
        # menu2=wx.Menu()
        # menu2.Append(wx.NewId(),u"撤销","Copy in status bar")
        # menu2.Append(wx.NewId(),u"复制","ctrl+c")
        # menu2.Append(wx.NewId(),u"粘贴","ctrl+v")
        # menu2.AppendSeparator()
        # menu2.Append(wx.NewId(),u"显示选项","Display Options")
        # menuBar.Append(menu2, u"编辑")
        # self.SetMenuBar(menuBar)
        # # print wx.grid.Grid.__doc__
        # grid = wx.grid.Grid(self)
        # box = wx.BoxSizer(wx.HORIZONTAL)
        # box.Add(grid,0,wx.EXPAND)

        # grid.CreateGrid(5,5)
        # # print grid.CreateGrid.__doc__
        # for row in range(5):
        #     for col in range(5):
        #         grid.SetCellValue(row, col, "(%s,%s)" % (row, col))

        # grid.SetCellTextColour(1, 1, "red")
        # grid.SetCellFont(1,1, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        # grid.SetCellBackgroundColour(2, 2, "light blue")
        
        # attr = wx.grid.GridCellAttr()
        # attr.SetTextColour("navyblue")
        # attr.SetBackgroundColour("pink")
        # attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        # grid.SetAttr(4, 0, attr)
        # grid.SetAttr(5, 1, attr)
        # grid.SetRowAttr(8, attr)


# app = wx.PySimpleApp()
# frame = TestFrame()
# frame.Show()
# app.MainLoop()