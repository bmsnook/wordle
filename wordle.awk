#!/usr/bin/awk -f

## NOTE: if "tput" is somewhere other than in "/usr/bin/tput"
##	   then update the path variable TPUT in the BEGIN section

function import_validwords(WFILE) {
	VALID_COUNT=0
	while ( (getline < WFILE) > 0) {
		VALID_COUNT++
		## Store the word in an unsorted array to test if guesses are valid
		VALID_WORDS[$0]
	}
	close(WFILE)
}

function import_wordlist(WFILE) {
	WCOUNT=0
	VALID_BONUS_COUNT=0
	while ( (getline < WFILE) > 0) {
		WCOUNT++
		## Store the word in an enumerated list for randomized picks
		WORDS[WCOUNT]=$0
		if ( !($0 in VALID_WORDS) ) {
			VALID_WORDS[$0]
			VALID_BONUS_COUNT++
		}
	}
	close(WFILE)
}

function get_term_width() {
	verify_tput_cmd=sprintf("[ -x %s ]",TPUT)
	tput_found_stat=system(verify_tput_cmd)
	close(verify_tput_cmd)
	if (tput_found_stat == 0) {
		cmd_cols=sprintf("%s cols",TPUT)
		cmd_cols | getline WIDTH
		close(cmd_cols)
	} else {
		WIDTH=80
	}
	return WIDTH
}

function print_left_justified(array_of_lines) {
	max_line_length=0
	NL=length(array_of_lines)
	for (i=1; i<=NL; i++){
		if (length(array_of_lines[i]) > max_line_length) {
			max_line_length=length(array_of_lines[i])
		}
	}
	WD=get_term_width()
	SZ=int(WD/max_line_length)
	for (i=1; i<=NL; i++){
		for (j=1; j<=length(array_of_lines[i]); j++) {
			printf "%-*s",SZ,substr(array_of_lines[i],j,1)
		}
		printf "\n"
	}
}

function print_center_justified(array_of_lines) {
	max_line_length=0
	NL=length(array_of_lines)
	for (i=1; i<=NL; i++){
		if (length(array_of_lines[i]) > max_line_length) {
			max_line_length=length(array_of_lines[i])
		}
	}
	WD=get_term_width()
	MARGIN=int((WD - max_line_length)/2)
	if (DEBUG2) {printf "int((%s - %s)/2) == %s\n",WD,max_line_length,MARGIN}
	for (i=1; i<=NL; i++){
		if (DEBUG2) {printf "Window width  = \"%s\"\n",WD}
		if (DEBUG2) {printf "MaxLineLength = \"%s\"\n",max_line_length}
		if (DEBUG2) {printf "Output margin = \"%s\"\n",MARGIN}
		if (DEBUG2) {print array_of_lines[i]}
		for (j=1; j<=MARGIN; j++) {
			printf " "
		}
		printf "%s",array_of_lines[i]
		printf "\n"
	}
}

function print_centered(array_of_lines) {
	## ignore max_line_length
	WD=get_term_width()
	NL=length(array_of_lines)
	for (i=1; i<=NL; i++){
		LILEN=length(array_of_lines[i])
		MARGIN=int((WD - LILEN)/2)
		if (DEBUG2) {printf "int((%s - %s)/2) == %s\n",WD,max_line_length,MARGIN}
		if (DEBUG2) {printf "Window width  = \"%s\"\n",WD}
		if (DEBUG2) {printf "MaxLineLength = \"%s\"\n",max_line_length}
		if (DEBUG2) {printf "Output margin = \"%s\"\n",MARGIN}
		if (DEBUG2) {print array_of_lines[i]}
		for (j=1; j<=MARGIN; j++) {
			printf " "
		}
		printf "%s",array_of_lines[i]
		printf "\n"
	}
}

function formatted_letter(letter) {
	if (CORRECT_ARRAY[letter]) {
		val=correct_tag(letter)
	} else if (MISPLACED_ARRAY[letter]) {
		val=misplaced_tag(letter)
	} else if (WRONG_ARRAY[letter]) {
		val=wrong_tag(letter)
	} else {
		val=basic_tag(letter)
	}
	return val
}

