# Trivia-style hangman
# Yahia Nasssab


#
#
#
# Current known bugs:
    # NONE
#	
#
#


## SETUP


# Required imports

from tkinter import Frame, Label, Tk, ttk
# from PIL import Image, ImageTk, ImageSequence
from random import choice as random_choice


# Each of the word banks based on chosen difficulty

from word_bank_normal import bank as normal_bank
from word_bank_hard import bank as hard_bank
from word_bank_drunk import bank as drunk_bank



# Set up the window

hangmanRoot = Tk()

hangmanRoot.title("Hangman Trivia")

windowWidth = 850
windowHeight = 500
hangmanRoot.geometry("{}x{}".format(windowWidth, windowHeight))

# Create pages
game_page = Frame()
game_page.place(x = 0, y =0, relwidth = 1, relheight = 1)
# game_page.pack(fill = "both", expand = True)

home_page = Frame()
home_page.place(x = 0, y =0, relwidth = 1, relheight = 1)
# home_page.pack(fill = "both", expand = True)



# Minor bug fixes

# Prevents the debugger from screaming at me
class WordBank:
    word_bank = {"":""}

# Unbinds the spacebar from every button (creates a dummy button that doesn't appear on the root)
no_space_button = ttk.Button(hangmanRoot)
no_space_button.unbind_class("TButton", "<Key-space>")
    
    
    
# Choose difficulty
def chosen_difficulty(difficulty):
        
    if difficulty == "normal":
        WordBank.word_bank = normal_bank.copy()
    
    elif difficulty == "hard":
        WordBank.word_bank = hard_bank.copy()
        
    elif difficulty == "drunk":
        WordBank.word_bank = drunk_bank.copy()
   
    # Make the game page visible above the home page
    game_page.lift()
        
    # Starts the game
    global new_game
    new_game = NewGame()  

    # Allows input from the player
    global stop_input
    stop_input = False
    
    return






## CREATING WIDGETS



# Label commands:

# Create a function for the button to close the app
def finished():
    hangmanRoot.destroy()
    hangmanRoot.quit()
    return

# Button to return to home screen, with the ability to be bound to a key
def main_menu(event = None):
    
    global strikeLabel
    global scoreLabel
    
    # For resetting the game
    new_game.wordLabel.destroy()
    new_game.updateLabel.destroy()
    new_game.clueLabel.destroy()
    new_game.wrongLabel.destroy()
    strikeLabel.destroy()
    scoreLabel.destroy()
    
    # Brings the home page in front of the game page
    home_page.lift()
    
    return




# Create some text on the home page for the user

difficultyLabel = Label(home_page, text = "Choose your difficulty:")
tipLabel = Label(home_page, text = "Tip: you can use your keyboard to guess letters")

# A button to return to the home page
home_button = ttk.Button(game_page, text = "Main Menu", command = main_menu)

# Button to close the app from the home page
exit_button_home = ttk.Button(home_page, text = "Exit", command = finished)

# Close the app from the gome page
exit_button_game = ttk.Button(game_page, text = "Exit", command = finished)

# Display the high score
global highScoreLabel
global high_score
highScoreLabel = Label(game_page, text = "High Score: 0")
high_score = 0

# Pack each label onto the root

home_button.pack(side = "left", anchor = "s")
exit_button_home.pack(side = "right", anchor = "s")
exit_button_game.pack(side = "right", anchor = "s")
difficultyLabel.pack(side = "top", pady = 20)
tipLabel.pack(side = "bottom", pady = 50)
highScoreLabel.pack(side = "bottom", pady = 50)


# Bind the 'Esc' key to the Main Menu button
hangmanRoot.bind("<Escape>", lambda event: main_menu(event = event))




# Let the window display explanatory text when hovering over a button

explainLabel = Label(home_page, text = "", font = "Times 12")

class HoverButton(ttk.Button):
    def __init__(self, master, explain_text = "", **kw):
        ttk.Button.__init__(self, master = master, **kw)
        self.explain_text = explain_text
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        global explainLabel
        explainLabel['text'] = self.explain_text
        
    def on_leave(self, event):
        global explainLabel
        explainLabel['text'] = ""


        
# Create a button for each difficulty

normalButton = HoverButton(home_page, 
                               explain_text = "To test your trivia knowledge. One clue - one possible answer",
                               text = "Normal", 
                               command = lambda difficulty = "normal": chosen_difficulty(difficulty))
normalButton.pack(side = "top", pady = 5)


hardButton = HoverButton(home_page,
                             explain_text = "For those who seek a greater challenge. Trivia-style: one clue - one possible answer",
                             text = "Hard", 
                             command = lambda difficulty = "hard": chosen_difficulty(difficulty))
hardButton.pack(side = "top", pady = 5)


drunkButton = HoverButton(home_page, 
                              explain_text = "More akin to classic Hangman",
                              text = "Drunk", 
                              command = lambda difficulty = "drunk": chosen_difficulty(difficulty))
drunkButton.pack(side = "top", pady = 5)

# Place the explantory label
explainLabel.pack(side = "top", pady = 15)



