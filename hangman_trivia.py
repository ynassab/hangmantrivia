# Trivia-style hangman
# Yahia Nasssab
# August 2018 (mostly)

# Currently known bugs:
	# - Word bank answers cannot have multiple corresponding clues
# Other future changes:
	# - On-screen keyboard should be packed in a frame so it moves when the window resizes. 
	#	The frame should be centred width-wise and a fixed distance from the top.


## SETUP


from tkinter import Frame, Label, Tk, ttk # GUI elements derived from tkinter module
from random import choice as random_choice

# Each of the word banks based on chosen difficulty
from word_bank_normal import bank as normal_bank
from word_bank_hard import bank as hard_bank
from word_bank_drunk import bank as drunk_bank

# Set up the window
handman_root = Tk()
handman_root.title("Hangman Trivia")
windowWidth = 850
windowHeight = 500
handman_root.geometry("{}x{}".format(windowWidth, windowHeight))

# Create pages
game_page = Frame()
game_page.place(x = 0, y =0, relwidth = 1, relheight = 1)
# game_page.pack(fill = "both", expand = True)

home_page = Frame()
home_page.place(x = 0, y =0, relwidth = 1, relheight = 1)
# home_page.pack(fill = "both", expand = True)

# I think it's a little cleaner to have global variables as class member attributes rather than using the "global" keyword
class Globals():
	pass
# global_vars = GlobalVars()


## Minor bug fixes


class WordBank: # Prevent the debugger from screaming at me because there's no initial word bank
	word_bank = {"":""}
	
# Unbind the spacebar from every button (creates a dummy button that doesn't appear on the root)
no_space_button = ttk.Button(handman_root)
no_space_button.unbind_class("TButton", "<Key-space>")

def chosen_difficulty(difficulty): # Choose difficulty
	
	if difficulty == "normal":
		WordBank.word_bank = normal_bank.copy()
	elif difficulty == "hard":
		WordBank.word_bank = hard_bank.copy()
	elif difficulty == "drunk":
		WordBank.word_bank = drunk_bank.copy()
	
	game_page.lift() # Make the game page visible above the home page
	Globals.new_game = NewGame() # Start the game
	Globals.stop_input = False # Allow input from the player
	
	return


## CREATING WIDGETS


def finished(): # Create a function for the button to close the app
	handman_root.destroy()
	handman_root.quit()
	return

# Button to return to home screen
def main_menu(event = None): # event arg gives ability to be bound to a key
	
	# Reset the game
	Globals.new_game.word_label.destroy()
	Globals.new_game.update_label.destroy()
	Globals.new_game.clue_label.destroy()
	Globals.new_game.wrong_label.destroy()
	Globals.strike_label.destroy()
	Globals.score_label.destroy()
	
	home_page.lift() # Bring the home page in front of the game page
	
	return

# Create some text on the home page for the user
difficultyLabel = Label(home_page, text = "Choose your difficulty:")
tipLabel = Label(home_page, text = "Tip: you can use your keyboard to guess letters")

# Main buttons
home_button = ttk.Button(game_page, text = "Main Menu", command = main_menu) # Return to the home page
exit_button_home = ttk.Button(home_page, text = "Exit", command = finished) # Close the app from the home page
exit_button_game = ttk.Button(game_page, text = "Exit", command = finished) # Close the app from the game page

# Display the high score
Globals.highscore_label = Label(game_page, text = "High Score: 0")
Globals.high_score = 0

# Pack each label onto the root
home_button.pack(side = "left", anchor = "s")
exit_button_home.pack(side = "right", anchor = "s")
exit_button_game.pack(side = "right", anchor = "s")
difficultyLabel.pack(side = "top", pady = 20)
tipLabel.pack(side = "bottom", pady = 50)
Globals.highscore_label.pack(side = "bottom", pady = 50)

handman_root.bind("<Escape>", lambda event: main_menu(event = event)) # Bind the 'Esc' key to the Main Menu button

Globals.explainLabel = Label(home_page, text = "", font = "Times 12") # Let the window display explanatory text when hovering over a button

class HoverButton(ttk.Button):
	def __init__(self, master, explain_text = "", **kw):
		ttk.Button.__init__(self, master = master, **kw)
		self.explain_text = explain_text
		self.bind("<Enter>", self.on_enter)
		self.bind("<Leave>", self.on_leave)
	
	def on_enter(self, event):
		Globals.explainLabel['text'] = self.explain_text
		
	def on_leave(self, event):
		Globals.explainLabel['text'] = ""
		
# Create a button for each difficulty
normalButton = HoverButton(home_page, 
							explain_text = "To test your trivia knowledge. One clue - one possible answer",
							text = "Normal", 
							command = lambda difficulty = "normal": chosen_difficulty(difficulty))
hardButton = HoverButton(home_page,
							explain_text = "For those who seek a greater challenge. Trivia-style: one clue - one possible answer",
							text = "Hard", 
							command = lambda difficulty = "hard": chosen_difficulty(difficulty))
drunkButton = HoverButton(home_page, 
							explain_text = "More akin to classic Hangman",
							text = "Drunk", 
							command = lambda difficulty = "drunk": chosen_difficulty(difficulty))