function map_letters(letter_array) {
	for (i=1; i<=length(letter_array); i++) {
		line=""
		num_per_line=split(letter_array[i],LA,"")
		for (j=1; j<num_per_line; j++) {
			val=formatted_letter(LA[j])
			line=sprintf("%s%s%s%s%s",line,KEY_LD,val,KEY_RD,KSEP)
		}
		val=formatted_letter(LA[num_per_line])
		line=sprintf("%s%s%s%s",line,KEY_LD,val,KEY_RD)
		LETTER_STATUS[i]=line
	}
}

function print_letters() {
	if (USE_KEYBOARD) {
		LETTER_FORMAT=map_letters(KEYBOARD)
	} else {
		LETTER_FORMAT=map_letters(ALPHABET)
	}
	if (CENTER) {
		print_centered(LETTER_STATUS)
	} else {
		print_center_justified(LETTER_STATUS)
	}
}

function print_title() {
	print_centered(TITLE)
}

function print_guide() {
	printf "GUIDE:\n"
	printf "  [%s]  ==  CORRECT letter\n",correct_tag("a")
	printf "  [%s]  ==  Misplaced letter (elsewhere in puzzle)\n",misplaced_tag("a")
	printf "  [%s]  ==  Wrong letter (not in puzzle)\n",wrong_tag("a")
	printf "  [%s]  ==  Untried letter\n",basic_tag("a")
	printf "\n"
}
function print_usage() {
	print_center_justified(USAGE_TEXT)
}

function print_options() {
	printf "OPTIONS:\n"
	printf "  0 == Quit\n"
	printf "  1 == Use QWERTY mapping for used letters status (DEFAULT)\n"
	printf "  2 == Use ALPHABETIC mapping for used letters status\n"
	printf "  3 == Toggle pre-board wordlist info and guide\n"
	printf "  8 == Toggle centered and justified display\n"
	printf "  9 == Toggle DEBUG mode (caution: reveals word pick)\n"
	printf "\n"
	disable_options()
	enable_guide()
}

function clear() {
	system(CLEAR)
	close(CLEAR)
}

function init_seed() {
	cmd="echo \$RANDOM"
	cmd | getline RANDOM
	close(cmd)
	if (RANDOM ~ /^[0-9]+$/) {
		SEED=RANDOM
	} else {
		SEED=DEFAULT_SEED
	}
}

function pick_word(ENUM_LIST_ARRAY) {
	wordcount=length(ENUM_LIST_ARRAY)
	srand(SEED)
	srand()
	rand_pick=rand()
	picked_number=int(rand_pick*wordcount)
	picked_word=ENUM_LIST_ARRAY[picked_number]
	init_pick_tracking()
	return picked_word
}

function init_pick_tracking() {
	NUM_GUESSES=0
	for (i=97; i<123; i++) {
		letter=sprintf("%c",i)
		CORRECT_ARRAY[letter]=0
		MISPLACED_ARRAY[letter]=0
		WRONG_ARRAY[letter]=0
		PICK_LETTER_COUNT[letter]=0
	}
	for (i=1; i<=6; i++) {
		for(j=1; j<=5; j++) {
			current_guess_array[j]=blank_tag()
		}
		current_guess_string=guess_line_array_to_string(current_guess_array)
		add_guess_line_to_board(current_guess_string,i)
	}
}

function init_stats() {
	GAMES_PLAYED=0
	GAMES_SOLVED=0
	for (i=1; i<=6; i++) {
		SOLVED_MOVES[i]=0
	}
}

function register_solution() {
	if (SOLVED) {
		GAMES_SOLVED++
		SOLVED_MOVES[NUM_GUESSES]++
		disable_set_solved()
	}
}

