#!/usr/bin/python3

import os
import re
import random
import string

## 
## global constants, variables, lists, etc.
## 

TPUT="/usr/bin/tput"
CLEAR="clear"

WORD_LIST_FILE="wordle-PLAY.txt"
VALID_WORDLIST="wordle-VALID.txt"
#WORD_LIST_FILE="list_A.txt"
#VALID_WORDLIST="list_B.txt"

VALID_WORDS	= []
WORDS		= []
USAGE_TEXT	= ["NOTE: misplaced # reflects occurrences; extras are marked wrong"]
SOLVED_MOVES		= {}
COUNT_LINE_GUESS	= {}
PICK_LETTER_COUNT	= {}
CORRECT_ARRAY		= {}
MISPLACED_ARRAY		= {}
WRONG_ARRAY			= {}
LETTER_STATUS		= {}
CURRENT_GUESS_ARRAY	= {}
CORRECT_TO_LABEL	= {}
OCCUR_TO_LABEL		= {}
LABELED_MISPLACED	= {}
ALL_GUESSES_FORMATTED	= {}
SOLVED_RATIO		= {}

VALID_COUNT=0
WCOUNT=0
VALID_BONUS_COUNT=0

KEYBOARD=["qwertyuiop", "asdfghjkl", "zxcvbnm"]
ALPHABET=["abcdefghi", "jklmnopqr", "stuvwxyz"]

## FIX these for Python
## AWK :: 0 == false, 1 == true
DEBUG		= False
DEBUG1		= False
DEBUG2		= False
STATS		= False
PLAYING		= True
SOLVED		= False
## Print Centered (1) or Center-Justified (0) (DEFAULT)
CENTER		= False
GUIDE		= True
USAGE		= True
## Display post-board/pre-prompt help: 0=NO,1=YES
HELP		= False
OPTIONS		= False
## Either print QWERTY (True) or ALPHABETIC (False)
USE_KEYBOARD= True

## Initialize default counts and values
TITLE			= [ "Wordle (Python CLI)" ]
DEFAULT_SEED	= 23
GAMES_PLAYED	= 0
GAMES_SOLVED	= 0
NUM_GUESSES		= 0
CORRECT_THIS_LINE	= 0

## Delimiters and Separators
GUESS_LD="["
GUESS_RD="]"
GSEP="  "
KEY_LD="["
KEY_RD="]"
KSEP="  "
CORRECT_TAG_DELIM	= "_"
MISPLACED_TAG_DELIM	= "-"
WRONG_TAG_DELIM		= "*"
BASIC_TAG_DELIM		= " "
BLANK_TAG_DELIM		= " "


## 
## functions
## 

def import_validwords(WFILE):
	global VALID_COUNT
	with open(WFILE, 'r') as f:
		for line in f:
			word = line.rstrip()
			VALID_COUNT += 1
			VALID_WORDS.append(word)
	f.close()

def import_wordlist(WFILE):
	global WCOUNT
	global VALID_COUNT
	global VALID_BONUS_COUNT
	with open(WFILE, 'r') as f:
		for line in f:
			WCOUNT += 1
			word = line.rstrip()
			WORDS.append(word)
			if word not in VALID_WORDS:
				VALID_COUNT += 1
				VALID_BONUS_COUNT += 1
				VALID_WORDS.append(word)
	f.close()

def get_term_width():
	verify_tput_cmd="[ -x " + TPUT + " ]"
	get_cols_cmd=TPUT + " cols"
	tput_found_stat = os.system(verify_tput_cmd)
	if tput_found_stat == 0:
		tput_cols_process = os.popen(get_cols_cmd)
		WIDTH = int(tput_cols_process.read().rstrip())
	else:
		WIDTH = 80
	return WIDTH

#def print_left_justified(array_of_lines):
#	max_line_length=0
#	NL=len(array_of_lines)
#	for each in array_of_lines:
#		if len(each) > max_line_length:
#			max_line_length = len(each)
#	termWidth = get_term_width()
#	SZ=int( termWidth / max_line_length )
#	for i in array_of_lines:
#		for j in range(0,len(array_of_lines[i])):
#			print("{0:SZ}".format(array_of_lines[i][j]), end='')
#		print("")

def print_center_justified(array_of_lines):
	max_line_length = 0
	NL = len(array_of_lines)
	for i in range(0,NL):
		if len(array_of_lines[i]) > max_line_length:
			max_line_length = len(array_of_lines[i])
	termWidth = get_term_width()
	MARGIN=int((termWidth - max_line_length)/2)
	for i in range(0,NL):
		for j in range(0,MARGIN):
			print(" ", end='')
		print("{}".format(array_of_lines[i]))

