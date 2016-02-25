import json
import logging
import requests
import sqlite3
import sys
import time

import config
import primeDiceClass as primedice

if len(sys.argv) < 4:
	sys.exit('usage: bot.py <login> <password> <token> <optional tor_port>')

logging.basicConfig(filename='log.txt', level=logging.INFO, format='[%(asctime)s] %(levelname)s : %(message)s', datefmt='%H:%M:%S')
logging.info("=== Bot is starting, please wait!")

bot = primedice.primedice()
if len(sys.argv) > 4:
	bot.setProxy(sys.argv[4])
while True:
	if bot.login(sys.argv[1], sys.argv[2], sys.argv[3]):
		break
	bot.restartTor()

bet_size = config.base_bet
streak = 0
profit = 0
wins = 0

conn = sqlite3.connect('primedice.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE if not exists primedice(id INTEGER PRIMARY KEY, date DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, \'LOCALTIME\')), bet TEXT, streak INT, profit TEXT, balance TEXT)')
conn.commit()

logging.info("=== Game is starting!")

while (bot.bet_count < config.max_bet_number) \
or (bot.balance >= config.min_balance) \
or (bot.balance <= config.max_balance) \
or (bet_size <= maximum_bet):

	try:

		if bet_size > bot.balance:
			logging.info("Insufficient funds! :( Returning to base bet!")
			bet_size = config.base_bet

		time.sleep(config.wait_time)
		
		bet_feedback = bot.bet(bet_size, config.win_chance, "<")
		if not bet_feedback['profit']:
			continue
			
		bot.bet_count += 1
		streak += 1
		profit += bet_feedback['profit']
		# cursor.execute("INSERT INTO primedice(bet, streak, profit, balance) VALUES('%s','%s','%s','%s')" % (bet_size, streak, profit, bot.balance))
		# conn.commit()
		
		# log json
		data = {}
		data['date'] = time.strftime("%Y-%m-%d %H:%M:%S")
		data['bet'] = bet_size
		data['streak'] = streak
		data['profit'] = profit
		data['balance'] = bot.balance
		json_data = json.dumps(data)
		print json_data

		if bet_feedback['win']:
			bet_size *= config.after_win_multiplier
			streak = 0
			profit = 0
			wins += 1

			if wins >= 50:
				wins = 0
				print bot.seed()

			if not bet_size:
				bet_size = config.base_bet
			bet_size += config.after_win_sum

		else:
			bet_size *= config.after_loss_multiplier
			if not bet_size:
				bet_size = bot.base_bet
			bet_size += config.after_loss_sum
	
	# exceptions --------------------------------------------------------------
	except primedice.CaptchaException:
		print '403: CaptchaException'
		bot.restartTor()
		
	except primedice.TooManyRequestsException:
		print '429: TooManyRequestsException'
		bot.restartTor()
		
	except primedice.AnswerNoneException:
		print 'AnswerNoneException'
		bot.restartTor()
		
	except requests.exceptions.ConnectionError:
		print 'ConnectionError'
		bot.restartTor()
		
	except requests.exceptions.ReadTimeout:
		print 'ReadTimeout'
		
	except AttributeError:
		print 'AttributeError'
		bot.restartTor()

logging.info('Exit')