function print_stats() {
	printf "Games Played: %6s      Games Solved: %6s      (%0.2f %%)\n\n", \
		GAMES_PLAYED,GAMES_SOLVED,(GAMES_SOLVED/GAMES_PLAYED)*100
	printf "Distribution of steps needed for solution:\n"
	for (i=1; i<=6; i++) {
		if (GAMES_SOLVED == 0) {
			ratio=0.0
		} else {
#			ratio=SOLVED_MOVES[i]/GAMES_SOLVED
			ratio=sprintf("%0.1f",(SOLVED_MOVES[i]/GAMES_SOLVED)*100)
		}
		SOLVED_RATIO[i]=ratio
#		printf "%s=%s (%0.2f%%)  ",i,SOLVED_MOVES[i],ratio
		printf "%s:%s (%0s%%)  ",i,SOLVED_MOVES[i],ratio
	}
	printf "\n"
	printf "\n"
}

function init_this_guess_tracking() {
	CORRECT_THIS_LINE=0
	for (i=1; i<=5; i++) {
		CURRENT_GUESS_ARRAY[i]=blank_tag()
	}
	for (i=97; i<123; i++) {
		letter=sprintf("%c",i)
		CORRECT_TO_LABEL[letter]=0
		OCCUR_TO_LABEL[letter]=0
		LABELED_MISPLACED[letter]=0
	}
}

function init_letters_in_current_guess() {
		for (i=97; i<123; i++) {
				letter=sprintf("%c",i)
				COUNT_LINE_GUESS[letter]=0
		}
}

function set_options(this) {
	if (this == 1) {
		enable_keyboard_letter_ordering()
	} else if (this == 2) {
		disable_keyboard_letter_ordering()
	} else if (this == 3) {
		if (GUIDE) {
			disable_guide()
		} else {
			enable_guide()
		}
	} else if (this == 8) {
		if (CENTER) {
			disable_centered_layout()
		} else {
			enable_centered_layout()
		}
	} else if (this == 9) {
		if (DEBUG) {
			disable_debug()
		} else {
			enable_debug()
		}
	} else {
		## do nothing
	} 
}

function disable_usage() {
	USAGE=0
}
function enable_usage() {
	USAGE=1
}

function disable_guide() {
	GUIDE=0
}
function enable_guide() {
	GUIDE=1
}

function disable_options() {
	OPTIONS=0
}

function enable_options() {
	OPTIONS=1
}

function disable_centered_layout() {
	CENTER=0
}
function enable_centered_layout() {
	CENTER=1
}
function disable_keyboard_letter_ordering() {
	USE_KEYBOARD=0
}
function enable_keyboard_letter_ordering() {
	USE_KEYBOARD=1
}
function disable_debug() {
	DEBUG=0
}
function enable_debug() {
	DEBUG=1
}

function disable_set_solved() {
	SOLVED=0
}
function enable_set_solved() {
	SOLVED=1
}

function disable_playing() {
	PLAYING=0
}

function guess_line_array_to_string(array) {
	gstring=""
	for (k=1; k<5; k++) {
		gstring=sprintf("%s%s%s%s%s",gstring,GSEP,GUESS_LD,array[k],GUESS_RD)
	}
	gstring=sprintf("%s%s%s%s%s",gstring,GSEP,GUESS_LD,array[5],GUESS_RD)
	return(gstring)
}

function add_guess_line_to_board(line_string, guess_number) {
	ALL_GUESSES_FORMATTED[guess_number]=line_string
}

function correct_tag(letter) {
	formatted=sprintf("%s%s%s",CORRECT_TAG_DELIM,toupper(letter),CORRECT_TAG_DELIM)
	return formatted
}

function misplaced_tag(letter) {
	formatted=sprintf("%s%s%s",MISPLACED_TAG_DELIM,toupper(letter),MISPLACED_TAG_DELIM)
	return formatted
}

function wrong_tag(letter) {
	formatted=sprintf("%s%s%s",WRONG_TAG_DELIM,toupper(letter),WRONG_TAG_DELIM)
	return formatted
}

function basic_tag(letter) {
	formatted=sprintf("%s%s%s",BASIC_TAG_DELIM,toupper(letter),BASIC_TAG_DELIM)
	return formatted
}

function blank_tag() {
	formatted=sprintf("%s %s",BLANK_TAG_DELIM,BLANK_TAG_DELIM)
	return formatted
}

