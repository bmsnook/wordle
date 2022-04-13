#!/usr/bin/gawk -f

function get_script_name() {
	cmd=sprintf("%s %s/%s",CURL,GAMEHOME,INDEX)
	while ( (cmd | getline) > 0) {
		if ( $0 ~ /script src=/ ) {
			split($0, scriptline, "\"")
			script=scriptline[2]
			if (script !~ /\.js$/) {
				script=SCRIPT_HISTORICAL
			}
		}
	}
	return script
}

## Oa = acceptable
## Ma = playable
function get_wordlists(scriptfile) {
	cmd=sprintf("%s %s/%s",CURL,GAMEHOME,scriptfile)
	while ( (cmd | getline) > 0 ) {
#	while ( (getline < SCRIPT_HISTORICAL) > 0 ) {
		if ( $0 ~ /(M|O)a=/ ) {
			START_MA_OFFSET=index($0,"Ma=")+4
			LENGTH_MA_STRING=index(substr($0,START_MA_OFFSET),"]")-1
			STRING_MA_PLAY=substr($0,START_MA_OFFSET,LENGTH_MA_STRING)
			START_OA_OFFSET=index($0,"Oa=")+4
			LENGTH_OA_STRING=index(substr($0,START_OA_OFFSET),"]")-1
			STRING_OA_VALID=substr($0,START_OA_OFFSET,LENGTH_OA_STRING)
		}
	}
	close(cmd)
#	close(SCRIPT_HISTORICAL)
}

function split_and_sort_string_to_file(the_string, output_file) {
	gsub("\"","",the_string)
	split(the_string,the_array,",")
	for (each_index in the_array) {
		print the_array[each_index] |& SORT
	}
	close(SORT, "to")
	while(SORT |& getline sorted_line) {
		print sorted_line > output_file
	}
	close(SORT)
	close(output_file)
}

BEGIN {
	CURL="/usr/bin/curl"
	SORT="/usr/bin/sort"

	GAMEHOME="https://www.nytimes.com/games/wordle"
	INDEX="index.html"
	SCRIPT_HISTORICAL="main.3d28ac0c.js"

	LIST_VALID="wordle-list_nyt_VALID.txt"
	LIST_PLAY="wordle-list_nyt_PLAY.txt"

	gamescript=get_script_name()
	get_wordlists(gamescript)

	split_and_sort_string_to_file(STRING_MA_PLAY,LIST_PLAY)
	split_and_sort_string_to_file(STRING_OA_VALID,LIST_VALID)
}

