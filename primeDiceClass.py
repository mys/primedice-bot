import json
import logging
import os
import random
import requests
import socket
import socks
import string
import sys
import time

class CaptchaException(Exception):
	pass
	
class TooManyRequestsException(Exception):
	pass
	
class BadGatewayException(Exception):
	pass
	
class AnswerNoneException(Exception):
	pass

class primedice():

	# -------------------------------------------------------------------------
	# __init__
	# -------------------------------------------------------------------------
	def __init__(self):
		self.login_url = 'https://api.primedice.com/api/login'
		self.bet_url = 'https://api.primedice.com/api/bet'
		self.seed_url = 'https://api.primedice.com/api/seed'
		self.info_url = 'https://api.primedice.com/api/users/1'
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.130 Chrome/43.0.2357.130 Safari/537.36'
		}
		self.session = requests.Session()
		self.bet_count = 0
		self.tor = False
		logging.getLogger("requests").setLevel(logging.WARNING)
		logging.getLogger("urllib3").setLevel(logging.WARNING)

	# -------------------------------------------------------------------------
	# setProxy
	# -------------------------------------------------------------------------
	def setProxy(self, host, port):
		int_port = int(port)
		socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, host, int_port)
		socket.socket = socks.socksocket
		self.port = port
		print 'ipify: ', self.session_get('https://api.ipify.org').content 

	# -------------------------------------------------------------------------
	# setTor proxy
	# -------------------------------------------------------------------------
	def setTor(self, port):
		self.tor = True
		int_port = int(port)
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', int_port)
		socket.socket = socks.socksocket
		self.port = port
		self.restartTor()

	# -------------------------------------------------------------------------
	# restartTor
	# -------------------------------------------------------------------------
	def restartTor(self):
		if self.tor:
			os.system('pkill -9 -f torrc.' + self.port)
			time.sleep(1)
			os.system('tor -f /etc/tor/torrc.' + self.port + ' &')
			time.sleep(30)
			#self.session.get('https://api.ipify.org').content
			print 'ipify: ', self.session_get('https://api.ipify.org').content 

	# -------------------------------------------------------------------------
	# session_get
	# -------------------------------------------------------------------------
	def session_get(self, url):
		answer = self.session.get(url)
		if not answer:
			print answer
			print answer.content
			raise AnswerNoneException
		if answer.status_code == 403:
			raise CaptchaException
		else:
			return answer

	# -------------------------------------------------------------------------
	# session_post
	# -------------------------------------------------------------------------
	def session_post(self, url, post):
		answer = self.session.post(url, data = post, headers = self.headers, \
			timeout = 30)
		if answer.status_code == 403:
			raise CaptchaException
		if answer.status_code == 429:
			raise TooManyRequestsException
		if answer.status_code == 502:
			raise BadGatewayException
		else:
			if not answer:
				print answer
				print answer.content
				print answer.status_code
				raise AnswerNoneException
			return answer

	# -------------------------------------------------------------------------
	# login
	# -------------------------------------------------------------------------
	def login(self, username, password, token):
		self.username = username
		self.password = password
		self.token = token
		post_data = {
			'username':str(username),
			'password':str(password),
			'opt':''
		}
		
		
		try:
			if not token:
				login_response = self.session_post(self.login_url, post_data).content
				self.token = json.loads(login_response)["access_token"]
			self.bet_url_params = self.bet_url + "?access_token=" + self.token
			self.seed_url_params = self.seed_url + "?access_token=" + self.token
			self.info_url_params = self.info_url + "?access_token=" + self.token
		
			answer = self.session.get(self.info_url_params)
			print answer
			print answer.content
			if answer.status_code == 403:
				raise CaptchaException
					
			self.balance = json.loads(answer.content)["user"]["balance"]
			logging.info('Login successful, token = %s' % (self.token))

		except CaptchaException:
			print 'Attention required(get): CAPTCHA'
			return False
		except Exception,e:
			print e
			if login_response == "Unauthorized":
				sys.exit("Wrong login details")
			elif login_response == "Too many requests.":
				sys.exit("Too many requests. Wait before running the script again")
			else:
				logging.error("Someting went wrong, unknown error")
				sys.exit(login_response)
		
		return True 

	# -------------------------------------------------------------------------
	# seed
	# -------------------------------------------------------------------------
	def seed(self):
		post_data = {
			'seed': ''.join(random.choice(string.letters + string.digits) \
				for _ in range(30))
		} 
		answer = self.session_post(self.seed_url_params, post = post_data);
		if answer.status_code == 200:
			return json.loads(answer.content)
		else:
			logging.error("Error while resetting seed")
			logging.error(answer)
			logging.error(answer.content)

	# -------------------------------------------------------------------------
	# bet
	# -------------------------------------------------------------------------
	def bet(self, amount = 0, target = 95, condition = "<"):
		try:
			target = float(target)
			amount = int(amount)
		except:
			return "Target must be an integer!"

		if not condition in ["<",">"]:
			logging.error("Wrong condition. Must be either > or <")
			
		else:
			params = {
				'access_token': self.token
			}
			post_data = {
				'amount':str(amount),
				'condition':str(condition),
				'target':str(target)
			}
			
			answer = self.session_post(self.bet_url_params, post = post_data)
				
			if answer.status_code == 200:
				bet_response = json.loads(answer.content)

				feedback = {
					'jackpot': bet_response["bet"]["jackpot"],
					'win': bet_response["bet"]["win"],
					'amount': bet_response["bet"]["amount"],
					'profit': bet_response["bet"]["profit"]
				}
				self.balance = bet_response["user"]["balance"]
				return feedback
				
			elif answer.status_code == 400:
			
				if answer.content == "Insufficient funds":
					sys.exit("Insufficient funds")
					
				if answer.content == "CHANGE SEED":
					return self.seed()
				
			elif answer.status_code == 524:
				logging.error(answer)
				return "Error 524: A timeout occured"
				
			else:
				logging.error("!Error %s:" % (answer.status_code))
				logging.error(answer)
				logging.error(answer.content)
				
