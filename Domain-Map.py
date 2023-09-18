import sys
import re
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import time


def getDomains(fileName):
	with open(fileName) as thisFile:
		allLines = [thisLine.rstrip() for thisLine in thisFile]
	
	validated = []
	for item in allLines:
		if(validDomain(item)):
			validated.append(item)
		else:
			raise Exception("Invalid item \""+item+"\" in file. Please make sure input file is a list of IPv4 addresses (see example-IPs.list).")
	return validated


def validDomain(potDomain):
	if(potDomain == None): #if NoneType
		return False
	if(potDomain == ""): #if empty
		return False
	if(len(potDomain) > 253): #if potential domain is longer than maximum fully-qualified domain name
		return False
	domainRulesRegex = "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,18}$"
	ruleTest = re.compile(domainRulesRegex) #compiled regular expression
	return re.search(domainRulesRegex, potDomain)


def recurseDoms(forrest, splitDomain):
	currTop = splitDomain.pop()
	if currTop in forrest:
		subs = forrest[currTop]
		newCount = 1 + subs.get("#count")
		subs.update({"#count": newCount})
		forrest[currTop] = subs
		if(len(splitDomain) > 0):
			forrest[currTop] = recurseDoms(forrest[currTop], splitDomain)
	else:
		if(len(splitDomain) > 0):
			forrest[currTop] = recurseDoms({"#count":1}, splitDomain)
		else:
			forrest[currTop] = {"#count":1}
	return forrest


def parseTree(forrest, count, parent):
	topLevels = getLargest(forrest, count)
	topLevels = patternOnly(topLevels)
	branches = {}

	for topRec in topLevels:
		topName = topRec[0]
		topTree = forrest[topName]
		domainName = topName
		if(parent != ''):
			domainName = topName+'.'+parent
		branches[domainName] = parseTree(topTree, count*2, domainName)
		branches[domainName]["#count"] = topRec[1]

	if(parent != ''):
		excludedCnt = 0
		for k in forrest.keys():
			matched = False
			for topL in topLevels:
				if(k == topL[0]):
					matched = True
			if((matched == False) and (k != "#count")):
				excludedCnt = excludedCnt + forrest[k]["#count"]
		
		if(excludedCnt > 0):
			subsName = "*."+parent
			branches[subsName] = {}
			branches[subsName]["#count"] = excludedCnt
	return branches


def getLargest(forrest, topNum):
	countList = []
	for lvlName in forrest:
		if(lvlName != "#count"):
			lvlTree = forrest[lvlName]
			countList.append([lvlName, lvlTree["#count"]])
	countList = sorted(countList, key=lambda q: q[1], reverse=True)
	return countList[:topNum]


def patternOnly(raw):
	repeats = []
	for index in range(len(raw)):
		if(raw[index][1] > 2):
			repeats.append(raw[index])
	return repeats


