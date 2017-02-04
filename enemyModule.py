import pygame
import random
from config import *

imgEnemy = 0
imgEnemyEnrageAnim = 0

class Enemy:
	box = pygame.Rect((0, 0), ENEMY_SIZE)
	
	vSpeed = 0
	tryJump = False
	
	facing = "L"
	turnTimer = 0
	
	curFrame = 0
	frameTimer = 0
	
	enragedAnimTimer = 0
	enragedTimer = 0
	alive = True
	
	def __init__(self, originX, originY):
		self.box = pygame.Rect((originX, originY), ENEMY_SIZE)
		self.vSpeed = 0
		self.tryJump = False
		self.facing = "L"
		self.turnTimer = random.randrange(ENEMY_MIN_TURN_TIMER, ENEMY_MAX_TURN_TIMER)
		self.curFrame = 0
		self.frameTimer = 0
		self.enragedAnimTimer = 0
		self.enragedTimer = 0
		self.alive = True
	
	def splatter(self):
		if self.enragedAnimTimer <= 0:
			if self.enragedTimer <= 0:#First splatter. Start "winding up"
				self.enragedAnimTimer = ENEMY_ENRAGED_ANIM_TIMER
			else:#Subsequent splatters while still enraged. Remain enraged
				self.enragedTimer = ENEMY_ENRAGED_TIMER
	
	def update(self, player, walls, hazards):
		self.tryJump = False
		if self.enragedAnimTimer > 0:#Proceed with Enraged Animation
			self.enragedAnimTimer = self.enragedAnimTimer - 1
			if self.enragedAnimTimer <= 0:
				self.enragedTimer = ENEMY_ENRAGED_TIMER
		elif self.enragedTimer > 0:#Pursue player over walls and drops
			self.enragedTimer = self.enragedTimer - 1
			self.moveEnraged(player, walls)
			self.moveVertical(walls)
		else:#Patrol one area, avoiding walls, drops, and hazards
			self.moveHorizontal(walls, hazards)
			self.moveVertical(walls)
			self.randomAboutFace()
		
		#Despite being programmed to avoid hazards when not enraged
		#Include this here incase the enragedTimer runs out while in the air over a hazard
		self.hazardCollisions(hazards)
		self.updateFrame()
	
	def moveEnraged(self, player, walls):
		distance = self.box[0] - player.box[0]
		if distance < -ENEMY_TRACK_DISTANCE:#Player is far to the Right of enemy
			self.facing = "R"
		elif distance > ENEMY_TRACK_DISTANCE:#Player is far to the Left of enemy
			self.facing = "L"
		if self.facing == "L":
			self.box[0] = self.box[0] - ENEMY_HSPEED_ENRAGED
			
			#Bounce off walls
			wall = self.box.collidelist(walls)
			if wall > -1:#Hitting a wall. Try to jump over it
				self.box[0] = walls[wall][0] + walls[wall][2]
				self.tryJump = True
			
			#Bounce off drops
			onGround = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(walls)
			scanRect = pygame.Rect(self.box[0] - self.box[2], self.box[1] + 1, self.box[2], self.box[3])
			drop = scanRect.collidelist(walls)
			if drop == -1 and onGround > -1:#Approaching a drop. Try to jump over it
				self.tryJump = True
		if self.facing == "R":
			self.box[0] = self.box[0] + ENEMY_HSPEED_ENRAGED
			
			#Bounce off walls
			wall = self.box.collidelist(walls)
			if wall > -1:#Hitting a wall. Try to jump over it
				self.box[0] = walls[wall][0] - self.box[2]
				self.tryJump = True
			
			#Bounce off drops
			onGround = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(walls)
			scanRect = pygame.Rect(self.box[0] + self.box[2], self.box[1] + 1, self.box[2], self.box[3])
			drop = scanRect.collidelist(walls)
			if drop == -1 and onGround > -1:#Approaching a drop. Try to jump over it
				self.tryJump = True
	
	def hazardCollisions(self, hazards):
		hazard = self.box.collidelist(hazards)
		if hazard > -1:
			self.alive = False
	
	def moveHorizontal(self, walls, hazards):
		if self.facing == "L":
			self.box[0] = self.box[0] - ENEMY_HSPEED
			
			#Bounce off walls
			wall = self.box.collidelist(walls)
			if wall > -1:
				self.box[0] = walls[wall][0] + walls[wall][2]
				self.facing = "R"
			
			#Bounce off hazards
			hazard = self.box.collidelist(hazards)
			if hazard > -1:
				self.box[0] = hazards[hazard][0] + hazards[hazard][2]
				self.facing = "R"
			
			#Bounce off drops
			onGround = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(walls)
			scanRect = pygame.Rect(self.box[0] - self.box[2], self.box[1] + 1, self.box[2], self.box[3])
			drop = scanRect.collidelist(walls)
			if drop == -1 and onGround > -1:
				self.facing = "R"
		elif self.facing == "R":
			self.box[0] = self.box[0] + ENEMY_HSPEED
			
			#Bounce off walls
			wall = self.box.collidelist(walls)
			if wall > -1:
				self.box[0] = walls[wall][0] - self.box[2]
				self.facing = "L"
			
			#Bounce off hazards
			hazard = self.box.collidelist(hazards)
			if hazard > -1:
				self.box[0] = hazards[hazard][0] - self.box[2]
				self.facing = "L"
			
			#Bounce off drops
			onGround = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(walls)
			scanRect = pygame.Rect(self.box[0] + self.box[2], self.box[1] + 1, self.box[2], self.box[3])
			drop = scanRect.collidelist(walls)
			if drop == -1 and onGround > -1:
				self.facing = "L"
	
	def moveVertical(self, walls):
		wall = pygame.Rect(self.box[0], self.box[1]+1, self.box[2], self.box[3]).collidelist(walls)
		if wall > -1:#Enemy is on the ground
			self.box[1] = walls[wall][1] - self.box[3]
			self.vSpeed = 0
			if self.tryJump:#Enemy is jumping while on the ground
				self.box[1] = self.box[1] - 1
				self.vSpeed = -ENEMY_JUMP_SPEED
		else:#Enemy is in the air
			self.vSpeed = self.vSpeed + ENEMY_GRAVITY
			if self.vSpeed > ENEMY_MAX_FALL_SPEED:
				self.vSpeed = ENEMY_MAX_FALL_SPEED
			self.box[1] = self.box[1] + self.vSpeed
			wall = self.box.collidelist(walls)
			if wall > -1:#Enemy hit a wall in the air
				if self.vSpeed > 0:#Enemy landed on a wall
					self.box[1] = walls[wall][1] - self.box[3]
				elif self.vSpeed < 0:#Enemy hit a wall with their head
					self.box[1] = walls[wall][1] + walls[wall][3]
				self.vSpeed = 0
	
	def randomAboutFace(self):
		self.turnTimer = self.turnTimer - 1
		if self.turnTimer <= 0:
			if self.facing == "R":
				self.facing = "L"
			elif self.facing == "L":
				self.facing = "R"
			
			self.turnTimer = random.randrange(ENEMY_MIN_TURN_TIMER, ENEMY_MAX_TURN_TIMER)
		
	def updateFrame(self):	
		self.frameTimer = self.frameTimer - 1
		if self.frameTimer <= 0:
			self.curFrame = self.curFrame + 1
			if self.curFrame >= ENEMY_NUM_FRAMES:
				self.curFrame = 0
			self.frameTimer = ENEMY_FRAME_TIMER
	
	def render(self, surface):
		if DRAW_DEBUG:
			growlBox = (
				self.box[0] - ENEMY_GROWL_DISTANCE[0],
				self.box[1] - ENEMY_GROWL_DISTANCE[1],
				ENEMY_GROWL_DISTANCE[0] * 2,
				ENEMY_GROWL_DISTANCE[1] * 2
			)
			pygame.draw.rect(surface, CLR_YELLOW, growlBox, 1)
		#Draw "winding up" animation
		#This is separate because it uses a different sprite sheet than the other two animations
		if self.enragedAnimTimer > 0:
			if self.facing == "R":
				#Figuring out x is more complicated because the frames are going up while the animation timer is going down
				x = (ENEMY_ENRAGED_NUM_FRAMES - 1) - (self.enragedAnimTimer / ENEMY_ENRAGED_ANIM_FRAME_TIME)
				surface.blit(imgEnemyEnrageAnim, self.box, ((x*ENEMY_SIZE[0], 0), ENEMY_SIZE))
			else:
				x = self.enragedAnimTimer / ENEMY_ENRAGED_ANIM_FRAME_TIME
				surface.blit(pygame.transform.flip(imgEnemyEnrageAnim, True, False), self.box, ((x*ENEMY_SIZE[0], 0), ENEMY_SIZE))
		else:#Draw normal/enraged animation
			x = self.curFrame * ENEMY_SIZE[0]
			y = 0
			if self.facing == "L":
				y = y + ENEMY_SIZE[1]
			if self.enragedTimer > 0:
				y = y + ENEMY_SIZE[1] * 2
			
			surface.blit(imgEnemy, self.box, ((x, y), ENEMY_SIZE))