# Place the home page elements on the window
normalButton.pack(side = "top", pady = 5)
hardButton.pack(side = "top", pady = 5)
drunkButton.pack(side = "top", pady = 5)
Globals.explainLabel.pack(side = "top", pady = 15)

home_page.lift() # Make the home page visible above the game page


## USER INPUT


# Create a button for each letter
def normal_button(buttonText, xCoord, yCoord):
	# buttonText: string object displayed on the button
	# xCoord: x-coordinate (integer) on the window
	# yCoord: y-coordinate (integer) on the window
	button = ttk.Button(game_page, text = buttonText, # Call the player_input function with the chosen letter
						command = lambda letter = buttonText: player_input(letter))
	button.place(x = xCoord, y = yCoord)
	return

top_button_row = "QWERTYUIOP"
top_button_xcoord = 37
top_button_ycoord = 250
middle_button_row = "ASDFGHJKL"
middle_button_xcoord = 75
middle_button_ycoord = 300
bottom_button_row = "ZXCVBNM"
bottom_button_xcoord = 150
bottom_button_ycoord = 350

for letter in top_button_row:
	# Example: create_button("A", 0, 300)
	normal_button(letter, top_button_xcoord, top_button_ycoord)
	top_button_xcoord += 75
for letter in middle_button_row:
	normal_button(letter, middle_button_xcoord, middle_button_ycoord)
	middle_button_xcoord += 75
for letter in bottom_button_row:
	normal_button(letter, bottom_button_xcoord, bottom_button_ycoord)
	bottom_button_xcoord += 75

def bind_key(key_symbol): # Allow user keyboard input in addition to GUI button usage
	# Bind a key to player_input call with the letter on the key as an argument
	handman_root.bind(key_symbol, lambda event, letter = key_symbol: player_input(letter))
	return
	
# Bind each appropriate key to corresponding letter
full_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
for letter in full_alphabet:
	bind_key(letter)


## MAIN GAME FUNCTIONALITY


def choose_word(): # Randomly choose the word
	# preserve the original word so as to show it after a player fails to guess correctly
	Globals.word_choice = random_choice(list(WordBank.word_bank.keys())) # Imported from random
	return Globals.word_choice

class NewGame():
	def __init__(self, wonGame = False):
		
		word = list( choose_word() ) # Convert word to list for ease of manipulation
		display_list = ["_ " for letter in word] # Create a series of blanks corresponding to letters in word
		
		for character in word: # Eliminate spaces and special characters
			if not character.isalpha():
				character_location = word.index(character) # Find the position of the character in target word
				display_list[character_location] = character + " " # Replace the '_ ' in the display with the character
				word[character_location] = None # Removes the character from the word so it isn't iterated over again
		
		# Allow the word to be displayed as a string
		display_word = ""
		for letter in display_list:
			display_word += letter
		
		letter_bank = set() # Create a bank so repeat letters aren't re-inputted
		
		clue_label = Label(game_page, # Where the clue will display
						text = WordBank.word_bank.get(Globals.word_choice), # Retrieve the chosen word from the word bank
						font = "Times 12")
		clue_label.pack(side = "top", pady = 15)
		
		word_label = Label(game_page, # Where output will display
						text = display_word,
						font = "Times 12")
		word_label.pack(side = "top", pady = 15)
		
		update_label = Label(game_page, # Where other text will display
							text = "Good luck!",
							font = "Times 12")
		update_label.pack(side = "top", pady = 15)
		
		wrong_label = Label(game_page, # Show the player the wrong letters they guessed
						text = "Wrong guesses:",
						font = "Times 12")
		wrong_label.pack(side = "top", pady = 15)
		
		if wonGame == False: # If the player loses the game, or if new game, set each count to 0
			Globals.strike_count = 0 # Reset strike count
			Globals.strike_label = Label(game_page, # Where the current strike count will display
								text = "Strikes: 0 of 7",
								font = "Times 12")
			Globals.strike_label.place(x = 37, y = 200)
			Globals.player_score = 0 # The score the player has acheived
			Globals.score_label = Label(game_page, # Print the score
								text = "Score: 0",
								font = "Times 12")
			Globals.score_label.place(x = 700, y = 200)
		
		# Attribute all objects to class member for global use
		# (Perfomed at bottom of declaration to make it apparent which objects are in the class)
		self.word = word
		self.display_list = display_list
		self.display_word = display_word
		self.letter_bank = letter_bank
		self.word_label = word_label
		self.update_label = update_label
		self.clue_label = clue_label
		self.wrong_label = wrong_label
		return

def reset_game(wonGame = False): # Remove GUI elements of an old game, destroy old game, and start new game
		
	Globals.new_game.word_label.destroy()
	Globals.new_game.update_label.destroy()
	Globals.new_game.clue_label.destroy()
	Globals.new_game.wrong_label.destroy()
	
	if wonGame == False: # If the player lost the game, reset the strike count:
		Globals.strike_label.destroy()
		Globals.score_label.destroy()
	
	del Globals.new_game
	Globals.stop_input = False
	
	if wonGame == False: # Determine if the strike count is reset
		Globals.new_game = NewGame()
	else:
		Globals.new_game = NewGame(wonGame = True)
	
	return