function mark_correct(letter) {
	CORRECT_ARRAY[letter]=1
}
	
function mark_misplaced(letter) {
	MISPLACED_ARRAY[letter]=1
}
	
function unmark_misplaced(letter) {
	MISPLACED_ARRAY[letter]=0
}
	
function mark_wrong(letter) {
	WRONG_ARRAY[letter]=1
}

function register_pick(pick) {
	NUM_GUESSES=0
	split(pick,pick_as_array,"")
	for (i=1; i<=5; i++) {
		letter=pick_as_array[i]
		PICK_LETTER_COUNT[letter]++
	}
	if (DEBUG) {
		for (i=97; i<123; i++) {				## IN DEBUG
			lett=sprintf("%c",i)				## IN DEBUG
			if (PICK_LETTER_COUNT[lett] > 0) {	## IN DEBUG
				printf "DEBUG: (reg_pick): Count of \"%s\" = \"%s\"\n",lett,PICK_LETTER_COUNT[lett]
			}									## IN DEBUG
		}										## IN DEBUG
	}  ## END DEBUG
}

function evaluate_guess(guess) {
	if ( !(guess in VALID_WORDS) ) { 
		return 0
	} 
	init_this_guess_tracking()
	NUM_GUESSES++
	split(CURRENT_WORD,pick_as_array,"")
	split(guess,guess_as_array,"")
	## 
	## Step 1/2 through the guess to count matches
	## 
	for (i=1; i<=5; i++) {
		letter=guess_as_array[i]
		COUNT_LINE_GUESS[letter]++
		if (pick_as_array[i] == guess_as_array[i]) {
			CORRECT_TO_LABEL[letter]++
			CORRECT_THIS_LINE++
		}
		OCCUR_TO_LABEL[letter]++
	}
	if (DEBUG) {									## IN DEBUG
		printf "Comparing \"%s\"  <==>  \"%s\"\n",CURRENT_WORD,guess
		for (i=97; i<123; i++) {					## IN DEBUG
			lett=sprintf("%c",i)					## IN DEBUG
			if (PICK_LETTER_COUNT[lett] > 0) {		## IN DEBUG
				printf "DEBUG: (eval): \"%s\" :: PLC=%s ;; C2L=%s ;; O2L=%s ;;",lett,PICK_LETTER_COUNT[lett],CORRECT_TO_LABEL[lett],OCCUR_TO_LABEL[lett]
				printf " COR=%s ;; MIS=%s ;; WRO=%s\n",CORRECT_ARRAY[lett],MISPLACED_ARRAY[lett],WRONG_ARRAY[lett]					## IN DEBUG
			}										## IN DEBUG
		}											## IN DEBUG
	}	## END DEBUG
	## 
	## Step 2/2 through the guess to format letters
	## 
	for (i=1; i<=5; i++) {
		letter=guess_as_array[i]
		if (PICK_LETTER_COUNT[letter] > 0) {
			if (pick_as_array[i] == guess_as_array[i]) {
				mark_correct(letter)
				unmark_misplaced(letter)
				current_guess_line_array[i]=correct_tag(letter)
			}
			else if ( (LABELED_MISPLACED[letter] + CORRECT_TO_LABEL[letter] + 1 )\
							<= ( PICK_LETTER_COUNT[letter] ) ) {
				mark_misplaced(letter)
				current_guess_line_array[i]=misplaced_tag(letter)
				LABELED_MISPLACED[letter]++
				enable_usage()
			}
			else {
				current_guess_line_array[i]=wrong_tag(letter)
			}
		}
		else {
			mark_wrong(letter)
			current_guess_line_array[i]=wrong_tag(letter)
		}
	}
	guess_string=guess_line_array_to_string(current_guess_line_array)
	add_guess_line_to_board(guess_string, NUM_GUESSES)
	if (CORRECT_THIS_LINE == 5) {
		enable_set_solved()
	}
	return 1
}

function print_guesses() {
	print_centered(ALL_GUESSES_FORMATTED)
}

