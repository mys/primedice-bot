import json
import logging
import requests
import sqlite3
import sys
import time

import config
import primeDiceClass as primedice


if len(sys.argv) < 4:
	# dropped tor proxy support as it was not working good with large scale deployment 
	# sys.exit('usage: bot.py <login> <password> <token> ')
	sys.exit('usage: bot.py <login> <password> <token> ')

logging.basicConfig(filename='log-' + sys.argv[1] + '.txt', level=logging.INFO, format='[%(asctime)s] %(levelname)s : %(message)s', datefmt='%H:%M:%S')
logging.info("=== Bot is starting, please wait!")

bot = primedice.primedice()
if len(sys.argv) > 5:
	bot.setProxy(sys.argv[4], sys.argv[5])
elif len(sys.argv) > 4:
	bot.setProxy(sys.argv[4])
while True:
	if bot.login(sys.argv[1], sys.argv[2], sys.argv[3]):
		break


bet_size = config.base_bet
streak = 0
profit = 0
wins = 0
win_chance = 10
sign = "<"
withdraw = 0
withbal = config.withbal
withdrawamount = config.withdrawamount
withdrawaddress = config.withdrawaddress
conn = sqlite3.connect('primedice-' + sys.argv[1] + '.sqlite')
cursor = conn.cursor()
cursor.execute('CREATE TABLE if not exists primedice(id INTEGER PRIMARY KEY, date DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, \'LOCALTIME\')), bet TEXT, streak INT, profit TEXT, balance TEXT)')
conn.commit()
 
logging.info("=== Game is starting!")

while (bot.bet_count < config.max_bet_number) \
or (bot.balance >= config.min_balance) \
or (bot.balance <= config.max_balance):

	try:

		if bet_size > bot.balance:
			logging.info("Insufficient funds! :( Returning to base bet!")
			bet_size = config.base_bet
		if bet_size > config.maximum_bet:
			logging.info('Exceeded maximum bet size!')
			bet_size = config.base_bet

		time.sleep(config.wait_time)
		#sing change if losse streak == a defined number you have to change the perecentage too for each individual sing 
		#if streak == 5 and sign == "<":
			#win_chance = 89.99
			#sign = ">"
			#logging.info(win_chance)
			#print(win_chance)
			#print("signchange >")
		
		#change 
		#elif streak == 5 and sign == ">":
			#win_chance = 10
			#sign = "<"
			#logging.info(win_chance)
			#print(win_chance)
			#print("sign change <<<<")
			
	
			

		
		bet_feedback = bot.bet(bet_size, win_chance, sign)
		if not bet_feedback['profit']:
			continue
			
		bot.bet_count += 1
		streak += 1
		profit += bet_feedback['profit']
	           
		
      
		# log json
		data = {}
		data['date'] = time.strftime("%Y-%m-%d %H:%M:%S")
		data['bet'] = bet_size
		data['streak'] = streak
		data['profit'] = profit
		data['balance'] = bot.balance
		json_data = json.dumps(data)
		print json_data
		logging.info(json_data) #python data logger because sqlite makes the bot run slower than it could limiting the maximum amounts of bets per second by 1/2 
		if bot.balance >= withbal : #auto withdraw comment to disable  
			bot.withdraw(withdrawamount,withdrawaddress)
			print("success")
	
		if bet_feedback['win']:
			bet_size *= config.after_win_multiplier
			streak = 0
			profit = 0
			wins += 1


			if wins >= 200:
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
		
		
	except primedice.TooManyRequestsException:
		print '429'
		print '429: TooManyRequestsException'
		print '429'
	except primedice.BadGatewayException:
		print '502: BadGatewayException'
		
		
	except primedice.AnswerNoneException:
		print 'AnswerNoneException'
		
		
	except requests.exceptions.ConnectionError:
		print 'ConnectionError'
	
		
	except requests.exceptions.ReadTimeout:
		print 'ReadTimeout'
	
		
	except AttributeError:
		print 'AttributeError'
	

logging.info('Exit')
