import pygame
import pickle
import math
import random
import enemyModule
from library import *
from config import *

imgSpike = 0
imgPaintSplatter = 0
imgGoal = 0

sndMonsterDocile = 0
sndMonsterEnraged = 0

fntMessageFont = 0
fntCheckpointFont = 0

def playEnragedSound():
	if SOUNDS_ENABLED:
		sndMonsterDocile.stop()
		if not pygame.mixer.get_busy():
			sndMonsterEnraged.play()

def playGrowlSound():
	if not pygame.mixer.get_busy() and SOUNDS_ENABLED:
		sndMonsterDocile.play()

def removeDeadPaintBalls(ball):
	return ball[3]

def removeDeadSplatters(splatter):
	return splatter[2]
	
def removeDeadHazardSplatters(hazardSplatter):
	return hazardSplatter[2]

def removeDeadEnemies(enemy):
	return enemy.alive

def saveToPickle(level):
	f = open("Data/level"+str(level.index)+".dat", "w")
	pickle.dump(level, f)
	f.close()

def loadFromPickle(index):
	f = open("Data/level"+str(index)+".dat", "r")
	level = pickle.load(f)
	f.close()
	return level

class Level:
	index = 0
	size = (0, 0)#Size of level in pixels
	offsetStart = (0, 0)
	playerStart = (0, 0)
	
	walls = [] #[pygame.Rect]
	
	paintBalls = [] #[paintRect, hSpeed, vSpeed, alive]
	splatters = [] #[destRect, sourceRect, alive]
	
	enemies = [] #[enemyModule.Enemy]
	hazards = [] #[pygame.Rect]
	hazardRotations = [] #[degrees_of_rotation]
	hazardSplatters = [] #[img, dest, alive]
	
	checkpoints = []#[pygame.Rect]
	messages = []#[messageText, origin]
	goal = pygame.Rect((0, 0), TILE_SIZE)
	
	checkpointMessageTimer = 0
	
	def __init__(self, index):
		self.index = index
		self.size = (0, 0)
		self.offsetStart = (0, 0)
		self.playerStart = (0, 0)
		self.walls = []
		self.paintBalls = []
		self.splatters = []
		self.enemies = []
		self.hazards = []
		self.hazardRotations = []
		self.hazardSplatters = []
		self.checkpoints = []
		self.messages = []
		self.goal = pygame.Rect((0, 0), TILE_SIZE)
		
		f = open("levels.txt", "r")
		
		#Find level data by index
		line = f.readline().strip()
		while not line == str(index):
			line = f.readline().strip()
		
		#Init size of level
		line = f.readline().strip()
		size = line.split()
		size[1] = int(size[1])
		size[2] = int(size[2])
		self.size = (size[1] * TILE_SIZE[0], size[2] * TILE_SIZE[1])
		
		#Init offsetStart of level
		line = f.readline().strip()
		offset = line.split()
		offset[1] = int(offset[1])
		offset[2] = int(offset[2])
		self.offsetStart = (offset[1], offset[2])
		
		#Init walls and hazards in level
		for y in range(size[2]):
			line = f.readline()
			for x in range(size[1]):
				if line[x] == "1":#Wall
					self.walls.append(pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
				elif line[x] in ["A", "V", "<", ">"]:#Hazard/Spike
					self.hazards.append(pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
					if line[x] == "A":
						self.hazardRotations.append(0)
					elif line[x] == "V":
						self.hazardRotations.append(2)
					elif line[x] == "<":
						self.hazardRotations.append(1)
					elif line[x] == ">":
						self.hazardRotations.append(3)
				elif line[x] == "G":#Goal
					self.goal[0] = x * TILE_SIZE[0]
					self.goal[1] = y * TILE_SIZE[1]
				elif line[x] == "E":#Enemy
					self.enemies.append(enemyModule.Enemy(x*TILE_SIZE[0], y*TILE_SIZE[1]));
				elif line[x] == "P":#Player
					self.playerStart = (x*TILE_SIZE[0], y*TILE_SIZE[1])
				elif line[x] == "C":#Checkpoint
					self.checkpoints.append(pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], TILE_SIZE[0], TILE_SIZE[1]))
		
		line = f.readline().strip()
		while not line == "---":
			message = line.split(",")
			self.messages.append((message[2], (int(message[0]), int(message[1]))))
			line = f.readline().strip()
		
		f.close()
	
	def firePaint(self, paintOrigin, targetOrigin):
		paintRect = pygame.Rect(paintOrigin, (PAINT_SIZE[0], PAINT_SIZE[1]))
		dir = directionPoints(paintOrigin, targetOrigin)
		hSpeed = getHSpeed(dir, PAINT_SPEED)
		vSpeed = getVSpeed(dir, PAINT_SPEED)
		self.paintBalls.append([paintRect, hSpeed, vSpeed, True])
	
	def addCheckpointMessage(self):
		self.checkpointMessageTimer = CHECKPOINT_TIMER
	
	#Update Methods
	def update(self, player, offset):
		self.updatePaintBalls()
		self.updateEnemies(player)
		self.killOffscreenSplatters(offset)
	
	def updatePaintBalls(self):
		for ball in self.paintBalls:
			ball[2] = ball[2] + PAINT_GRAVITY
			if ball[2] > PAINT_MAX_FALL_SPEED:
				ball[2] = PAINT_MAX_FALL_SPEED
				
			ball[0][0] = ball[0][0] + ball[1]
			ball[0][1] = ball[0][1] + ball[2]
			
			wall = ball[0].collidelist(self.walls)
			hazard = ball[0].collidelist(self.hazards)
			enemyCollide = False
			for enemy in self.enemies:
				if ball[0].colliderect(enemy.box):
					enemyCollide = True
			
			if wall > -1 or hazard > -1 or enemyCollide:
				splatterRect = self.splatterPaint(ball[0])
				self.collideSplatterEnemies(splatterRect)
				ball[3] = False
			
		self.paintBalls = filter(removeDeadPaintBalls, self.paintBalls)
	
	#paintSplatter = (destination, area)
	def splatterPaint(self, ballRect):
		splatterOrigin = (ballRect[0] + ballRect[2]/2, ballRect[1] + ballRect[3]/2)
		splatterRect = pygame.Rect(
			(splatterOrigin[0] - SPLATTER_SIZE[0]/2, splatterOrigin[1] - SPLATTER_SIZE[1]/2),
			SPLATTER_SIZE
		)
		wallList = splatterRect.collidelistall(self.walls)
		for wall in wallList:
			#Find the position on the source image that should be drawn
			sourceX = self.walls[wall][0] - splatterRect[0]
			sourceY = self.walls[wall][1] - splatterRect[1]
			self.splatters.append(
				[
					self.walls[wall],
					pygame.Rect(sourceX, sourceY, self.walls[wall][2], self.walls[wall][3]),
					True
				]
			)
		
		hazardList = splatterRect.collidelistall(self.hazards)
		for hazard in hazardList:
			#Find the position on the source image that should be drawn
			sourceX = self.hazards[hazard][0] - splatterRect[0]
			sourceY = self.hazards[hazard][1] - splatterRect[1]
			
			imgRotatedSpike = pygame.transform.rotate(imgSpike, self.hazardRotations[hazard] * 90)
			imgSplatterSlice = pygame.Surface(TILE_SIZE, pygame.SRCALPHA)
			imgSplatterSlice.blit(imgPaintSplatter, (0, 0), (sourceX, sourceY, TILE_SIZE[0], TILE_SIZE[1]))
			
			imgSplatter = pygame.Surface(TILE_SIZE, pygame.SRCALPHA)
			for x in range(TILE_SIZE[0]):
				for y in range(TILE_SIZE[1]):
					pixel = (x, y)
					#If the pixel is Black in both images, set to Opaque Black, else set to Transparent
					if imgRotatedSpike.get_at(pixel) == CLR_BLACK and imgSplatterSlice.get_at(pixel) == CLR_BLACK:
						imgSplatter.set_at(pixel, CLR_BLACK)
					else:
						imgSplatter.set_at(pixel, CLR_TRANSPARENT)
			
			self.hazardSplatters.append(
				[
					imgSplatter,
					self.hazards[hazard],
					True
				]
			)
		
		return splatterRect
	
	def collideSplatterEnemies(self, splatterRect):
		for enemy in self.enemies:
			if splatterRect.colliderect(enemy.box):
				enemy.splatter()
	
	def updateEnemies(self, player):
		playEnraged = False
		playGrowl = False
		for enemy in self.enemies:
			enemy.update(player, self.walls, self.hazards)
			if enemy.enragedTimer > 0:
				playEnraged = True
			elif abs(player.box[0] - enemy.box[0]) < ENEMY_GROWL_DISTANCE[0] and abs(player.box[1] - enemy.box[1]) < ENEMY_GROWL_DISTANCE[1]:
				playGrowl = True
		
		if playEnraged:
			playEnragedSound()
		elif playGrowl:
			playGrowlSound()
		else:
			pygame.mixer.stop()
		
		self.enemies = filter(removeDeadEnemies, self.enemies)
	
	def killOffscreenSplatters(self, offset):
		for splatter in self.splatters:
			#Offscreen to Left or Right
			if splatter[0][0] + splatter[0][2] < offset[0] + SPLATTER_LIMIT[0] or splatter[0][0] > offset[0] + SPLATTER_LIMIT[1]:
				splatter[2] = False
			#Offscreen to Up or Down
			if splatter[0][1] + splatter[0][3] < offset[1] + SPLATTER_LIMIT[2] or splatter[0][1] > offset[1] + SPLATTER_LIMIT[3]:
				splatter[2] = False
		
		self.splatters = filter(removeDeadSplatters, self.splatters)
		
		for hazardSplatter in self.hazardSplatters:
			#Offscreen to Left or Right
			if hazardSplatter[1][0] + hazardSplatter[1][2] < offset[0] or hazardSplatter[1][0] > offset[0] + SCREEN_SIZE[0]:
				hazardSplatter[2] = False
			#Offscreen to Up or Down
			if hazardSplatter[1][1] - hazardSplatter[1][3] < offset[1] or hazardSplatter[1][1] > offset[1] + SCREEN_SIZE[1]:
				hazardSplatter[2] = False
		
		self.hazardSplatters = filter(removeDeadHazardSplatters, self.hazardSplatters)
	
	#Render Methods
	def renderBehindPlayer(self, offset, surface):
		screenRect = pygame.Rect(offset, SCREEN_SIZE)
		if DRAW_DEBUG:
			drawWalls = screenRect.collidelistall(self.walls)
			for wall in drawWalls:
				pygame.draw.rect(surface, CLR_LIME, self.walls[wall])
			for index in range(len(self.hazards)):
				surface.blit(pygame.transform.rotate(imgSpike, self.hazardRotations[index] * 90), self.hazards[index])
			for checkpoint in self.checkpoints:
				pygame.draw.rect(surface, CLR_AQUA, checkpoint)
		
		for paintBall in self.paintBalls:
			pygame.draw.ellipse(surface, CLR_BLACK, paintBall[0])
		for splatter in self.splatters:
			surface.blit(imgPaintSplatter, splatter[0], splatter[1])
		for hazardSplatter in self.hazardSplatters:
			surface.blit(hazardSplatter[0], hazardSplatter[1])
		
		
		
		surface.blit(imgGoal, self.goal)
	
	def renderFrontPlayer(self, offset, playerOrigin, surface):
		for enemy in self.enemies:
			enemy.render(surface)
		for message in self.messages:
			surface.blit(fntMessageFont.render(message[0], False, CLR_BLACK), message[1])
		
		if self.checkpointMessageTimer > 0:
			self.checkpointMessageTimer = self.checkpointMessageTimer - 1
			self.renderCheckpointMessage(playerOrigin, surface)
	
	def renderCheckpointMessage(self, playerOrigin, surface):
		messageOrigin = (
			playerOrigin[0] - 75,
			playerOrigin[1] - 25
		)
		surface.blit(fntCheckpointFont.render("Checkpoint Reached", False, CLR_BLACK), messageOrigin)
	
	def clearSplatters(self):
		del self.splatters[:]
		del self.hazardSplatters[:]