# Make the home page visible above the game page
home_page.lift()


## USER INPUT


# Create a button for each letter

def NormalButton(buttonText, xCoord, yCoord):
    
    """
    buttonText: string object to be displayed on button.
    xCoord: integer indicating x-coordinate for button on window
    yCoord: integer indicating y-coordinate for button on window
    """
    button = ttk.Button(game_page, text = buttonText, # re-initiates the player_input function with the chosen letter
                                                             command = lambda letter = buttonText: player_input(letter))
    button.place(x = xCoord, y = yCoord)
    
    return
    

top_button_row = list("QWERTYUIOP")
top_button_xcoord = 37
top_button_ycoord = 250

for letter in top_button_row:
    # Example: create_button("A", 0, 300)
    NormalButton(letter, top_button_xcoord, top_button_ycoord)
    top_button_xcoord += 75

    

middle_button_row = list("ASDFGHJKL")
middle_button_xcoord = 75
middle_button_ycoord = 300

for letter in middle_button_row:
    NormalButton(letter, middle_button_xcoord, middle_button_ycoord)
    middle_button_xcoord += 75
    

    
bottom_button_row = list("ZXCVBNM")    
bottom_button_xcoord = 150
bottom_button_ycoord = 350

for letter in bottom_button_row:
    NormalButton(letter, bottom_button_xcoord, bottom_button_ycoord)
    bottom_button_xcoord += 75
    

# Allow user keyboard input in addition to GUI button usage
def bind_key(key_symbol):
    # Binds a key to player_input call with the letter on the key as an argument
    hangmanRoot.bind(key_symbol, lambda event, letter = key_symbol: player_input(letter))
    return
    
# Bind each appropriate key to corresponding letter        
full_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
for letter in list(full_alphabet):
    bind_key(letter)

    
        
    
    
    
## MAIN GAME FUNCTIONALITY



# Randomly chooses the word
def choose_word():
    # preserves the original word so as to show it after a player fails to guess correctly
    global word_choice
    
    # Imported from random
    word_choice = random_choice(list(WordBank.word_bank.keys()))
    return word_choice


class NewGame():
    def __init__(self, wonGame = False):
        
        # Converts word to list for ease of manipulation
        word = list( choose_word() )
                
        # Creates a series of blanks corresponding to letters in word
        display_list = ["_ " for letter in word]
        
        for character in word:
            
            # Eliminate spaces and special characters
            if not character.isalpha():
                # Find the position of the character in target word
                character_location = word.index(character)
                # Replace the '_ ' in the display with the character
                display_list[character_location] = character + " "
                # Removes the character from the word so it isn't iterated over again
                word[character_location] = None
                   
                    
        # Allow word to be displayed as a string
        display_word = ""
        for letter in display_list:
            display_word += letter
            
        
        # Create a bank so repeat letters aren't re-inputted
        letter_bank = set()    
           
            
        # Where clue will display
        clueLabel = Label(game_page,
                         # Retrieves the chosen word from the word bank
                          text = WordBank.word_bank.get(word_choice),
                         font = "Times 12")
        clueLabel.pack(side = "top", pady = 15)
                        
            
        # Where output will display
        wordLabel = Label(game_page, 
                          text = display_word,
                          font = "Times 12")
        wordLabel.pack(side = "top", pady = 15)
                        

        # Where other text will display
        updateLabel = Label(game_page, 
                            text = "Good luck!",
                            font = "Times 12")
        updateLabel.pack(side = "top", pady = 15)
        
        
        # Shows the player the wrong letters they guessed
        wrongLabel = Label(game_page,
                           text = "Wrong guesses:",
                           font = "Times 12")
        wrongLabel.pack(side = "top", pady = 15)
        
        
        # If the player loses the game, or if new game, set each count to 0
        if wonGame == False:
            
            # reset strike count
            global strike_count
            strike_count = 0
            
            # Where the current strike count will display
            global strikeLabel
            strikeLabel = Label(game_page, 
                                text = "Strikes: 0 of 7",
                                font = "Times 12")
            strikeLabel.place(x = 37, y = 200)
            
            
            # The score the player has acheived
            global player_score
            player_score = 0
            
            # Prints the score
            global scoreLabel
            scoreLabel = Label(game_page, 
                                text = "Score: 0",
                                font = "Times 12")
            scoreLabel.place(x = 700, y = 200)
            
            
        # Attributes all objects to class member for global use
        # (Makes it easy to see which objects are in this class when done at the bottom)
        self.word = word
        self.display_list = display_list
        self.display_word = display_word
        self.letter_bank = letter_bank
        self.wordLabel = wordLabel
        self.updateLabel = updateLabel
        self.clueLabel = clueLabel
        self.wrongLabel = wrongLabel
        
        return

    

