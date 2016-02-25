import json
import pygame
import os
from time import sleep
import subprocess
import select
import sys
import time

print 'gui.py initiating...'
time.sleep(3)

os.putenv('SDL_FBDEV', '/dev/fb1')

current_date = 'none'
current_bet_size = 0
current_streak = 0
longest_streak = 0
current_profit = 0
current_balance = 0
is_duplicator = False

def displayAll():
	font = pygame.font.SysFont("Terminal", 24)
	text_surface = font.render('Last bet: ', 0, (220,100,0), (0,0,0))
	lcd.blit(text_surface,(10,10))
	# date
	text_surface = font.render('%s ' % current_date, 0, (220,100,0), (0,0,0))
	lcd.blit(text_surface,(10,50))
	# bet
	text_surface = font.render('%s sat                          ' % current_bet_size, 0, (220,100,0), (0,0,0))
	lcd.blit(text_surface,(10,70))
	# streak, longest
	text_surface = font.render('Step #%s, longest: #%s          ' % (current_streak, longest_streak), 0, (220,100,0), (0,0,0))
	lcd.blit(text_surface,(10,90))
	# profit
	text_surface = font.render('Profit: %s sat          ' % (current_profit), 0, (220,100,0), (0,0,0))
	lcd.blit(text_surface,(10,110))
	
	# logo
	lcd.blit(btnBitcoin, pygame.rect.Rect(330,10,128,128))
	
	# balance
	text_surface = font.render('Total: %s sat   ' % current_balance, 0, (220,100,0), (0,0,0))
	rect = text_surface.get_rect(center=(390,170))
	lcd.blit(text_surface,rect)
	
	pygame.display.update()

def displayDuplicator():
	lcd.blit(screenshot, pygame.rect.Rect(0,0,480,320))
	pygame.display.update()
	
def hideDuplicator():
	lcd.fill((0,0,0))
	pygame.display.update()

def displayLog():
	margin = 200
	for item in stack:
		color = (120,120,120)
		if not item.startswith("{"):
			color = (220,0,0)
		font = pygame.font.SysFont("Terminal", 22)
		text_surface = font.render('%s                                                                                               ' % item, 0, color, (0,0,0))
		#rect = text_surface.get_rect(center=(240,160))
		lcd.blit(text_surface,(10,margin))
		margin = margin + 18
	pygame.display.update()
	
pygame.init()

pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((480, 320))
lcd.fill((0,0,0))
btnBitcoin = pygame.image.load("/home/pi/PrimeDice/btc.png").convert_alpha()
btnBitcoin.fill((255, 255, 255, 220), None, pygame.BLEND_RGBA_MULT)
screenshot = pygame.image.load("/home/pi/duplicator/duplicator.png")
screenshot = pygame.transform.scale(screenshot, (480, 320))
pygame.display.update()

f = subprocess.Popen(['tail','-F','/home/pi/log.txt'],\
	stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

stack = []
stack.insert(0, "")
stack.insert(0, "")
stack.insert(0, "")
stack.insert(0, "")
stack.insert(0, "")
stack.insert(0, "")

displayAll()

print 'gui.py running...'

while True:

	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			if btnBitcoin.get_rect().collidepoint(pygame.mouse.get_pos()):
				displayDuplicator()
				is_duplicator = True
				break;
			if screenshot.get_rect().collidepoint(pygame.mouse.get_pos()):
				hideDuplicator();
				is_duplicator = False
				break;
				
	if p.poll(1) and is_duplicator == False:
		line = f.stdout.readline()
		
		if line.isspace():
			continue
		
		if not line.startswith("{u"):
			if line.startswith("{"):
				print line
				current_date = json.loads(line)['date']
				current_bet_size = json.loads(line)['bet']
				current_streak = json.loads(line)['streak']
				if current_streak > longest_streak:
					longest_streak = current_streak
				current_profit = json.loads(line)['profit']
				current_balance = json.loads(line)['balance']
				displayAll()

		stack.pop()
		stack.insert(0, line.replace('\t', '  ').replace('\n', ''))
		print 'LINE: ', line
		displayLog()
	sleep(0.1)
