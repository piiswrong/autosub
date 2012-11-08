#coding = utf-8 
import re
# import chardet
import codecs
# def AssParser(url):
# 	myf=open(url,'r');

# def GetTheEncoding(content):
# 	# myf=open(url,'r');
# 	# # print myf.read();
# 	# cont=myf.read();
# 	char=chardet.detect(content)
# 	return char['encoding'];
def AssParser(url):
	myf=open(url,'r');
	# print myf.read();
	cont=myf.read();
	dec=GetTheEncoding(cont)
	p=re.compile("Dialogue: [^\n]*");
	j=p.findall(cont);
	li=[];
	count=0;
	for i in j:
		tmp=i.split(',')
		count=count+1;
		nsub=[]
		len(tmp);
		title="";
		for d in range(9,len(tmp)):
			title=title+tmp[d];
		nsub.append(count)
		nsub.append(tmp[1])
		nsub.append(tmp[2]);
		nsub.append(title)
		# print nsub
		li.append(nsub)
	return li;
def SrtParser(url):
	myf=open(url,'r');
	# print myf.read();
	cont=myf.read()
	dec=GetTheEncoding(cont)
	allitem=cont.split('\n')
	li=[];
	ct=0;
	for i in range(0,len(allitem)/4):
		nsub=[];
		
		tmp=allitem[i*4+1];
		tmp=tmp.split(' ');
		# print tmp;
		nsub.append(allitem[i*4]);
		nsub.append(tmp[0].replace(',','.'));
		if(len(tmp)>2):
			nsub.append(tmp[2].replace(',','.'));
			nsub.append(allitem[i*4+2])
		# print nsub
		li.append(nsub);
	return li;
	# print allitem

def ShowItems(li):
	for i in li:
		print str(i.number)+' '+i.starttime+' '+i.endtime+' '+i.content;



# ShowItems(srt);
	

