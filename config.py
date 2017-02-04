SCREEN_SIZE = (640,480)
FRAME_TIME = 50

TILE_SIZE = (32,32)

START_LEVEL = 1
DRAW_DEBUG = False
DRAW_MOUSE = False
SOUNDS_ENABLED = True
HIDDEN_SCREEN_POS = False
GOD_MODE = False

#Set to True before compiling distribution version
LOAD_LEVELS_FROM_PICKLE = True

#Game States
STATE_TITLE = 0
STATE_CONTROLS = 3
STATE_PLAY = 1
STATE_CREDITS = 2

NUM_LEVELS = 5

#Farthest Left the player can move before the screen moves with them,
#Farthest Right the player can move before the screen moves with them
#Farthest Up the player can move before the screen moves with them,
#Farthest Down the player can move before the screen moves with them
OFFSET_LIMIT = (240, SCREEN_SIZE[0] - 240, 200, SCREEN_SIZE[1] - 200)

#Farthest Left the splatter can be before it dies
#Farthest Right the splatter can be before it dies
#Farthest Up the splatter can be before it dies
#Farthest Down the splatter can be before it dies
SPLATTER_LIMIT = (-256, SCREEN_SIZE[0] + 256, -256, SCREEN_SIZE[1] + 256)

CHECKPOINT_TIMER = 60

#Player
PLAYER_SIZE = (16,16)
PLAYER_WALK_SPEED = 4
PLAYER_RUN_SPEED = 8
PLAYER_JUMP_SPEED = 8
PLAYER_GRAVITY = 1
PLAYER_MAX_FALL_SPEED = 8
PLAYER_FIRE_TIMER = 10
PLAYER_JUMP_TIMER = 10
PLAYER_FRAME_TIMER = 5
PLAYER_NUM_FRAMES = 2

PLAYER_DEATH_ANIM_TIMER = 24 #Time for total animation. Non-Looping animation
PLAYER_DEATH_ANIM_NUM_FRAMES = 4
PLAYER_DEATH_ANIM_FRAME_TIME = PLAYER_DEATH_ANIM_TIMER / PLAYER_DEATH_ANIM_NUM_FRAMES
PLAYER_DEATH_SIZE = (16,16)

#How far up and to the left from the player's location to draw the Death animation 
#Because it is bigger than the player sprite
PLAYER_DEATH_OFFSET = (0,0)

#Paint Ball
PAINT_SIZE = (8,8)
PAINT_SPEED = 8
PAINT_MAX_FALL_SPEED = 10
PAINT_GRAVITY = 0.4
SPLATTER_SIZE = (96,96)

#Enemy
ENEMY_SIZE = (32,32)
ENEMY_HSPEED = 1
ENEMY_HSPEED_ENRAGED = 5
ENEMY_JUMP_SPEED = 15
ENEMY_GRAVITY = 1
ENEMY_MAX_FALL_SPEED = 15
ENEMY_TRACK_DISTANCE = 50 #How far away the player can get before the enemy changes direction
ENEMY_FRAME_TIMER = 20 #Time per frame. Looping animation
ENEMY_NUM_FRAMES = 2
ENEMY_MIN_TURN_TIMER = 100
ENEMY_MAX_TURN_TIMER = 200
ENEMY_GROWL_DISTANCE = (500,200) #How far away the player is when the growl sound starts playing

ENEMY_ENRAGED_ANIM_TIMER = 40 #Time for total animation. Non-Looping animation
ENEMY_ENRAGED_NUM_FRAMES = 4
ENEMY_ENRAGED_ANIM_FRAME_TIME = ENEMY_ENRAGED_ANIM_TIMER / ENEMY_ENRAGED_NUM_FRAMES
ENEMY_ENRAGED_TIMER = 100

#Colors
CLR_AQUA = (0,255,255)
CLR_BLACK = (0,0,0)
CLR_BLUE = (0,0,255)
CLR_CORNFLOWER_BLUE = (100,149,237)
CLR_FUCHSIA = (255,0,255)
CLR_GRAY = (128,128,128)
CLR_GREEN = (0,128,0)
CLR_LIME = (0,255,0)
CLR_MAROON = (128,0,0)
CLR_NAVY_BLUE = (0,0,128)
CLR_OLIVE = (128,128,0)
CLR_ORANGE = (255,150,0)
CLR_PINK = (255,0,255)
CLR_PURPLE = (128,0,128)
CLR_RED = (255,0,0)
CLR_SILVER = (192,192,192)
CLR_TEAL = (0,128,128)
CLR_WHITE = (255,255,255)
CLR_YELLOW = (255,255,0)
CLR_TRANSPARENT = (0,0,0,0)