import pygame, pickle
from pygame.locals import *
from os import listdir

def afficher(img, X, Y):
	rect = tiles[img].get_rect()
	if "center" in tags[img]:
		rect.center = tc * (X + 0.5), tc * (Y + 0.5)
	elif "align_tl" in tags[img]:
		rect.topleft = tc * X, tc * Y
	elif "align_bl" in tags[img]:
		rect.bottomleft = tc * X, tc * (Y + 1)
	elif "align_br" in tags[img]:
		rect.bottomright = tc * (X + 1), tc * (Y + 1)
	elif "align_tr" in tags[img]:
		rect.topright = tc * (X + 1), tc * Y
	elif "align_mt" in tags[img]:
		rect.midtop = tc * (X + 0.5), tc * Y
	elif "align_ml" in tags[img]:
		rect.midleft = tc * X, tc * (Y + 0.5)
	elif "align_mb" in tags[img]:
		rect.midbottom = tc * (X + 0.5), tc * (Y + 1)
	elif "align_mr" in tags[img]:
		rect.midright = tc * (X + 1), tc * (Y + 0.5)
	fenetre.blit(tiles[img], rect)
	return rect

def actualiser():
	fenetre.blit(tiles["fond"], (0, 0))
	fenetre.blit(tiles["perso"], perso)
	for tile in board.items():
		if tile[1] != "":
			afficher(tile[1], tile[0][0], tile[0][1])
	pygame.display.flip()

class DataError(BaseException):
	def __init__(self, msg = "Niveau invalide"):
		self.message = msg
	def __str__(self):
		return str(self.message)

pygame.init()

# Variables
tf = (1200, 800)
tc = 50
board = {}
rect = {}
solid = []
mortal = []
slope_up = []
slope_down = []
t = 0			# "Compteur" de temps pour la gravité
v = 0			# Valeur initiale de la vitesse (= Pas de saut)
v0 = 10			# Valeur de la vitesse lors du saut (= Début du saut)
g0 = 0.9		# Coefficient gravitationnel
g1 = 1.5		# Valeur du coefficient gravitationnel lors du plongeon
g = g0			# Initialisation de la gravité
cd = 0			# Compteur pour ralentir l'animation de saut
cd0 = 6			# Valeur à atteindre pour le compteur pour passer à l'animation suivante
vm = 3			# Valeur de la vitesse de mouvement (gauche / droite)
gms = True
continuer = 1

# Chargement du plateau
if listdir("levels") == []:
	raise DataError("Aucun niveau disponible.")

print("Liste des niveaux :")
for save in listdir("levels"):
	print(save)
nom = input("\nNom : ")
with open("levels/{nom}".format(nom = nom), "rb") as data:
	level_data = pickle.Unpickler(data).load()

try:
	board = level_data["board"]
except KeyError:
	raise DataError
try:
	spawn = level_data["spawn"]
except KeyError:
	raise DataError
try:
	end = level_data["end"]
except KeyError:
	raise DataError

# Création de la fenêtre
fenetre = pygame.display.set_mode(tf)
pygame.display.set_caption("Give Down - {nom}".format(nom = nom))
pygame.key.set_repeat(50, 10)

# Import des données communes et affichage du fond
from misc.cst import *
fenetre.blit(tiles["fond"], (0, 0))

# Initialisation du personnage
perso = tiles["perso"].get_rect()
perso.x, perso.y = spawn
fenetre.blit(tiles["perso"], perso)

# Affichage du plateau
for X in range(tf[0] // tc):
	for Y in range(tf[1] // tc):
		rect[X, Y] = afficher(board[X, Y], X, Y)
		
		if "solid" in tags[board[X, Y]]:
			solid.append(rect[X, Y])
		elif "mortal" in tags[board[X, Y]]:
			mortal.append(rect[X, Y])
		elif "slope_up" in tags[board[X, Y]]:
			slope_up.append(rect[X, Y])
		elif "slope_down" in tags[board[X, Y]]:
			slope_down.append(rect[X, Y])

pygame.display.flip()

while continuer:
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			continuer = 0
	
	if gms:
		cd += 1
		if cd == cd0:
			cd = 0
			gravity = int(g * t**2 - v * t)
			t += 1
			perso.y += gravity
			collide_blocs = perso.collidelist(solid)
			if collide_blocs != -1:
				if gravity > 0:
					perso.y = solid[collide_blocs].y - perso.h
					t, g, v = 0, g0, 0
				else:
					perso.y = solid[collide_blocs].y + tc
			elif perso.y > tf[1] - perso.h:
				perso.y = tf[1] - perso.h
				t, g, v = 0, g0, 0
			elif perso.y < 0:
				perso.y = 0
			
			collide_slopes_up = perso.collidelist(slope_up)
			if collide_slopes_up != -1:
				if perso.bottomright[0] - slope_up[collide_slopes_up].x > tc - perso.bottomright[1] + slope_up[collide_slopes_up].y:
					if gravity >= 0 or perso.right >= slope_up[collide_slopes_up].left + vm / 2:
						perso.y = slope_up[collide_slopes_up].y - perso.bottomright[0] + slope_up[collide_slopes_up].x - perso.h + tc
						t, g, v, = 0, g0, 0
					else:
						perso.y = slope_up[collide_slopes_up].y + tc
	
	keys = pygame.key.get_pressed()
	if keys[K_UP]:
		if gms:
			v = v0
		else:
			perso.y -= vm
			if perso.collidelist(solid) != -1 or perso.y < 0:
				perso.y += vm
	if keys[K_DOWN]:
		if gms:
			g = g1
		else:
			perso.y += vm
			if perso.collidelist(solid) != -1 or perso.y > tf[1] - perso.h:
				perso.y -= vm
	if keys[K_RIGHT]:
		perso.x += vm
		if perso.collidelist(solid) != -1 or perso.x > tf[0] - perso.w:
			perso.x -= vm
	
		collide_slopes_up = perso.collidelist(slope_up)
		if collide_slopes_up != -1:
			perso.y = slope_up[collide_slopes_up].y - perso.bottomright[0] + slope_up[collide_slopes_up].x - perso.h + tc
	
	if keys[K_LEFT]:
		perso.x -= vm
		if perso.collidelist(solid) != -1 or perso.x < 0:
			perso.x += vm
	
		collide_slopes_up = perso.collidelist(slope_up)
		if collide_slopes_up != -1:
			perso.y = slope_up[collide_slopes_up].y - perso.bottomright[0] + slope_up[collide_slopes_up].x - perso.h + tc
	
	if keys[K_g] and keys[59]:
		if keys[K_c] and not(keys[K_s]):
			gms = False
			print("Cheat code #1 : Activating")
		if keys[K_s] and not(keys[K_c]):
			gms = True
			print("Cheat code #1 : Desactivating")
	
	if keys[K_s] and keys[K_p]:
		spawn = perso.bottomleft
	
	if gms:
		if perso.collidelist(mortal) + 1:
			perso.bottomleft = spawn
	
	if perso.colliderect(end):
		print("Gg, c'est gagné !")
	
	actualiser()

pygame.quit()