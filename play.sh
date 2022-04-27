#!/bin/bash

echo "Play the awk or python version in a docker container? [a|p]  "
read response

if [ "${response}" = "a" ]; then
	docker build -f Dockerfile-awk -t wordle-awk .
	docker run -it wordle-awk
elif [ "${response}" = "p" ]; then
	docker build -f Dockerfile-pycli -t wordle-pycli .
	docker run -it wordle-pycli
else
	echo "I didn't understand. Please try again."
fi