def print_centered(array_of_lines):
	termWidth=get_term_width()
	NL=len(array_of_lines)
	for i in range(0,NL):
		LILEN = len(array_of_lines[i])
		MARGIN = int((termWidth - LILEN)/2)
		for j in range(0,MARGIN):
			print(" ", end='')
		print("{}".format(array_of_lines[i]))

def formatted_letter(letter):
	global CORRECT_ARRAY
	global MISPLACED_ARRAY
	global WRONG_ARRAY
	if CORRECT_ARRAY[letter]:
		val = correct_tag(letter)
	elif MISPLACED_ARRAY[letter]:
		val = misplaced_tag(letter)
	elif WRONG_ARRAY[letter]:
		val = wrong_tag(letter)
	else:
		val = basic_tag(letter)
	return val

def map_letters(letter_array):
	global KEY_LD
	global KEY_RD
	global KSEP
	global LETTER_STATUS
	for i in range(0, len(letter_array)):
		line=""
		LA    = letter_array[i]
		LILEN = len(LA)
		for j in range (0, LILEN - 1):
			val = formatted_letter(LA[j])
			line = line + KEY_LD + val + KEY_RD + KSEP
		val = formatted_letter( LA[LILEN - 1] )
		line = line + KEY_LD + val + KEY_RD
		LETTER_STATUS[i] = line

def print_letters():
	if USE_KEYBOARD:
		LETTER_FORMAT = map_letters(KEYBOARD)
	else:
		LETTER_FORMAT = map_letters(ALPHABET)
	if CENTER:
		print_centered(LETTER_STATUS)
	else:
		print_center_justified(LETTER_STATUS)

def print_title():
	print_centered(TITLE)

def print_guide():
	print("GUIDE:")
	print("  [{}]  ==  CORRECT letter".format(correct_tag("a")))
	print("  [{}]  ==  Misplaced letter (elsewhere in line)".format(misplaced_tag("a")))
	print("  [{}]  ==  Wrong letter (not in puzzle)".format(wrong_tag("a")))
	print("  [{}]  ==  Untried letter".format(basic_tag("a")))
	print("")

def print_usage():
	global USAGE_TEXT
	print_center_justified(USAGE_TEXT)

def print_options():
	print("OPTIONS:")
	print("  0 == Quit")
	print("  1 == Use QWERTY mapping for used letters status (DEFAULT)")
	print("  2 == Use ALPHABETIC mapping for used letters status")
	print("  3 == Toggle pre-board wordlist info and guide")
	print("  8 == Toggle centered and justified display")
	print("  9 == Toggle DEBUG mode (caution: reveals word pick)")
	print("")
	disable_options()
	enable_guide()

def clear():
	os.system(CLEAR)

def pick_word(WORD_ARRAY):
	wordcount = len(WORD_ARRAY)
	rand_pick = random.randint(0, wordcount-1)
	picked_word = WORD_ARRAY[rand_pick]
	init_pick_tracking()
	return picked_word
	
def init_pick_tracking():
	NUM_GUESSES=0
	current_guess_array = {}
	for letter in string.ascii_lowercase:
		CORRECT_ARRAY[letter] = 0
		MISPLACED_ARRAY[letter] = 0
		WRONG_ARRAY[letter] = 0
		PICK_LETTER_COUNT[letter] = 0
	for i in range(0,6):
		for j in range(0,5):
			current_guess_array[j] = blank_tag()
		current_guess_string = guess_line_array_to_string(current_guess_array)
		add_guess_line_to_board(current_guess_string,i)

def init_stats():
	global GAMES_PLAYED
	global GAMES_SOLVED
	global SOLVED_MOVES
	global SOLVED_RATIO
	GAMES_PLAYED = 0
	GAMES_SOLVED = 0
	for i in range(1,7):
		SOLVED_MOVES[i] = 0
		SOLVED_RATIO[i] = 0.0

def register_solution():
	global SOLVED
	global GAMES_SOLVED
	global SOLVED_MOVES
	if SOLVED:
		GAMES_SOLVED += 1
		SOLVED_MOVES[NUM_GUESSES] += 1
		SOLVED = False

