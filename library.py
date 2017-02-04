import math

def distance(start, end):
	diffX = abs(start[0] - end[0])
	diffY = abs(start[1] - end[1])
	
	dist = math.sqrt(diffX*diffX + diffY*diffY)
	return dist

def directionPoints(start, end):
	xDiff = end[0] - start[0]
	yDiff = end[1] - start[1]
	return directionDiffs(xDiff, yDiff)

def directionDiffs(xDiff, yDiff):
	degrees = math.degrees(math.atan2(-yDiff, xDiff))
	while degrees < 0:
		degrees = degrees + 360
	
	return degrees
	
def getHSpeed(dir, speed):
	return math.cos(math.radians(dir)) * speed

def getVSpeed(dir, speed):
	return -(math.sin(math.radians(dir)) * speed)

