import sys
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import time

firstOctet = "-1"


def getIPsSlash16(fileName):
	with open(fileName) as thisFile:
		allLines = [thisLine.rstrip() for thisLine in thisFile]
	
	validated = []
	for item in allLines:
		if(applicableIPSlash16(item)):
			validated.append(item)
	return validated


def applicableIPSlash16(potIP):
	isApplicableIP = True
	if((len(potIP) >= 7) and (len(potIP) <= 16)):
		if(potIP.count('.') == 3):
			octets = potIP.split('.')
			if(octets[0] == firstOctet):
				for octet in octets[1:]:
					if(octet.isnumeric()):
						value = int(octet)
						if((value < 0) and (value > 255)):
							isApplicableIP = False
					else:
						isApplicableIP = False
			else:
				isApplicableIP = False
		else:
			isApplicableIP = False
	else:
		isApplicableIP = False
	return isApplicableIP


def parseSlash16sSlash16(addresses):
	slash16s = {}
	for q in range(256):
		cidr = firstOctet+'.'+str(q)+".0.0/16"
		slash16s[cidr] = 0
	
	for ip in addresses:
		secondOctet = ip.split('.')[1]
		cidr = firstOctet+'.'+secondOctet+".0.0/16"
		slash16s[cidr] = slash16s[cidr]+1
	
	return slash16s


def drawMapSlash16(legend):
	bSize = 48
	gap = 3
	dimension = 819
	black = (0,0,0)
	white = (255,255,255)
	numFont = PIL.ImageFont.truetype(".LiberationSansNarrow-Regular.ttf",15)
	# LiberationSans-Regular
	img = PIL.Image.new(mode="RGB",size=(dimension,dimension),color=black)
	d = PIL.ImageDraw.Draw(img)
	
	rows = [
		["0", "1", "14","15", "16", "19", "20", "21","234","235","236","239","240","241","254","255"],
		["3", "2", "13","12", "17", "18", "23", "22","233","232","237","238","243","242","253","252"],
		["4", "7",  "8","11", "30", "29", "24", "25","230","231","226","225","244","247","248","251"],
		["5", "6",  "9","10", "31", "28", "27", "26","229","228","227","224","245","246","249","250"],
		["58","57","54","53", "32", "35", "36", "37","218","219","220","223","202","201","198","197"],
		["59","56","55","52", "33", "34", "39", "38","217","216","221","222","203","200","199","196"],
		["60","61","50","51", "46", "45", "40", "41","214","215","210","209","204","205","194","195"],
		["63","62","49","48", "47", "44", "43", "42","213","212","211","208","207","206","193","192"],
		["64","67","68","69","122","123","124","127","128","131","132","133","186","187","188","191"],
		["65","66","71","70","121","120","125","126","129","130","135","134","185","184","189","190"],
		["78","77","72","73","118","119","114","113","142","141","136","137","182","183","178","177"],
		["79","76","75","74","117","116","115","112","143","140","139","138","181","180","179","176"],
		["80","81","94","95", "96", "97","110","111","144","145","158","159","160","161","174","175"],
		["83","82","93","92", "99", "98","109","108","147","146","157","156","163","162","173","172"],
		["84","87","88","91","100","103","104","107","148","151","152","155","164","167","168","171"],
		["85","86","89","90","101","102","105","106","149","150","153","154","165","166","169","170"]
	]
	
	# draw grid
	for y in range(16):
		yCor = (y*bSize)+((y+1)*gap)
		for x in range(16):
			slash16 = firstOctet+'.'+rows[y][x]+".0.0/16"
			redness = 255 - legend[slash16]
			xCor = (x*bSize)+((x+1)*gap)
			d.rectangle((xCor,yCor,xCor+bSize,yCor+bSize),fill=(255,redness,redness))
			d.text((xCor+3,yCor+2),firstOctet+'.'+rows[y][x],fill=black,font=numFont)
	writeTime = int(time.time())
	fName = "Slash-16_mapped-IPs_"+str(writeTime)+".jpg"
	img.save(fName)
	return fName


firstOctet = sys.argv[2]
allIPs = getIPsSlash16(sys.argv[1])
applicableIPs = list(set(allIPs))
print(str(len(applicableIPs))+" applicable IPv4 addresses of "+firstOctet+".0.0.0/8")
slash16s = parseSlash16sSlash16(applicableIPs)
print(slash16s)
mapName = drawMapSlash16(slash16s)
print("IP Map successfully written to "+mapName)
