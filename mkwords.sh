#!/bin/bash

cd wordle_data
aspell -d en dump master | aspell -l en expand > my.dict
awk '!/'\''/ && !/[A-Z]/ && length($0)==5' my.dict | sort > wordle-list.txt

