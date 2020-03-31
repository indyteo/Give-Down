import pygame, pickle
from pygame.locals import *
from os import listdir
from os.path import isfile

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

def actualiser():
	fenetre.blit(tiles["fond"], (0, 0))
	fenetre.blit(tiles["grid"], (0, 0))
	for tile in board.items():
		afficher(tile[1], tile[0][0], tile[0][1])
	for tile in inv.items():
		afficher(tile[1], tile[0][0] + tf[0] // tc, tile[0][1])
	pygame.display.flip()

pygame.init()

# Variables
tf = (1200, 800)
ti = (200, 800)
tc = 50
board = {}
inv = {}
rect = {}
selected = "empty"
continuer = 1

# Chargement du plateau
print("Liste des niveaux :")
for save in listdir("levels"):
	print(save)
nom = input("\nNom du niveau à charger (\"none\" pour créer un nouveau niveau) : ")

if nom == "none":
	for X in range(tf[0] // tc):
		for Y in range(tf[1] // tc):
			board[X, Y] = "empty"

else:
	with open("levels/{nom}".format(nom = nom), "rb") as data:
		level_data = pickle.Unpickler(data).load()

	try:
		board = level_data["board"]
	except KeyError:
		for X in range(tf[0] // tc):
			for Y in range(tf[1] // tc):
				board[X, Y] = "empty"
	try:
		spawn = level_data["spawn"]
	except KeyError:
		spawn = (0, 675)
	try:
		end = level_data["end"]
	except KeyError:
		pass

# Création de la fenêtre
fenetre = pygame.display.set_mode((tf[0] + ti[0], tf[1]))
pygame.display.set_caption("Give Down - Level Editor")
pygame.key.set_repeat(50, 10)

# Import des données communes et affichage du fond
from misc.cst import *
fenetre.blit(tiles["fond"], (0, 0))
fenetre.blit(tiles["grid"], (0, 0))

# Affichage du plateau
for X in range(tf[0] // tc):
	for Y in range(tf[1] // tc):
		afficher(board[X, Y], X, Y)

# Création de l'inventaire
a = [tile for tile in tiles.keys() if tiles[tile].get_width() == tc or tile == "spawn_flag" or tile == "end_flag"]
i = 0
for X in range(ti[0] // tc):
	for Y in range(ti[1] // tc):
		try:
			inv[X, Y] = a[i]
			i += 1
		except IndexError:
			inv[X, Y] = "empty"

# Affichage de l'inventaire
for tile in inv.items():
	afficher(tile[1], tile[0][0] + tf[0] // tc, tile[0][1])

pygame.display.flip()

while continuer:
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			continuer = 0
			save = 0
		if event.type == KEYDOWN and event.key == K_RETURN:
			continuer = 0
			save = 1
		
		elif event.type == MOUSEBUTTONDOWN:
			if event.button == 1:
				if event.pos[0] > tf[0]:
					selected = inv[(event.pos[0] - tf[0]) // tc, event.pos[1] // tc]
				else:
					board[event.pos[0] // tc, event.pos[1] // tc] = selected
					actualiser()
			elif event.button == 3:
				if event.pos[0] > tf[0]:
					selected = "empty"
				else:
					board[event.pos[0] // tc, event.pos[1] // tc] = "empty"
					actualiser()
			elif event.button == 2:
				if event.pos[0] > tf[0]:
					selected = inv[(event.pos[0] - tf[0]) // tc, event.pos[1] // tc]
				else:
					selected = board[event.pos[0] // tc, event.pos[1] // tc]
		elif event.type == MOUSEMOTION:
			if event.buttons[0] == 1 and event.pos[0] < tf[0]: 
				board[event.pos[0] // tc, event.pos[1] // tc] = selected
				actualiser()
			elif event.buttons[2] == 1 and event.pos[0] < tf[0]:
				board[event.pos[0] // tc, event.pos[1] // tc] = "empty"
				actualiser()

pygame.quit()

if save:
	nom = input("Nom : ")
	for search in board.items():
		if search[1] == "spawn_flag":
			spawn = search[0][0] * tc, search[0][1] * tc
		elif search[1] == "end_flag":
			end = tiles["end_flag"].get_rect(topleft = (search[0][0] * tc, search[0][1] * tc))
	niveau = {"nom": nom, "board": board, "spawn": spawn, "end": end}
	if not(isfile("levels/{nom}".format(nom = nom))):
		open("levels/{nom}".format(nom = nom), "w").close()
	with open("levels/{nom}".format(nom = nom), "wb") as data:
		pickle.Pickler(data).dump(niveau)
	print("Niveau créé !")
	input()