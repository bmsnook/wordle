#!/usr/bin/python3

import os
import random

TPUT="/usr/bin/tput"
CLEAR="clear"

#WORD_LIST_FILE="wordle-PLAY.txt"
#VALID_WORDLIST="wordle-VALID.txt"
WORD_LIST_FILE="list_A.txt"
VALID_WORDLIST="list_B.txt"
TEST_LIST_FILE="list_S.txt"

VALID_WORDS = []
WORDS = []
TEST_ARRAY = []
TEST_2 = {}
TEST_DICT = {}
TEST_LIST = []

VALID_COUNT=0
WCOUNT=0
VALID_BONUS_COUNT=0
TEST_COUNT=0

KEYBOARD=["qwertyuiop", "asdfghjkl", "zxcvbnm"]
ALPHABET=["abcdefghi", "jklmnopqr", "stuvwxyz"]

## FIX these for Python
## AWK :: 0 == false, 1 == true
DEBUG		= True
DEBUG2		= False
STATS		= False
PLAYING		= True
SOLVED		= False
## Print Centered (1) or Center-Justified (0) (DEFAULT)
CENTER		= 0
GUIDE		= True
USAGE		= True
## Display post-board/pre-prompt help: 0=NO,1=YES
HELP		= False
## Either print QWERTY (True) or ALPHABETIC (False)
USE_KEYBOARD= True

## Initialize default counts and values
DEFAULT_SEED=23
GAMES_PLAYED=0
GAMES_SOLVED=0

## Delimiters and Separators
GUESS_LD="["
GUESS_RD="]"
GSEP="  "
KEY_LD="["
KEY_RD="]"
KSEP="  "


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
	if DEBUG2:
		print("DEBUG: get_term_width: verify_tput_cmd = {}".format(verify_tput_cmd))
		print("DEBUG: get_term_width: get_cols_cmd = {}".format(get_cols_cmd))
		print("DEBUG: get_term_width: tput_found_stat = {}".format(tput_found_stat))
	if tput_found_stat == 0:
		tput_cols_process = os.popen(get_cols_cmd)
		WIDTH = tput_cols_process.read().rstrip()
		if DEBUG2:
			print("DEBUG: get_term_width: WIDTH         = \"{}\"".format(WIDTH))
	else:
		WIDTH = 80
	return WIDTH

def print_justified(array_of_lines):
	max_line_length=0
	NL=len(array_of_lines)
	for each in array_of_lines:
		if len(each) > max_line_length:
			max_line_length = len(each)
	WD=get_term_width()
	SZ=int(WD/max_line_length)
	for i in array_of_lines:
		for j in range(1,len(array_of_lines[i])):
			print("{0:SZ}".format("x"), end='')
		print("")

def print_center_justified(array_of_lines):
	max_line_length = 0
	NL = len(array_of_lines)
	for i in range(1,NL):
		if len(array_of_lines[i]) > max_line_length:
			max_line_length = len(array_of_lines[i])
	WD=get_term_width
	MARGIN=int((WD - max_line_length)/2)
	for i in range(1,NL):
		for j in range(1,MARGIN):
			print(" ", end='')
		print("{}".format(array_of_lines[i]))

def print_centered(array_of_lines):
	WD=get_term_width()
	NL=len(array_of_lines)
	for i in range(1,NL):
		LILEN = len(array_of_lines[i])
		MARGIN = int((WD - LILEN)/2)
		for j in range(1,MARGIN):
			print(" ", end='')
		print("{}".format(array_of_lines[i]))

def formatted_letter(letter):
	global CORRECT_ARRAY
	if CORRECT_ARRAY[letter]:
		val = correct_tag(letter)
	elif MISPLACED_LETTER[letter]:
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
	for i in range(1, len(letter_array)):
		line=""
		num_per_line = split(letter_array[i], LA, "")	## CONVERT FROM AWK
		for j in range (0, num_per_line-2):
			val = formatted_letter(LA[j])
			line = line + KEY_LD + val + KEY_RD + KSEP
		val = formatted_letter(LA[num_per_line-1])
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

def print_keyboard():
	print_justified(KEYBOARD)

def print_alpha():
	print_justified(ALPHABET)

def print_guide():
	print("GUIDE:")
	print("  [%s]  ==  CORRECT letter".format(correct_tag("a")))
	print("  [%s]  ==  Misplaced letter (elsewhere in puzzle)".format(misplaced_tag("a")))
	print("  [%s]  ==  Wrong letter (not in puzzle)".format(wrong_tag("a")))
	print("  [%s]  ==  Untried letter".format(basic_tag("a")))
	print("")

def print_usage():
	print("NOTE: only as many letters as occur will be marked misplaced;")
	print("      additional instances will be marked wrong")
	print("")

def print_post_help():
	print("OPTIONS:")
	print("  0 == Quit")
	print("  1 == Use QWERTY mapping for used letters status (DEFAULT)")
	print("  2 == Use ALPHABETIC mapping for used letters status")
	print("  3 == Toggle pre-board wordlist info and guide")
	print("  8 == Toggle centered and justified display")
	print("  9 == Toggle DEBUG mode (caution: reveals word pick)")
	print("")
	HELP  = False
	GUIDE = True

def clear():
	os.system(CLEAR)

def pick_word(WORD_ARRAY):
	wordcount = len(WORD_ARRAY)
	rand_pick = random.randint(0, wordcount-1)
	picked_word = WORD_ARRAY[rand_pick]
	return picked_word
	
def init_pick_tracking():
	NUM_GUESSES=0
	for i in range(97, 123):
		## guessing python has another way to iterate through the alphabet
		letter = "something something with " + i

## 
## initialization
## 
clear()

random.seed()

import_validwords(VALID_WORDLIST)
import_wordlist(WORD_LIST_FILE)

if DEBUG:
	print("==========")
	print("VALID_WORDS:")
	print("==========")
	print(VALID_WORDS)
	print("")
	print("==========")
	print("PLAY WORDS:")
	print("==========")
	print(WORDS)

## 
## main()
## 
print("Hello Wordle.")
print("The terminal width is \"{}\".".format(get_term_width()))

print("#####  TEST 1  #####")
import_validwords(VALID_WORDLIST)
print("There are {} words in VALID_WORDLIST)".format(len(VALID_WORDLIST)))

print("#####  TEST 2  #####")
import_wordlist(WORD_LIST_FILE)
print("There are {} words in WORD_LIST_FILE)".format(len(WORD_LIST_FILE)))

#response=input("Enter a word to search for: ")
#rr = response.strip()
#if rr in VALID_WORDS:
#	print(f"Found \"{rr}\"")
#else:
#	print(f"Could NOT find \"{rr}\"")

print("I picked a word: {}".format(pick_word(WORDS)))