def update_score():
	Globals.score_label['text'] = " Score: " + str(Globals.player_score) # Update the current score
	if Globals.player_score > Globals.high_score: # Update the high score
		Globals.highscore_label['text'] = "High Score: " + str(Globals.player_score)
		Globals.high_score = Globals.player_score
	return

def player_input(input_letter): # Process user input
	
	if Globals.stop_input: # Prevent player input while game is resetting
		return
	
	Globals.new_game.update_label['text'] = "" # Clear the update label
	
	letter_found = True
	while letter_found:
		
		if input_letter == "": # Ignore if player doesn't input anything
			return
		if not input_letter.isalpha(): # Accept only letters
			Globals.new_game.update_label['text'] = "Enter letters only, please"
			return
		
		if input_letter.upper() in Globals.new_game.letter_bank: # Reject repeat letters
			Globals.new_game.update_label['text'] = "You already guessed that letter!"
			return
		
		input_letter = input_letter.upper() # Convert letter to capital (necessary if player is using keyboard without caps lock)
		incur_strike = True # Strike is incurred if letter not found in word
		letter_inputted = True # Loop through the word to catch all instances of the chosen letter

		while letter_inputted:
		
			Globals.new_game.letter_bank.add(input_letter) # Guard against repeat letters
			
			if input_letter in Globals.new_game.word:

				letter_location = Globals.new_game.word.index(input_letter) # Find the position of the letter in target word
				Globals.new_game.display_list[letter_location] = input_letter + " " # Replace the '_ ' in the display with the letter
				Globals.new_game.word[letter_location] = None # Remove the letter from the target word so it isn't iterated over again
				Globals.player_score += 1 # Give the player a point
				update_score() # Update the current score and the high score
				incur_strike = False # Ensure a strike doesn't occur
				continue  # Repeat for every occurence of the letter

			if incur_strike:
				Globals.strike_count += 1
				# Tell the player immediately how many strikes they have
				Globals.new_game.update_label['text'] = "Nope! Current strike count: " + str(Globals.strike_count) + " of 7"
				Globals.strike_label['text'] = "Strikes: " + str(Globals.strike_count) + " of 7" # Continuously show the running total
				if Globals.new_game.wrong_label['text'] == "Wrong guesses:": # Tell the player which letter they guessed wrong
					Globals.new_game.wrong_label['text'] += " " + input_letter.upper() # No comma if it's the first letter
				else:
					Globals.new_game.wrong_label['text'] += ", " + input_letter.upper() # With a comma
			
			letter_inputted = False

		# Allow the word to be displayed as a string
		Globals.new_game.display_word = ""
		for letter in Globals.new_game.display_list:
			Globals.new_game.display_word += letter
		Globals.new_game.word_label['text'] = Globals.new_game.display_word # Update the GUI
		
		if Globals.strike_count >= 7: # If the player loses
			
			Globals.new_game.word_label['text'] = Globals.word_choice # Reveal the word
			lose_wait_time = 3 # seconds
			Globals.new_game.update_label['text'] = "Game over :( \n Starting new game in %d seconds." % lose_wait_time # Tell the player they lost :(
			Globals.stop_input = True # Prevent player input while the game is resetting
			game_page.after(lose_wait_time*1000, reset_game) # Start new game after the wait time (enough time to see the word they missed)

		if "_ " not in Globals.new_game.display_list: # Word correct guessed
			
			WordBank.word_bank.pop(Globals.word_choice) # Remove the word from the word bank so it isn't iterated over again
			
			if WordBank.word_bank == {}: # Stop the game if the player has answered all possible clues
				Globals.new_game.update_label['text'] = """Congratulations! You've completed all the possible clues in this bank!
				\n Click \"Main Menu\" or press the Esc key to attempt another difficulty setting."""
				# Globals.stop_input = True
				# game_page.after(5000, main_menu)
				return
			
			win_wait_time = 1 # seconds (note if this changes to change game text to singular/plural seconds)
			Globals.new_game.update_label['text'] = "You win! :D Starting new game in %d second." % win_wait_time # Tell the player they won! :D
			
			# Give the player points based on how short the word was
			if len(Globals.word_choice) <= 5:
				Globals.player_score += 25
			elif 5 < len(Globals.word_choice) <= 10:
				Globals.player_score += 20
			elif 10 < len(Globals.word_choice) <= 15:
				Globals.player_score += 15
			elif 15 < len(Globals.word_choice) <= 20:
				Globals.player_score += 10
			elif len(Globals.word_choice) > 20:
				Globals.player_score += 5
			
			update_score() # Update the current score and the high score
			Globals.stop_input = True # Prevent player input while the game is resetting
			game_page.after(win_wait_time*1000, lambda wonGame = True: reset_game(wonGame = wonGame)) # Start new game after the wait time
		
		letter_found = False
		
	return

handman_root.mainloop() # Keep the GUI open until the user closes it
