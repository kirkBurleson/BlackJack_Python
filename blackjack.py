import random

class Player:
	hands = []
	bets = [0,0,0,0]
	split_aces = [False, False, False, False]
	bet = 0
	money = 50.0

class Game:
	DECKS = 4
	SUITS = 4
	cards = [2,3,4,5,6,7,8,9,10,'J','Q','K','A']
	shoe = (cards * SUITS) * DECKS
	mark = len(shoe) - 12
	pos = 0
	playing = True

	def next_card(self):
		if self.pos == self.mark:
			self.pos = 0
			self.shuffle()

		card = self.shoe[self.pos]
		self.pos += 1

		return card

	def shuffle(self):
		end = len(self.shoe)

		while end > 0:
			i = int(random.random() * end)
			(self.shoe[i], self.shoe[end-1]) = (self.shoe[end-1], self.shoe[i])
			end -= 1

class Dealer:
	hand = []

def can_split(hand, player):
	if len(hand) != 2 or len(player.hands) == 4 or player.money < player.bet * len(player.hands):
		return False

	# J,Q,K
	if is_string(hand[0]) and is_string(hand[1]):
		return hand[0] == hand[1]

	# Numbers
	if type(hand[0]) == type(1) and type(hand[1]) == type(1):
		return hand[0] == hand[1]

	# Aces and mixed types (num, str)
	return is_double_aces(hand)

def change_ace(hand):
	for i in range(len(hand)):
		card = hand[i]
		if type(card) == type("") and card == 'A':
			hand[i] = 1
			return True

	return False

def get_total(hand, idx="", player=""):
	total = 0
	for card in hand:
		tp = type(card)

		if tp == type(1):
			if card > 0 and card < 11:
				total += int(card)
				continue
		elif tp == type(""):
			if card == 'A':
				total += 11
			else:
				total += 10

	if total > 21:
		# try aces as 1's instead of 11's
		if change_ace(hand) == True:
			total = get_total(hand, idx)
		else:
			total = "BUST"

	if total == 21 and len(hand) == 2:
		total = "BLACKJACK"

		if type(idx) == type(1):
			if player.split_aces[idx]:
				total = 21

	return total

def join(list):
	s = ''
	for item in list:
		s += str(item) + ' '

	return s[:-1]

def is_string(val):
	return type(val) == type("")

def ones_to_aces(hand):
	new = []
	for card in hand:
		if card == 1:
			new.append('A')
		else:
			new.append(card)

	return new

def is_double_aces(hand):
	if hand[0] == 1 or is_string(hand[0]) and hand[0] == 'A':
		if hand[1] == 1 or is_string(hand[1]) and hand[1] == 'A':
			return True
	return False

def has_soft_17(hand, get_total):
	for card in hand:
		if card == 1:
			return get_total(hand) == 17
		if is_string(card) and card == 'A':
			return get_total(hand) == 17

	return False

def start():
	game = Game()
	player = Player()
	dealer = Dealer()

	game.shuffle()

	while game.playing == True:
		if player.money < 1:
			game.playing = False
			continue

		# bet
		print("************")
		print("$ %.2f | Bet: " % player.money, end="")
		try:
			player.bet = int(input())
			if player.bet == -1:
				break
			if player.bet > player.money:
				continue
			
		except ValueError:
			continue

		player.bets[0] = player.bet

		#deal
		player.hands.append([game.next_card()])
		dealer.hand.append(game.next_card())
		player.hands[0].append(game.next_card())
		dealer.hand.append("?")

		print("************")
		print("Dealer: ", join(dealer.hand))

		# player's turn
		hands = len(player.hands)
		x = 0
		while x < hands:
			while True:
				if len(player.hands[x]) < 2:
					player.hands[x].append(game.next_card())

				total = get_total(player.hands[x], x, player)

				print("Hand ",x+1,": ",join(ones_to_aces(player.hands[x]))," ==> ",total, sep="")
				# check for bust and blackjack
				if is_string(total):
					break

				print("(H)it (S)tand (D)ouble down s(P)lit: ", end="")
				
				try:
					choice = str(input()).upper()
				except ValueError:
					continue
				
				print()

				if choice == "Q":
					print("Bye.")
					return

				if choice == "H":
					player.hands[x].append(game.next_card())
					continue

				if choice == "S":
					break

				if choice == "D":
					total = get_total(player.hands[x])
					if player.bets[x] * 2 > player.money:
						print("You don't have the money to cover that bet.")
						continue

					if len(player.hands[x]) != 2 or total < 9 or total > 11:
						print("Can only double down on first 2 cards with a total of 9, 10, or 11.")
						continue
					else:
						player.hands[x].append(game.next_card())
						player.bets[x] *= 2
						total = get_total(player.hands[x])
						print("Hand ",x+1,": ",join(ones_to_aces(player.hands[x]))," ==> ",total, sep="")
						break

				if choice == "P":
					if can_split(player.hands[x], player) == False:
						print("Can only split pairs on first 2 cards.")
					else:
						if is_double_aces(player.hands[x]):
							player.split_aces[x] = True
							player.split_aces[x+1] = True

						player.hands.append([player.hands[x].pop()])

						if is_string(player.hands[x][0]) == False and player.hands[x][0] == 1:
							player.hands[x][0] = 'A'

						hands = len(player.hands)
						player.bets[x+1] = player.bet
						continue
			x += 1

		# dealer's turn
		print("------------")
		dealer.hand[1] = game.next_card()

		while True:
			total = get_total(dealer.hand)
			print("Dealer: ", join(ones_to_aces(dealer.hand)), " --> ", total, sep="")

			if type(total) == type(1):
				if total < 17:
					dealer.hand.append(game.next_card())
					continue

				if total == 17 and has_soft_17(dealer.hand, get_total):
					print("Dealer hits soft 17")
					dealer.hand.append(game.next_card())
					continue

				print("Dealer stands on ", total)
				break
			else:
				break

		# pay out
		total_d = get_total(dealer.hand)
		winnings = 0

		for i in range(len(player.hands)):
			hand = player.hands[i]
			total = get_total(hand)

			if is_string(total) and total == "BLACKJACK" and player.split_aces[i] == True:
				total = 21

			if is_string(total) and total == "BLACKJACK":
				if is_string(total_d) and total_d == "BLACKJACK":
					continue
				else:
					winnings += player.bets[i] * 1.5
			elif is_string(total_d) and total_d == "BLACKJACK":
				winnings -= player.bets[i]


			elif is_string(total) and total == "BUST":
				if is_string(total_d) and total_d == "BUST":
					continue
				else:
					winnings -= player.bets[i]
			elif is_string(total_d) and total_d == "BUST":
				winnings += player.bets[i]


			elif total == total_d:
				continue
			elif total > total_d:
				winnings += player.bets[i]
			else:
				winnings -= player.bets[i]

		player.money += winnings
		print("------------")
		if winnings > 0:
			print("Winner")
		elif winnings < 0:
			print("Loser")
		else:
			print("Push")

		# clear state
		player.hands = []
		player.bets = [0,0,0,0]
		player.split_aces = [False,False,False,False]
		player.bet = 0
		dealer.hand = []

	print("Bye.")

#--------------------------------------
start()