package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"slices"
	"strings"
	"time"

	"golang.org/x/term"
)

var CLEAR string = "clear"

var WORD_LIST_FILE string = "wordle-PLAY.txt"
var VALID_WORDLIST string = "wordle-VALID.txt"
var DEFAULT_WIDTH int = 80

var VALID_WORDS []string = []string{}
var WORDS []string = []string{}
var USAGE_TEXT []string = []string{"NOTE: misplaced # reflects occurrences; extras are marked wrong"}
var SOLVED_MOVES map[int]int = map[int]int{}
var COUNT_LINE_GUESS map[string]int = map[string]int{}
var PICK_LETTER_COUNT map[string]int = map[string]int{}
var CORRECT_ARRAY map[string]bool = map[string]bool{}
var MISPLACED_ARRAY map[string]bool = map[string]bool{}
var WRONG_ARRAY map[string]bool = map[string]bool{}

// var LETTER_STATUS map[string]int = map[string]int{}
// var LETTER_STATUS map[int]string = map[int]string{}
var LETTER_STATUS []string = []string{}
var CURRENT_GUESS_ARRAY map[int]string = map[int]string{}
var CORRECT_TO_LABEL map[string]int = map[string]int{}
var OCCUR_TO_LABEL map[string]int = map[string]int{}
var LABELED_MISPLACED map[string]int = map[string]int{}
var ALL_GUESSES_FORMATTED []string = []string{}
var SOLVED_RATIO map[int]float32 = map[int]float32{}

var VALID_COUNT int = 0
var WCOUNT int = 0
var VALID_BONUS_COUNT int = 0

var KEYBOARD []string = []string{"qwertyuiop", "asdfghjkl", "zxcvbnm"}
var ALPHABET []string = []string{"abcdefghi", "jklmnopqr", "stuvwxyz"}

var DEBUG bool = false
var DEBUG1 bool = false
var DEBUG2 bool = false
var STATS bool = false
var PLAYING bool = true
var SOLVED bool = false
var CENTER bool = false
var GUIDE bool = true
var USAGE bool = true
var OPTIONS bool = false
var USE_KEYBOARD bool = true

var TITLE []string = []string{"Wordle (Go CLI)"}
var DEFAULT_SEED int = 23
var GAMES_PLAYED int = 0
var GAMES_SOLVED int = 0
var NUM_GUESSES int = 0
var CORRECT_THIS_LINE int = 0

var GUESS_LD string = "["
var GUESS_RD string = "]"
var GSEP string = "  "
var KEY_LD string = "["
var KEY_RD string = "]"
var KSEP string = "  "
var CORRECT_TAG_DELIM string = "_"
var MISPLACED_TAG_DELIM string = "-"
var WRONG_TAG_DELIM string = "*"
var BASIC_TAG_DELIM string = " "
var BLANK_TAG_DELIM string = " "

var CURRENT_WORD string = ""

func import_validwords(WFILE string) {
	file, err := os.Open(WFILE)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error opening file %s: %v\n", WFILE, err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		word := strings.TrimSpace(scanner.Text())
		if word != "" {
			VALID_COUNT += 1
			VALID_WORDS = append(VALID_WORDS, word)
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Error reading file %s: %v\n", WFILE, err)
	}
}

func import_wordlist(WFILE string) {
	file, err := os.Open(WFILE)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error opening file %s: %v\n", WFILE, err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		word := strings.TrimSpace(scanner.Text())
		if word != "" {
			WCOUNT += 1
			WORDS = append(WORDS, word)

			// Check if word is not already in VALID_WORDS
			found := false
			for _, validWord := range VALID_WORDS {
				if validWord == word {
					found = true
					break
				}
			}

			if !found {
				VALID_COUNT += 1
				VALID_BONUS_COUNT += 1
				VALID_WORDS = append(VALID_WORDS, word)
			}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Error reading file %s: %v\n", WFILE, err)
	}
}

