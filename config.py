# Login details
username = ''
password = ''
token = ''

# How much will this program run?
max_bet_number = 0 	# 0 is infinity
min_balance = 0		# Stop playing when reached min_balance
max_balance = 10000000	# Stop playing when reached max_balance

wait_time = 0.5		# Seconds to wait between requests

# Betting strategy
base_bet = 2		# minimum = 1
win_chance = 10		# maximum = 98
maximum_bet = 150000	# 1000000 = 0.01 BTC

after_loss_multiplier = 1.12	# 1 - do not multiply, 0 - return to base bet
after_win_multiplier = 0	# 1 - do not multiply, 0 - return to base bet

after_loss_sum = 0	# after multiply, if lost, sum this
after_win_sum = 0	# after multiply, if win, sum this

seed_win = 50       # change seed every no. wins
