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
	for each in array_of_lines:
		if length(each) > max_line_length:
			max_line_length = length(each)
	WD=get_term_width()
	SZ=int(WD/max_line_length)
	for i in array_of_lines:
		for j in range(1,length(array_of_lines[i])):
			print("{0:SZ}".format("x"), end='')
	print("")

## 
## initialization
## 
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