func get_term_width() int {
	width := DEFAULT_WIDTH
	fd := int(os.Stdout.Fd())
	// Check if the terminal is a TTY
	if !term.IsTerminal(fd) {
		// fmt.Println("Not a terminal")
		// return
		width = DEFAULT_WIDTH
	}
	// Get the terminal size
	width, height, err := term.GetSize(fd)
	_ = height
	if err != nil {
		// fmt.Println("Error getting terminal size:", err)
		// return
		width = DEFAULT_WIDTH
	}
	return width
}

func print_left_justified(array_of_lines []string) {

	max_line_length := 0
	NL := len(array_of_lines)
	for i := 0; i < NL; i++ {
		if len(array_of_lines[i]) > max_line_length {
			max_line_length = len(array_of_lines[i])
		}
	}
	WD := get_term_width()
	SZ := int(WD / max_line_length)
	for i := 0; i < NL; i++ {
		for j := 0; j < len(array_of_lines[i]); j++ {
			fmt.Printf("%-*c", SZ, array_of_lines[i][j])
		}
		fmt.Println()
	}
}

func print_center_justified(array_of_lines []string) {

	max_line_length := 0
	NL := len(array_of_lines)
	for i := 0; i < NL; i++ {
		if len(array_of_lines[i]) > max_line_length {
			max_line_length = len(array_of_lines[i])
		}
	}
	WD := get_term_width()
	MARGIN := int((WD - max_line_length) / 2)
	for i := 0; i < NL; i++ {
		for j := 0; j < MARGIN; j++ {
			fmt.Print(" ")
		}
		fmt.Println(array_of_lines[i])
	}
}

func print_centered(array_of_lines []string) {
	WD := get_term_width()
	NL := len(array_of_lines)
	for i := 0; i < NL; i++ {
		LILEN := len(array_of_lines[i])
		MARGIN := int((WD - LILEN) / 2)
		for j := 0; j < MARGIN; j++ {
			fmt.Print(" ")
		}
		fmt.Println(array_of_lines[i])
	}
}

func formatted_letter(letter string) string {
	if CORRECT_ARRAY[letter] {
		return CORRECT_TAG_DELIM + letter + CORRECT_TAG_DELIM
	} else if MISPLACED_ARRAY[letter] {
		return MISPLACED_TAG_DELIM + letter + MISPLACED_TAG_DELIM
	} else if WRONG_ARRAY[letter] {
		return WRONG_TAG_DELIM + letter + WRONG_TAG_DELIM
	} else {
		return BASIC_TAG_DELIM + letter + BASIC_TAG_DELIM
	}
}

// func map_letters(letter_array []string) []string {
func map_letters(letter_array []string) {
	LETTER_STATUS = make([]string, len(letter_array))
	for i := 0; i < len(letter_array); i++ {
		line := ""
		num_per_line := strings.Split(letter_array[i], "")
		for j := 0; j < len(num_per_line)-1; j++ {
			val := formatted_letter(num_per_line[j])
			line = line + KEY_LD + val + KEY_RD + KSEP
		}
		val := formatted_letter(num_per_line[len(num_per_line)-1])
		line = line + KEY_LD + val + KEY_RD
		LETTER_STATUS[i] = line
	}
	// return LETTER_STATUS
}

func print_letters() {
	if USE_KEYBOARD {
		map_letters(KEYBOARD)
	} else {
		map_letters(ALPHABET)
	}
	if CENTER {
		print_centered(LETTER_STATUS)
	} else {
		print_center_justified(LETTER_STATUS)
	}
}

func print_title() {
	print_centered(TITLE)
}

func print_guide() {
	fmt.Println("GUIDE:")
	fmt.Println("  [" + correct_tag("a") + "]  ==  CORRECT letter")
	fmt.Println("  [" + misplaced_tag("a") + "]  ==  Misplaced letter (elsewhere in puzzle)")
	fmt.Println("  [" + wrong_tag("a") + "]  ==  Wrong letter (not in puzzle)")
	fmt.Println("  [" + basic_tag("a") + "]  ==  Untried letter")
	fmt.Println()
}

func print_usage() {
	print_center_justified(USAGE_TEXT)
}