def drawTree(forrest, total):
	assignedColors = assignTreeColors(128, list(forrest.keys()))
	gap = -1
	mult = 1
	while(gap < 0):
		size = 64*mult
		dimension = (size*16)+(int(size/4)*17)
		gap = calcGap(forrest, 0, dimension)
		if(gap < 0):
			mult = mult+1
	gray = (128,128,128)
	fontSize = int(size/2)
	domFont = PIL.ImageFont.truetype(".LiberationSansNarrow-Bold.ttf", fontSize)
	img = PIL.Image.new(mode="RGB",size=(dimension,dimension),color=gray)
	draw = PIL.ImageDraw.Draw(img)
	separate = 100*mult

	treeKeys = list(forrest.keys())
	x = int(dimension - separate)
	locations = {}
	for q in range(int(dimension/(separate*2))):
		currForrest = removeWild(getXlevel([forrest], q))
		gap = calcGap(currForrest, 0, dimension)
		y = 0
		width = (fontSize/2)*(getMaxChars(currForrest)+3)
		for treeName in currForrest.keys():
			if((treeName != "#count") and (x-width > 0)):
				y = y+gap
				thisColor = assignedColors[treeName.split('.')[-1]]
				dispName = "*."+treeName.split('.')[0]
				b = currForrest[treeName]["#count"]
				percent = int(100*(b/total))
				if(percent > 2):
					dispName = dispName+" - "+str(percent)+'%'
				if(treeName.count('.') > 0):
					parent = parseParent(treeName)
					draw.line((x+int(width/10),int(y+(b/2)), locations[parent][0],locations[parent][1]), fill=(0,0,0), width=mult)
				draw.rectangle([(x-width,y),(x+(width/10),y+b)], fill=thisColor, outline=thisColor)
				draw.text((x-(9*int(width/10)),(y-int(fontSize/2))+int(b/2)),dispName,fill=(255,255,255),font=domFont)
				locations[treeName] = [int(x-width),int(y+(b/2))]
				y = y+b
		x = (x - width) - separate
	writeTime = int(time.time())
	fName = "graphed-domains_"+str(writeTime)+".jpg"
	img.save(fName)
	
	return fName


def assignTreeColors(ltns, tlds):
	half = int(ltns/2)
	
	assigned = {}
	red=(ltns,0,0)
	assigned[tlds[0]] = red 
	orange=(ltns,half,0)
	assigned[tlds[1]] = orange
	magenta=(ltns,0,half)
	assigned[tlds[2]] = magenta
	yellow=(ltns,ltns,0)
	assigned[tlds[3]] = yellow
	purple=(ltns,0,ltns)
	assigned[tlds[4]] = purple
	yellowGreen=(half,ltns,0)
	assigned[tlds[5]] = yellowGreen
	violet=(half,0,ltns)
	assigned[tlds[6]] = violet
	green=(0,ltns,0)
	assigned[tlds[7]] = green
	seaGreen=(0,ltns,half)
	turquois=(0,ltns,ltns)
	lightBlue=(0,half,ltns)
	
	return assigned


def calcGap(ogTree, level, dimension):
	leveledTree = getXlevel([ogTree], level)
	bSum = sumCounts(leveledTree)
	layerCount = len(leveledTree.keys())
	gap = int((dimension-bSum)/(layerCount+1))
	return gap


def getXlevel(inList, x):
	outTrees = {}
	for tree in inList:
		if(isinstance(tree, int) == False):
			for k in tree.keys():
				if(k != "count"):
					outTrees[k] = tree[k]
	if(x == 0):
		return outTrees
	callList = list(outTrees.values())
	return getXlevel(callList, x-1)


def sumCounts(tree):
	summation = 0
	for k in tree.keys():
		if((k[0:2] != "*.") and (k != "#count")):
			summation = summation + tree[k]["#count"]
	return summation


def removeWild(dictionary):
	retDict = {}
	for k in dictionary.keys():
		if(k[0:2] != "*."):
			retDict[k] = dictionary[k]
	return retDict


def getMaxChars(forrest):
	maximum = 0
	for treeName in forrest.keys():
		if(treeName != "#count"):
			subName = "*."+treeName.split('.')[0]
			currLen = len(subName)
			if(currLen > maximum):
				maximum = currLen
	return maximum


def parseParent(domainName):
	parts = domainName.split('.')
	parts.pop(0)
	parent = parts.pop(0)
	for pt in parts:
		parent = parent + '.'
		parent = parent + pt
	return parent


allDomains = getDomains(sys.argv[1])
uniqueDomains = list(set(allDomains))
print(str(len(uniqueDomains))+" unique domain names")
forrest = {}
for domainName in allDomains:
	levels = domainName.split('.')
	forrest = recurseDoms(forrest, levels)
dispDomains = parseTree(forrest, 8, '')
graphName = drawTree(dispDomains, len(uniqueDomains))
print("Domain Graph successfully written to "+graphName)