def print_stats():
	global SOLVED_RATIO
	global SOLVED_MOVES
	global GAMES_SOLVED
	print("Games Played: {:6}      Games Solved: {:6}      ({:.2f} %)".format(\
			GAMES_PLAYED, GAMES_SOLVED, (GAMES_SOLVED / GAMES_PLAYED) * 100))
	for i in range(1,7):
		if GAMES_SOLVED == 0:
			ratio = 0.0
		else:
			ratio = "%.1f" % ((SOLVED_MOVES[i]/GAMES_SOLVED)*100)
		SOLVED_RATIO[i] = ratio
		print("{}:{} ({}%)  ".format(i,SOLVED_MOVES[i],ratio), end='')
	print("")
	print("")

def init_this_guess_tracking():
	global CORRECT_THIS_LINE
	global CURRENT_GUESS_ARRAY
	global CORRECT_TO_LABEL
	global OCCUR_TO_LABEL
	global LABELED_MISPLACED
	CORRECT_THIS_LINE = 0
	for i in range(0,5):
		CURRENT_GUESS_ARRAY[i] = blank_tag()
	for letter in string.ascii_lowercase:
		CORRECT_TO_LABEL[letter] = 0
		OCCUR_TO_LABEL[letter] = 0
		LABELED_MISPLACED[letter] = 0

def init_letters_in_current_guess():
	global COUNT_LINE_GUESS
	for letter in string.ascii_lowercase:
		COUNT_LINE_GUESS[letter] = 0

def set_options(raw):
	this = int(raw)
	global USE_KEYBOARD
	global GUIDE
	global CENTER
	global DEBUG
	if this == 1:
		USE_KEYBOARD = True
	elif this == 2:
		USE_KEYBOARD = False
	elif this == 3:
		if GUIDE:
			GUIDE = False
		else:
			GUIDE = True
	elif this == 8:
		if CENTER:
			CENTER = False
		else:
			CENTER = True
	elif this == 9:
		if DEBUG:
			DEBUG = False
		else:
			DEBUG = True
	else:
		pass

def disable_usage():
	global USAGE
	USAGE = False

def enable_usage():
	global USAGE
	USAGE = True

def disable_guide():
	global GUIDE
	GUIDE = False

def enable_guide():
	global GUIDE
	GUIDE = True

def disable_help():
	global HELP
	HELP = False

def enable_help():
	global HELP
	HELP = True

def disable_options():
	global OPTIONS
	OPTIONS = False

def enable_options():
	global OPTIONS
	OPTIONS = True


def guess_line_array_to_string(array):
	gstring=""
	for i in range(0,5):
		gstring = gstring + GSEP + GUESS_LD + array[i] + GUESS_RD
	return(gstring)

def add_guess_line_to_board(line_string, guess_number):
	global ALL_GUESS_FORMATTED
	ALL_GUESSES_FORMATTED[guess_number] = line_string

def correct_tag(letter):
	global CORRECT_TAG_DELIM
	formatted = CORRECT_TAG_DELIM + letter.upper() + CORRECT_TAG_DELIM
	return formatted

def misplaced_tag(letter):
	global MISPLACED_TAG_DELIM
	formatted = MISPLACED_TAG_DELIM + letter.upper() + MISPLACED_TAG_DELIM
	return formatted

def wrong_tag(letter):
	global WRONG_TAG_DELIM
	formatted = WRONG_TAG_DELIM + letter.upper() + WRONG_TAG_DELIM
	return formatted

def basic_tag(letter):
	global BASIC_TAG_DELIM
	formatted = BASIC_TAG_DELIM + letter.upper() + BASIC_TAG_DELIM
	return formatted

def blank_tag():
	global BLANK_TAG_DELIM
	formatted = BLANK_TAG_DELIM + " " + BLANK_TAG_DELIM
	return formatted

def mark_correct(letter):
	global CORRECT_ARRAY
	CORRECT_ARRAY[letter] = 1

def mark_misplaced(letter):
	global MISPLACED_ARRAY
	MISPLACED_ARRAY[letter] = 1

def unmark_misplaced(letter):
	global MISPLACED_ARRAY
	MISPLACED_ARRAY[letter] = 0

def mark_wrong(letter):
	global WRONG_ARRAY
	WRONG_ARRAY[letter] = 1

def register_pick(pick):
	global PICK_LETTER_COUNT
	global NUM_GUESSES
	NUM_GUESSES = 0
	for letter in pick:
		PICK_LETTER_COUNT[letter] += 1