func print_options() {
	fmt.Println("OPTIONS:")
	fmt.Println("  0 == Quit")
	fmt.Println("  1 == Use QWERTY mapping for used letters status (DEFAULT)")
	fmt.Println("  2 == Use ALPHABETIC mapping for used letters status")
	fmt.Println("  3 == Toggle pre-board wordlist info and guide")
	fmt.Println("  8 == Toggle centered and justified display")
	fmt.Println("  9 == Toggle DEBUG mode (caution: reveals word pick)")
	fmt.Println()
	disable_options()
	enable_guide()
}

func clear() {
	// os.Command(CLEAR).Run()
	clear_cmd := exec.Command(CLEAR)
	clear_cmd.Stdout = os.Stdout
	clear_cmd.Run()
}

func pick_word(ENUM_LIST_ARRAY []string) string {
	wordcount := len(ENUM_LIST_ARRAY)
	rand.Seed(time.Now().UnixNano())
	picked_number := rand.Intn(wordcount)
	picked_word := ENUM_LIST_ARRAY[picked_number]
	init_pick_tracking()
	return picked_word
}

func init_pick_tracking() {
	NUM_GUESSES = 0
	SOLVED = false
	ALL_GUESSES_FORMATTED = make([]string, 6)
	for i := 0; i < 6; i++ {
		guess_string := ""
		for j := 0; j < 5; j++ {
			guess_string += GUESS_LD + blank_tag() + GUESS_RD
			if j < 4 {
				guess_string += GSEP
			}
		}
		ALL_GUESSES_FORMATTED[i] = guess_string
	}
	// for letter := range "abcdefghijklmnopqrstuvwxyz" {
	for c := 'a'; c <= 'z'; c++ {
		letter := string(c)
		CORRECT_ARRAY[letter] = false
		MISPLACED_ARRAY[letter] = false
		WRONG_ARRAY[letter] = false
		PICK_LETTER_COUNT[letter] = 0
	}
}

func init_stats() {
	GAMES_PLAYED = 0
	GAMES_SOLVED = 0
	for i := 1; i <= 6; i++ {
		SOLVED_MOVES[i] = 0
		SOLVED_RATIO[i] = 0.0
	}
}

func register_solution() {
	if SOLVED {
		GAMES_SOLVED += 1
		SOLVED_MOVES[NUM_GUESSES] += 1
	}
}

func print_stats() {
	ratio := float32(0.0)
	fmt.Printf("Games Played: %6d      Games Solved: %6d      (%.2f %%)\n", GAMES_PLAYED, GAMES_SOLVED, float32(GAMES_SOLVED)/float32(GAMES_PLAYED)*100)
	for i := 1; i <= 6; i++ {
		if GAMES_SOLVED == 0 {
			ratio = float32(0.0)
		} else {
			ratio = float32(SOLVED_MOVES[i]) / float32(GAMES_SOLVED) * 100
		}
		SOLVED_RATIO[i] = ratio
		fmt.Printf("%d:%d (%.1f%%)  ", i, SOLVED_MOVES[i], ratio)
	}
	fmt.Println()
	fmt.Println()
}

func init_this_guess_tracking() {
	CORRECT_THIS_LINE = 0
	for i := 0; i < 5; i++ {
		CURRENT_GUESS_ARRAY[i] = blank_tag()
	}
	// for letter := range "abcdefghijklmnopqrstuvwxyz" {
	for c := 'a'; c <= 'z'; c++ {
		letter := string(c)
		CORRECT_TO_LABEL[letter] = 0
		OCCUR_TO_LABEL[letter] = 0
		LABELED_MISPLACED[letter] = 0
	}
}

func init_letters_in_current_guess() {
	// for letter := range "abcdefghijklmnopqrstuvwxyz" {
	for c := 'a'; c <= 'z'; c++ {
		letter := string(c)
		COUNT_LINE_GUESS[letter] = 0
	}
}

func set_options(this int) {
	if this == 1 {
		enable_keyboard_letter_ordering()
	} else if this == 2 {
		disable_keyboard_letter_ordering()
	} else if this == 3 {
		if GUIDE {
			disable_guide()
		} else {
			enable_guide()
		}
	} else if this == 8 {
		if CENTER {
			disable_centered_layout()
		} else {
			enable_centered_layout()
		}
	} else if this == 9 {
		if DEBUG {
			disable_debug()
		} else {
			enable_debug()
		}
	}
}

