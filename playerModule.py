import pygame
import levelModule
import enemyModule
from config import *

imgPlayer = 0
imgPlayerDeathAnim = 0

class Player:
	leftPressed = False
	rightPressed = False
	jumpPressed = False
	runPressed = False
	firePressed = False
	
	box = pygame.Rect((0, 0), PLAYER_SIZE)
	lastCheckpoint = 0
	
	vSpeed = 0
	fireTimer = 0
	jumpTimer = 0
	facing = "R"
	curFrame = 0
	frameTimer = 0
	alive = True
	
	deathAnimTimer = 0
	deathHazard = 0 #[destRect, rotation]
	
	def __init__(self):
		self.leftPressed = False
		self.rightPressed = False
		self.jumpPressed = False
		self.runPressed = False
		self.firePressed = False
		
		self.box = pygame.Rect((0, 0), PLAYER_SIZE)
		self.lastCheckpoint = 0
		
		self.vSpeed = 0
		self.fireTimer = 0
		self.jumpTimer = 0
		self.facing = "R"
		
		self.alive = True
		
		self.deathAnimTimer = 0
		self.deathHazard = 0
	
	#Update Methods
	def update(self, level, offset):
		if self.alive:
			self.moveHorizontal(level)
			self.moveVertical(level)
			self.checkCollisions(level)
			self.firePaintBalls(level, offset)
		else:
			self.deathAnimTimer = self.deathAnimTimer - 1
	
	def moveHorizontal(self, level):
		if self.leftPressed or self.rightPressed:
			self.updateFrame()
		else:
			self.frameTimer = 0
			self.curFrame = 0
		if self.leftPressed:
			self.facing = "L"
			if self.runPressed:
				self.box[0] = self.box[0] - PLAYER_RUN_SPEED
			else:
				self.box[0] = self.box[0] - PLAYER_WALK_SPEED
			wall = self.box.collidelist(level.walls)
			if wall > -1:
				self.box[0] = level.walls[wall][0] + level.walls[wall][2]
		if self.rightPressed:
			self.facing = "R"
			if self.runPressed:
				self.box[0] = self.box[0] + PLAYER_RUN_SPEED
			else:
				self.box[0] = self.box[0] + PLAYER_WALK_SPEED
			wall = self.box.collidelist(level.walls)
			if wall > -1:
				self.box[0] = level.walls[wall][0] - self.box[2]
				
		#Check if walked off screen
		if self.box[0] < 0:
			self.box[0] = 0
		if self.box[0] + self.box[3] > level.size[0]:
			self.box[0] = level.size[0] - self.box[3]
		
	def updateFrame(self):
		self.frameTimer = self.frameTimer - 1
		if self.frameTimer <= 0:
			self.curFrame = self.curFrame + 1
			if self.curFrame >= PLAYER_NUM_FRAMES:
				self.curFrame = 0
			
			self.frameTimer = PLAYER_FRAME_TIMER
	
	def moveVertical(self, level):
		wall = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(level.walls)
		if wall > -1:#Player is on the ground
			self.box[1] = level.walls[wall][1] - self.box[3]
			self.vSpeed = 0
			if self.jumpPressed:#Player is jumping while on the ground
				self.box[1] = self.box[1] - 1
				self.vSpeed = -PLAYER_JUMP_SPEED
				self.jumpTimer = PLAYER_JUMP_TIMER
		else:#Player is in the air
			if self.jumpPressed and self.jumpTimer > 0:
				self.jumpTimer = self.jumpTimer - 1
				self.vSpeed = -PLAYER_JUMP_SPEED
			else:
				self.vSpeed = self.vSpeed + PLAYER_GRAVITY
				self.jumpTimer = 0
			if self.vSpeed > PLAYER_MAX_FALL_SPEED:
				self.vSpeed = PLAYER_MAX_FALL_SPEED
			self.box[1] = self.box[1] + self.vSpeed
			wall = self.box.collidelist(level.walls)
			if wall > -1:#Player hit a wall in the air
				if self.vSpeed > 0:#Player landed on a wall
					self.box[1] = level.walls[wall][1] - self.box[3]
				elif self.vSpeed < 0:#Player hit a wall with their head
					self.box[1] = level.walls[wall][1] + level.walls[wall][3]
				self.jumpTimer = 0
				self.vSpeed = 0
	
	#Check collisions with enemies and hazards
	def checkCollisions(self, level):
		checkpointIndex = self.box.collidelist(level.checkpoints)
		if checkpointIndex > -1 and not self.lastCheckpoint == level.checkpoints[checkpointIndex]:
			level.addCheckpointMessage()
			self.lastCheckpoint = level.checkpoints[checkpointIndex]
		
		#Build boxes that are slightly smaller than the actual box
		hazards = []
		for i in range(len(level.hazards)):
			if level.hazardRotations[i] == 0:#A
				hazards.append(pygame.Rect(level.hazards[i][0]+4, level.hazards[i][1]+8, level.hazards[i][2]-8, level.hazards[i][3]-8))
			elif level.hazardRotations[i] == 1:#<
				hazards.append(pygame.Rect(level.hazards[i][0]+8, level.hazards[i][1]+4, level.hazards[i][2]-8, level.hazards[i][3]-8))
			elif level.hazardRotations[i] == 2:#V
				hazards.append(pygame.Rect(level.hazards[i][0]+4, level.hazards[i][1], level.hazards[i][2]-8, level.hazards[i][3]-8))
			elif level.hazardRotations[i] == 3:#>
				hazards.append(pygame.Rect(level.hazards[i][0], level.hazards[i][1]+4, level.hazards[i][2]-8, level.hazards[i][3]-8))
		
		enemyIndex = -1
		for i in range(len(level.enemies)):
			if self.box.colliderect(level.enemies[i].box) and level.enemies[i].enragedTimer > 0:
				enemyIndex = i
				break
		hazardIndex = self.box.collidelist(hazards)
		
		#Collided with an enemy/hazard. Kill player
		if (enemyIndex > -1 or hazardIndex > -1) and not GOD_MODE:
			self.alive = False
			self.deathAnimTimer = PLAYER_DEATH_ANIM_TIMER
			
			if hazardIndex > -1:
				self.deathHazard = (level.hazards[hazardIndex], level.hazardRotations[hazardIndex])
	
	def firePaintBalls(self, level, offset):
		if self.fireTimer > 0:
			self.fireTimer = self.fireTimer - 1
		if self.firePressed and self.fireTimer <= 0:
			originX = self.box[0] + self.box[2]/2 - PAINT_SIZE[0]/2
			originY = self.box[1] + self.box[3]/2 - PAINT_SIZE[1]/2
			
			mousePos = pygame.mouse.get_pos()
			targetX = mousePos[0] + offset[0]
			targetY = mousePos[1] + offset[1]
			
			level.firePaint((originX, originY), (targetX, targetY))
			self.fireTimer = PLAYER_FIRE_TIMER
	
	#Render Methods
	def render(self, surface):
		if self.alive:
			x = self.curFrame * PLAYER_SIZE[0]
			if self.facing == "R":
				y = 0
			elif self.facing == "L":
				y = PLAYER_SIZE[1]
			
			surface.blit(imgPlayer, self.box, (x, y, PLAYER_SIZE[0], PLAYER_SIZE[1]))
			
			if DRAW_DEBUG and not self.lastCheckpoint == 0:
				pygame.draw.rect(surface, CLR_OLIVE, self.lastCheckpoint)
		else:
			if not self.deathHazard == 0: #Draw hazard that killed player
				surface.blit(pygame.transform.rotate(levelModule.imgSpike, self.deathHazard[1] * 90), self.deathHazard[0])
			#Draw death animation based on self.deathAnimTimer
			x = (PLAYER_DEATH_ANIM_NUM_FRAMES - 1) - (self.deathAnimTimer / PLAYER_DEATH_ANIM_FRAME_TIME)
			surface.blit(
				imgPlayerDeathAnim,
				(self.box[0] - PLAYER_DEATH_OFFSET[0], self.box[1] - PLAYER_DEATH_OFFSET[1]),
				((x*PLAYER_DEATH_SIZE[0], 0), PLAYER_DEATH_SIZE)
			)