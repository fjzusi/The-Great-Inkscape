import pygame
import os
import playerModule
import levelModule
import enemyModule
from config import *

#Initialize Game
done = False
pygame.init()
if HIDDEN_SCREEN_POS:
	os.environ['SDL_VIDEO_WINDOW_POS'] = '700,600'
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("The Great Inkscape")
clock = pygame.time.Clock()
offset = [0, 0]
gameState = STATE_TITLE

leftKeys = [pygame.K_LEFT, pygame.K_a]
rightKeys = [pygame.K_RIGHT, pygame.K_d]
jumpKeys = [pygame.K_UP, pygame.K_SPACE, pygame.K_w]
#Experimenting with getting rid of run
#runKeys = [pygame.K_LSHIFT, pygame.K_RSHIFT]
runKeys = []

#Load Content
imgTitleScreen = pygame.image.load("Image/TitleScreen.png").convert()
imgControlScreen = pygame.image.load("Image/ControlScreen.png").convert()
imgCreditsScreen = pygame.image.load("Image/CreditsScreen.png").convert()
levelModule.imgSpike = pygame.image.load("Image/Spike.png").convert_alpha()
levelModule.imgPaintSplatter = pygame.image.load("Image/PaintSplatter.png").convert_alpha()
levelModule.imgGoal = pygame.image.load("Image/Door.png").convert_alpha()
playerModule.imgPlayer = pygame.image.load("Image/Player.png").convert_alpha()
playerModule.imgPlayerDeathAnim = pygame.image.load("Image/PlayerDeath.png").convert_alpha()
enemyModule.imgEnemy = pygame.image.load("Image/Enemy.png").convert_alpha()
enemyModule.imgEnemyEnrageAnim = pygame.image.load("Image/EnemyEnrageAnimation.png").convert_alpha()

levelModule.sndMonsterDocile = pygame.mixer.Sound("Sound/Monster_Docile.wav")
levelModule.sndMonsterEnraged = pygame.mixer.Sound("Sound/Monster_Active.wav")

levelModule.fntMessageFont = pygame.font.SysFont("Kristen ITC", 32)
levelModule.fntMessageFont.set_bold(True)
levelModule.fntCheckpointFont = pygame.font.SysFont("Kristen ITC", 18)

screenBuf = pygame.Surface(SCREEN_SIZE)

level = 0
player = playerModule.Player()