func disable_usage() {
	USAGE = false
}

func enable_usage() {
	USAGE = true
}

func disable_guide() {
	GUIDE = false
}

func enable_guide() {
	GUIDE = true
}

func disable_options() {
	OPTIONS = false
}

func enable_options() {
	OPTIONS = true
}

func disable_centered_layout() {
	CENTER = false
}

func enable_centered_layout() {
	CENTER = true
}

func disable_keyboard_letter_ordering() {
	USE_KEYBOARD = false
}

func enable_keyboard_letter_ordering() {
	USE_KEYBOARD = true
}

func disable_debug() {
	DEBUG = false
}

func enable_debug() {
	DEBUG = true
}

func disable_set_solved() {
	SOLVED = false
}

func enable_set_solved() {
	SOLVED = true
}

func disable_playing() {
	PLAYING = false
}

func guess_line_array_to_string(guess_line_array []string) string {
	guess_string := ""
	for i := 0; i < len(guess_line_array); i++ {
		guess_string += GUESS_LD + guess_line_array[i] + GUESS_RD
		if i < len(guess_line_array)-1 {
			guess_string += GSEP
		}
	}
	return guess_string
}

func add_guess_line_to_board(guess_string string, guess_number int) {
	ALL_GUESSES_FORMATTED[guess_number] = guess_string
}

func correct_tag(letter string) string {
	return CORRECT_TAG_DELIM + strings.ToUpper(letter) + CORRECT_TAG_DELIM
}

func misplaced_tag(letter string) string {
	return MISPLACED_TAG_DELIM + strings.ToUpper(letter) + MISPLACED_TAG_DELIM
}

func wrong_tag(letter string) string {
	return WRONG_TAG_DELIM + strings.ToUpper(letter) + WRONG_TAG_DELIM
}

func basic_tag(letter string) string {
	return BASIC_TAG_DELIM + strings.ToUpper(letter) + BASIC_TAG_DELIM
}

func blank_tag() string {
	return BLANK_TAG_DELIM + " " + BLANK_TAG_DELIM
}

func mark_correct(letter string) {
	CORRECT_ARRAY[letter] = true
}

func mark_misplaced(letter string) {
	MISPLACED_ARRAY[letter] = true
}

func unmark_misplaced(letter string) {
	MISPLACED_ARRAY[letter] = false
}

func mark_wrong(letter string) {
	WRONG_ARRAY[letter] = true
}

func register_pick(pick string) {
	NUM_GUESSES = 0
	// split(pick, pick_as_array, "")
	pick_as_array := strings.Split(pick, "")
	for _, letter := range pick_as_array {
		PICK_LETTER_COUNT[letter] += 1
	}
}

func evaluate_guess(guess string) int {
	current_guess_line_array := make([]string, 5)
	for i := 0; i < 5; i++ {
		current_guess_line_array[i] = blank_tag()
	}
	if !slices.Contains(VALID_WORDS, guess) {
		return 0
	}
	init_this_guess_tracking()
	// Step through 1/2 times to count matches
	for i := 0; i < 5; i++ {
		// letter := guess[i]
		letter := string(guess[i])
		COUNT_LINE_GUESS[letter] += 1
		if string(CURRENT_WORD[i]) == letter {
			CORRECT_TO_LABEL[letter] += 1
			CORRECT_THIS_LINE += 1
		}
		OCCUR_TO_LABEL[letter] += 1
	}
	// Step through 2/2 times to format letters
	for i := 0; i < 5; i++ {
		// letter := guess[i]
		letter := string(guess[i])
		if PICK_LETTER_COUNT[letter] > 0 {
			if string(CURRENT_WORD[i]) == letter {
				mark_correct(letter)
				unmark_misplaced(letter)
				current_guess_line_array[i] = correct_tag(letter)
			} else if (LABELED_MISPLACED[letter] + CORRECT_TO_LABEL[letter] + 1) <= PICK_LETTER_COUNT[letter] {
				mark_misplaced(letter)
				current_guess_line_array[i] = misplaced_tag(letter)
				LABELED_MISPLACED[letter] += 1
				enable_usage()
			} else {
				current_guess_line_array[i] = wrong_tag(letter)
			}
		} else {
			mark_wrong(letter)
			current_guess_line_array[i] = wrong_tag(letter)
		}
	}
	current_guess_string := guess_line_array_to_string(current_guess_line_array)
	add_guess_line_to_board(current_guess_string, NUM_GUESSES)
	if CORRECT_THIS_LINE == 5 {
		enable_set_solved()
	}
	NUM_GUESSES += 1
	return 1
}