function print_wordlist_stats() {
	printf "Playing with %s words acceptable to guess.\n",VALID_COUNT
	printf "Playing with %s words.\n\n",WCOUNT
}

function print_board() {
	if ( !(DEBUG) ) { clear() }
	print_title()
	if ( OPTIONS ) { disable_guide() }
	if ( GUIDE ) { print_guide() }
	print_guesses()
	printf "\n"
	print_letters()
	printf "\n"
	if ( OPTIONS ) {
		print_options()
		enable_guide()
	}
	if ( USAGE ) { print_usage() }
}

function prompt_user() {
	response=""
	printf "Enter text, ? for options, or 0 to quit: "
	getline
	return $0
}

function process_response(this) {
	if (this == 0) {
		disable_playing()
		exit 0
	} else if (this ~ /^[1-9]$/) {
		set_options(this)
	} else if (this == "?") {
		enable_options()
		disable_guide()
	} else if (this ~ /[a-z][a-z][a-z][a-z][a-z]/) {
		evaluate_guess(this)
	}
}

function process_final(this) {
	if (this == 0) {
		disable_playing()
		exit 0
	} else if (this ~ /^[1-9]$/) {
		set_options(this)
	} else if (this == "?") {
		enable_options()
		disable_guide()
	}
}

## INIT
## 
BEGIN{
	WORD_LIST_FILE="wordle-PLAY.txt"
	VALID_WORDLIST="wordle-VALID.txt"

	TPUT="/usr/bin/tput"
	CLEAR="clear"

	TITLE[1]="Wordle (AWK CLI)"
	USAGE_TEXT[1]="NOTE: misplaced # reflects occurrences; extras are marked wrong"
	## AWK :: 0 == false, 1 == true
	DEBUG=0
	DEBUG2=0
	STATS=0
	PLAYING=1
	SOLVED=0
	DEFAULT_SEED=23
	GAMES_PLAYED=0
	GAMES_SOLVED=0
	## Display letter key Centered (1=True) or Center-Justified (0=False) (DEFAULT)
	CENTER=0
	## Display guide to correct, misplaced, wrong, unchosen letters
	GUIDE=1
	## Display usage hint (currently regarding # of misplaced letters)
	USAGE=1
	## Display configuration options
	OPTIONS=0
	## Either print key QWERTY (1=True)(DEFAULT) or ALPHABETIC (0=False)
	USE_KEYBOARD=1

	KEYBOARD[1]="qwertyuiop"
	KEYBOARD[2]="asdfghjkl"
	KEYBOARD[3]="zxcvbnm"
	ALPHABET[1]="abcdefghi"
	ALPHABET[2]="jklmnopqr"
	ALPHABET[3]="stuvwxyz"

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


	import_validwords(VALID_WORDLIST)
	import_wordlist(WORD_LIST_FILE)
	init_stats()

	exit
}

## MAIN
## 
{
	lines[NR]=$0;
	if (length($0)>max){
		max=length($0)
	}
}

## POST
## 
END{
	init_seed()
	if (max > 0) {
		print_left_justified(lines)
	}
	while (PLAYING) {
		init_letters_in_current_guess()
		disable_usage()
		CURRENT_WORD=pick_word(WORDS)
		if (DEBUG) { printf "DEBUG: Picked word: \"%s\"\n",CURRENT_WORD }
		register_pick(CURRENT_WORD)
		while ( PLAYING && (NUM_GUESSES < 6) && !(SOLVED) ) {
			print_board()
			process_response(tolower(prompt_user()))
		}
		GAMES_PLAYED++
		if (SOLVED) {
			register_solution()
			disable_guide()
			print_board()
			print_stats()
			printf "Congratulations for solving \"%s\". Play again?\n",CURRENT_WORD
		} else if (NUM_GUESSES == 6) {
			disable_guide()
			print_board()
			printf "Puzzle not solved in 6 guesses. Reveal word [N|y]? "
			getline
			if ($0 ~ /^[Yy]/) {
				printf "The word was \"%s\". Play again?\n",CURRENT_WORD
			}
		}
		enable_guide()
		process_final(tolower(prompt_user()))
	}
}