while done == False:
	#Check Controls
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			if gameState == STATE_TITLE:
				gameState = STATE_CONTROLS
			elif gameState == STATE_CONTROLS:
				gameState = STATE_PLAY
				if LOAD_LEVELS_FROM_PICKLE:
					level = levelModule.loadFromPickle(START_LEVEL)
				else:
					level = levelModule.Level(START_LEVEL)
				
				offset = [level.offsetStart[0], level.offsetStart[1]]
				player.box[0] = level.playerStart[0]
				player.box[1] = level.playerStart[1]
				player.deathHazard = 0
				player.alive = True
				screenBuf = pygame.Surface(level.size)
			elif gameState == STATE_PLAY:
				if event.key in leftKeys:
					player.leftPressed = True
				if event.key in rightKeys:
					player.rightPressed = True
				if event.key in jumpKeys:
					player.jumpPressed = True
				if event.key in runKeys:
					player.runPressed = True
			elif gameState == STATE_CREDITS:
				gameState = STATE_TITLE
		if event.type == pygame.KEYUP:
			if gameState == STATE_PLAY:
				if event.key in leftKeys:
					player.leftPressed = False
				if event.key in rightKeys:
					player.rightPressed = False
				if event.key in jumpKeys:
					player.jumpPressed = False
				if event.key in runKeys:
					player.runPressed = False
		
		if event.type == pygame.MOUSEBUTTONDOWN and gameState == STATE_PLAY:
			player.firePressed = True
		if event.type == pygame.MOUSEBUTTONUP and gameState == STATE_PLAY:
			player.firePressed = False
	#Update
	if gameState == STATE_PLAY:
		if player.alive:
			player.update(level, offset)
			level.update(player, offset)
			
			#Update Drawing Offset
			#Player moving Left
			if offset[0] <= 0:
				offset[0] = 0
			else:
				while player.box[0] - offset[0] < OFFSET_LIMIT[0]:
					offset[0] = offset[0] - 1
			#Player moving Right
			if offset[0] >= level.size[0] - SCREEN_SIZE[0]:
				offset[0] = level.size[0] - SCREEN_SIZE[0]
			else:
				while player.box[0] - offset[0] > OFFSET_LIMIT[1]:
					offset[0] = offset[0] + 1
			#Player moving Up
			if offset[1] <= 0:
				offset[1] = 0
			else:
				while player.box[1] - offset[1] < OFFSET_LIMIT[2]:
					offset[1] = offset[1] - 1
			#Player moving Down
			if offset[1] >= level.size[1] - SCREEN_SIZE[1]:
				offset[1] = level.size[1] - SCREEN_SIZE[1]
			else:
				while player.box[1] - offset[1] > OFFSET_LIMIT[3]:
					offset[1] = offset[1] + 1
			
			#Player has reached the goal
			if player.box.colliderect(level.goal):
				nextIndex = level.index + 1
				if nextIndex > NUM_LEVELS:
					gameState = STATE_CREDITS
				else:
					if LOAD_LEVELS_FROM_PICKLE:
						level = levelModule.loadFromPickle(nextIndex)
					else:
						level = levelModule.Level(nextIndex)
					offset = [level.offsetStart[0], level.offsetStart[1]]
					player.box[0] = level.playerStart[0]
					player.box[1] = level.playerStart[1]
					player.lastCheckpoint = 0
					player.deathHazard = 0
					player.alive = True
					screenBuf = pygame.Surface(level.size)
		else:
			player.update(level, offset)
			if player.deathAnimTimer <= 0:
				#Death animation has finished playing. Reset level
				index = level.index
				if LOAD_LEVELS_FROM_PICKLE:
					level = levelModule.loadFromPickle(index)
				else:
					level = levelModule.Level(index)
				offset = [level.offsetStart[0], level.offsetStart[1]]
				if player.lastCheckpoint == 0:#Player has not hit a checkpoint yet
					player.box[0] = level.playerStart[0]
					player.box[1] = level.playerStart[1]
				else:
					checkpointX = player.lastCheckpoint[0]
					checkpointY = player.lastCheckpoint[1]
					player.box[0] = checkpointX
					player.box[1] = checkpointY
				
				player.alive = True
				player.deathHazard = 0
		
	#Render
	if DRAW_DEBUG:
		screenBuf.fill(CLR_PINK)
	else:
		screenBuf.fill(CLR_WHITE)
	if gameState == STATE_TITLE:
		screen.blit(imgTitleScreen, (0, 0))
	elif gameState == STATE_CONTROLS:
		screen.blit(imgControlScreen, (0, 0))
	elif gameState == STATE_CREDITS:
		screen.blit(imgCreditsScreen, (0, 0))
	elif gameState == STATE_PLAY:
		level.renderBehindPlayer(offset, screenBuf)
		player.render(screenBuf)
		level.renderFrontPlayer(offset, (player.box[0], player.box[1]), screenBuf)
		screen.blit(screenBuf, (-offset[0], -offset[1]))
		
		if DRAW_MOUSE:
			mousePos = pygame.mouse.get_pos()
			realMousePos = (offset[0] + mousePos[0], offset[1] + mousePos[1])
			screen.blit(levelModule.fntMessageFont.render(str(realMousePos), False, CLR_BLACK), (0, 0))
	
	#Loop
	pygame.display.flip()
	clock.tick(FRAME_TIME)

pygame.mixer.quit()
pygame.quit()