func print_guesses() {
	if DEBUG {
		print_left_justified(ALL_GUESSES_FORMATTED)
	} else {
		print_centered(ALL_GUESSES_FORMATTED)
	}
}

func print_wordlist_stats() {
	fmt.Println("Playing with", VALID_COUNT, "words acceptable to guess.")
	fmt.Println("Playing with", WCOUNT, "words.")
}

func print_board() {
	if !(DEBUG) {
		clear()
	}
	print_title()
	if OPTIONS {
		disable_guide()
	}
	if GUIDE {
		print_guide()
	}
	print_guesses()
	fmt.Println()
	print_letters()
	fmt.Println()
	if OPTIONS {
		print_options()
		enable_guide()
	}
	if USAGE {
		print_usage()
	}
}

func prompt_user() string {
	fmt.Print("Enter text, ? for options, or 0 to quit: ")
	var response string
	fmt.Scanln(&response)
	return response
}

func process_response(this string) {
	if DEBUG {
		fmt.Println("DEBUG: (process_response): response == '", this, "'")
	}
	looksLikeOption := regexp.MustCompile("^[1-9]$")
	looksLikeWord := regexp.MustCompile("^[a-z][a-z][a-z][a-z][a-z]$")
	if this == "0" {
		disable_playing()
		if DEBUG1 {
			fmt.Println("DEBUG: (process_response): input = '", this, "'")
			fmt.Println("DEBUG: (process_response): PLAYING = '", PLAYING, "'")
		}
		return
	} else if looksLikeOption.MatchString(this) {
		if n, err := strconv.Atoi(this); err == nil {
			set_options(n)
		}
		return
	} else if looksLikeWord.MatchString(this) {
		evaluate_guess(this)
		return
	} else if this == "?" {
		enable_options()
		disable_guide()
		return
	}
	return
}

func process_final(this string) {
	if DEBUG {
		fmt.Println("DEBUG: (process_final): response == '", this, "'")
	}
	looksLikeOption := regexp.MustCompile("^[1-9]$")
	if this == "0" {
		disable_playing()
		return
	} else if looksLikeOption.MatchString(this) {
		if n, err := strconv.Atoi(this); err == nil {
			set_options(n)
		}
		return
	} else if this == "?" {
		enable_options()
		disable_guide()
		return
	}
	// Any non-zero input continues to a new game
	return
}

func main() {
	// init_seed()
	import_validwords(VALID_WORDLIST)
	import_wordlist(WORD_LIST_FILE)
	init_stats()
	for PLAYING {
		init_letters_in_current_guess()
		disable_usage()
		CURRENT_WORD = pick_word(WORDS)
		if DEBUG {
			fmt.Println("Picked word:", CURRENT_WORD)
		}
		register_pick(CURRENT_WORD)
		for PLAYING && (NUM_GUESSES < 6) && !SOLVED {
			print_board()
			process_response(strings.ToLower(prompt_user()))
		}
		GAMES_PLAYED += 1
		if SOLVED {
			register_solution()
			disable_guide()
			print_board()
			print_stats()
			fmt.Println("Congratulations for solving: '", CURRENT_WORD, "'. Play again?")
		} else if NUM_GUESSES == 6 {
			disable_guide()
			print_board()
			fmt.Println("Puzzle not solved in 6 guesses. Reveal word [N|y]? ")
			var response string
			fmt.Scanln(&response)
			if strings.ToLower(response) == "y" {
				fmt.Println("The word was: '", CURRENT_WORD, "'. Play again?")
			}
		}
		enable_guide()
		if PLAYING {
			process_final(strings.ToLower(prompt_user()))
		}
	}
}
