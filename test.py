import time
import subprocess  
import commands
import os
f = open('url.txt', 'r')
url = f.readline()[:-1]
while url != "":
	p = subprocess.Popen(['/home/wluo/chromium/tick/src/out/Default/chrome', '--remote-debugging-port=9222'],stdout=subprocess.PIPE)  
	print ("zhangxiaolei")
        print (url)
	time.sleep(5)
        print("****************node start********************************* ")
	#(status, output) = commands.getstatusoutput("node Hello.js https://" + url)
	#print(status, output)
	ti = subprocess.Popen(['node', 'Hello.js', 'https://'+url],stdout=subprocess.PIPE)
        print("****************node end*************************************")
	time.sleep(10)	
	#print ti.stdout.read();
	print ('nihao zhangxiaolei'+url)
	(status, output) = commands.getstatusoutput("kill -9 $(ps -ef | grep chrome | awk '{print $2}')")
	url = f.readline()

f.close()
