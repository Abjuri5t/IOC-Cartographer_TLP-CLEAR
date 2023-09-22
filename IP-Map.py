import sys
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import time


def getIPs(fileName):
	with open(fileName) as thisFile:
		allLines = [thisLine.rstrip() for thisLine in thisFile]
	
	validated = []
	for item in allLines:
		if(validIP(item)):
			validated.append(item)
		else:
			raise Exception("Invalid item \""+item+"\" in file. Please make sure input file is a list of IPv4 addresses (see example-IPs.list).")
	return validated


def validIP(potIP):
	isIP = True
	if((len(potIP) >= 7) and (len(potIP) <= 16)):
		if(potIP.count('.') == 3):
			octets = potIP.split('.')
			for octet in octets:
				if(octet.isnumeric()):
					value = int(octet)
					if((value < 0) and (value > 255)):
						isIP = False
				else:
					isIP = False
		else:
			isIP = False
	else:
		isIP = False
	return isIP


def parseSlash8s(addresses):
	slash8s = {}
	for q in range(256):
		cidr = str(q)+".0.0.0/8"
		slash8s[cidr] = 0
	
	for ip in addresses:
		firstOctet = ip.split('.')[0]
		cidr = firstOctet+".0.0.0/8"
		slash8s[cidr] = slash8s[cidr]+1
	
	return slash8s


def drawMap(legend, colorWeight):
	bSize = 48
	gap = 3
	dimension = 819
	black = (0,0,0)
	white = (255,255,255)
	numFont = PIL.ImageFont.truetype(".LiberationSansNarrow-Regular.ttf",18)
	# LiberationSans-Regular
	img = PIL.Image.new(mode="RGB",size=(dimension,dimension),color=black)
	d = PIL.ImageDraw.Draw(img)
	
	rows = [
		["0", "1", "14","15", "16", "19", "20", "21","234","235","236","239","240","241","254","255"]
		["3", "2", "13","12", "17", "18", "23", "22","233","232","237","238","243","242","253","252"]
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
			slash8 = rows[y][x]+".0.0.0/8"
			redness = 255 - int(legend[slash8] * colorWeight)
			xCor = (x*bSize)+((x+1)*gap)
			d.rectangle((xCor,yCor,xCor+bSize,yCor+bSize),fill=(255,redness,redness))
			d.text((xCor+6,yCor+3),rows[y]	[x],fill=black,font=numFont)
	writeTime = int(time.time())
	fName = "mapped-IPs_"+str(writeTime)+".jpg"
	img.save(fName)
	return fName


allIPs = getIPs(sys.argv[1])
weight = 1
if(len(sys.argv) > 2):
	weight = float(sys.argv[2])
else:
	print("No color weight provided. Using default weight of 1")
uniqueIPs = list(set(allIPs))
print(str(len(uniqueIPs))+" unique IPv4 addresses")
slash8s = parseSlash8s(uniqueIPs)
mapName = drawMap(slash8s, weight)
print("IP Map successfully written to "+mapName)