def evaluate_guess(guess):
	global CURRENT_WORD
	global VALID_WORDS
	global NUM_GUESSES
	global CORRECT_TO_LABEL
	global OCCUR_TO_LABEL
	global CORRECT_THIS_LINE
	global LABELED_MISPLACED
	global PICK_LETTER_COUNT
	global SOLVED
	current_guess_line_array = {}
	for i in range(0,5):
		current_guess_line_array[i] = blank_tag()
	if ( not (guess in VALID_WORDS) ):
		return 0
	init_this_guess_tracking()
	## Step through 1/2 times to count matches
	for i in range(0,5):
		letter = guess[i]
		COUNT_LINE_GUESS[letter] += 1
		if CURRENT_WORD[i] == letter:
			CORRECT_TO_LABEL[letter] += 1
			CORRECT_THIS_LINE += 1
		OCCUR_TO_LABEL[letter] += 1
	## Step through 2/2 times to format letters
	for i in range(0,5):
		letter = guess[i]
		if PICK_LETTER_COUNT[letter] > 0:
			if CURRENT_WORD[i] == letter:
				mark_correct(letter)
				unmark_misplaced(letter)
				current_guess_line_array[i] = correct_tag(letter)
			elif ( (LABELED_MISPLACED[letter] + CORRECT_TO_LABEL[letter] + 1 )\
					<= ( PICK_LETTER_COUNT[letter] ) ):
				mark_misplaced(letter)
				current_guess_line_array[i] = misplaced_tag(letter)
				LABELED_MISPLACED[letter] += 1
				enable_usage()
			else:
				current_guess_line_array[i] = wrong_tag(letter)
		else:
			mark_wrong(letter)
			current_guess_line_array[i] = wrong_tag(letter)
	guess_string = guess_line_array_to_string(current_guess_line_array)
	add_guess_line_to_board(guess_string, NUM_GUESSES)
	if CORRECT_THIS_LINE == 5:
		SOLVED = True
	NUM_GUESSES += 1
	return 1

def print_guesses():
	print_centered(ALL_GUESSES_FORMATTED)

def print_board():
	if not DEBUG:
		clear()
	print_title()
	if OPTIONS:
		disable_guide()
	if GUIDE:
		print_guide()
	print_guesses()
	print("")
	print_letters()
	print("")
	if OPTIONS:
		print_options()
		enable_guide()
	if USAGE:
		print_usage()

def prompt_user():
	response=input("Enter text, ? for options, or 0 to quit: ")
	return response

def process_response(this):
	global PLAYING
	global HELP
	global GUIDE
	if DEBUG:
		print("DEBUG: (process_response): reponse == '{}'".format(this))
	looksLikeOption = re.compile("^[1-9]$")
	looksLikeWord = re.compile("^[a-z][a-z][a-z][a-z][a-z]$")
	if this == "0":
		PLAYING = False
		if DEBUG1:
			print("DEBUG: (process_response): input = '{}'".format(this))
			print("DEBUG: (process_response): PLAYING = '{}'".format(PLAYING))
		exit()
	elif looksLikeOption.match(this):
		set_options(this)
	elif this == "?":
		enable_options()
		disable_guide()
	elif looksLikeWord.match(this.lower()):
		evaluate_guess(this)

def process_final(this):
	global PLAYING
	looksLikeOption = re.compile("^[1-9]$")
	looksLikeWord = re.compile("^[a-z][a-z][a-z][a-z][a-z]$")
	if this == "0":
		PLAYING = False
		exit()
	elif looksLikeOption.match(this):
		set_options(this)
	elif this == "?":
		enable_options()
		disable_guide()


## 
## initialization
## 
clear()
random.seed()

## 
## main()
## 
init_stats()
import_validwords(VALID_WORDLIST)
import_wordlist(WORD_LIST_FILE)

while PLAYING:
	init_letters_in_current_guess()
	disable_usage()
	CURRENT_WORD = pick_word(WORDS)
	if DEBUG:
		print("Picked word: \"{}\"".format(CURRENT_WORD))
	register_pick(CURRENT_WORD)
	while ( PLAYING and (NUM_GUESSES < 6) and not SOLVED ):
		print_board()
		process_response(prompt_user().lower())
	GAMES_PLAYED += 1
	if SOLVED:
		register_solution()
		disable_guide()
		print_board()
		print_stats()
		print("Congratulations for solving \"{}\". Play again?".format(CURRENT_WORD))
	elif NUM_GUESSES == 6:
		disable_guide()
		print_board()
		response=input("Puzzle not solved in 6 guesses. Reveal word [N|y]? ")
		if response.lower() == "y":
			print("The word was \"{}\". Play again?".format(CURRENT_WORD))
	enable_guide()
	process_final(prompt_user().lower())