# Removes GUI elements of an old game, destroys old game, and starts new game
def reset_game(wonGame = False):
    
    global word_choice
    global new_game
    global stop_input
         
    
    new_game.wordLabel.destroy()
    new_game.updateLabel.destroy()
    new_game.clueLabel.destroy()
    new_game.wrongLabel.destroy()
    # If the player lost the game, reset the strike count:
    if wonGame == False:
        strikeLabel.destroy()
        scoreLabel.destroy()
    
    del new_game
    
    stop_input = False
        
    # Determines whether the strike count is reset or not
    if wonGame == False:
        new_game = NewGame()
    else:
        new_game = NewGame(wonGame = True)
    
    return




# Processes user input   
def player_input(input_letter):
    
    global new_game
    global stop_input
    global strike_count
    global player_score
    global strikeLabel
    global highScoreLabel
    global high_score
    
    # Prevents player input while game is resetting
    if stop_input:
        return
    
    # Clear the update label
    new_game.updateLabel['text'] = ""
    
    letterFound = True
    
    while letterFound:                    
                        
        # Ignore if player doesn't input anything
        if input_letter == "":
            return
        # Accept only letters
        if not input_letter.isalpha():
            new_game.updateLabel['text'] = "Enter letters only, please"
            return
        
        # Reject repeat letters
        if input_letter.upper() in new_game.letter_bank:
            new_game.updateLabel['text'] = "You already guessed that letter!"
            return
                
        # Convert letter to capital (necessary if player is using keyboard without caps lock)
        input_letter = input_letter.upper()
        
        # Strike is incurred if letter not found in word
        incurStrike = True

        # Loop through the word to catch all instances of the chosen letter
        letterInputted = True

        while letterInputted:
            
            # Guards against repeat letters
            new_game.letter_bank.add(input_letter)            
            
            if input_letter in new_game.word:

                # Find the position of the letter in target word
                letter_location = new_game.word.index(input_letter)
                # Replace the '_ ' in the display with the letter
                new_game.display_list[letter_location] = input_letter + " "
                # Removes the letter from the target word so it isn't iterated over again
                new_game.word[letter_location] = None       
                # Give the player a point
                player_score += 1
                # Update the current score
                scoreLabel['text'] = " Score: " + str(player_score)
                # Update the high score
                if player_score > high_score:
                    highScoreLabel['text'] = "High Score: " + str(player_score)
                    high_score = player_score
                # Ensures a strike doesn't occur
                incurStrike = False
                # Repeat for every occurence of the letter
                continue 

            if incurStrike:
                strike_count += 1
                # Tell the player immediately how many strikes they have
                new_game.updateLabel['text'] = "Nope! Current strike count: " + str(strike_count) + " of 7"
                # Continuously show the running total
                strikeLabel['text'] = "Strikes: " + str(strike_count) + " of 7"
                # Tell the player which letter they guess wrong
                if new_game.wrongLabel['text'] == "Wrong guesses:":
                    # No comma if first letter
                    new_game.wrongLabel['text'] += " " + input_letter.upper()
                else:
                    # Put a comma after every letter
                    new_game.wrongLabel['text'] += ", " + input_letter.upper()

            letterInputted = False

        # Allow word to be displayed as a string
        new_game.display_word = ""
        for letter in new_game.display_list:
            new_game.display_word += letter

        # Update the GUI
        new_game.wordLabel['text'] = new_game.display_word
        
        
        if strike_count >= 7:       
            
            # Reveal word if player loses     
            new_game.wordLabel['text'] = word_choice
            
            # Tell the player they lost :(
            new_game.updateLabel['text'] = "Game over :(  \n Starting new game in 3 seconds."
            # Prevents player input while game is resetting
            stop_input = True            
            # Start new game after 3 seconds (enough time to see the word they missed)
            game_page.after(3000, reset_game)

        if "_ " not in new_game.display_list:
            
            # Removes the word from the word bank so it isn't iterated over again
            WordBank.word_bank.pop(word_choice)
            
            # Stops the game if the player has answered all possible clues
            if WordBank.word_bank == {}:
                new_game.updateLabel['text'] = "Congratulations! You've completed all the possible clues in this bank! \n Returning to Main Menu in 5 seconds."
                stop_input = True
                game_page.after(5000, main_menu)
                return
            
            # Tell the player they won! :D
            new_game.updateLabel['text'] = "You win! :D Starting new game in 1 second."
            
            # Gives the player points based on how short the word was
            if len(word_choice) <= 5:
                player_score += 25
            elif 5 < len(word_choice) <= 10:
                player_score += 20
            elif 10 < len(word_choice) <= 15:
                player_score += 15
            elif 15 < len(word_choice) <= 20:
                player_score += 10
            elif len(word_choice) > 20:
                player_score += 5
            # Update the player on their score
            scoreLabel['text'] = " Score: " + str(player_score)
            
            # Update the high score
            if player_score > high_score:
                highScoreLabel['text'] = "High Score: " + str(player_score)
                high_score = player_score
            
            # Prevents player input while game is resetting
            stop_input = True
            # Start new game after 1 second
            game_page.after(1000, lambda wonGame = True: reset_game(wonGame = wonGame))
        
        letterFound = False
        
    return




# Keeps the GUI open until the user closes it
hangmanRoot.mainloop()