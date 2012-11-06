''' Subtitles'''

class Subtitles():
	"""docstring for subtitles"""
	number=0;
	starttime="";
	endtime="";
	content="";
	def __init__(self):
		pass
	def settime(self,start,end):
		self.starttime=start;
		self.endtime=end;
	def set(self,thing):
		self.content=thing;


		
		