# Wordle on the Command Line
## Using awk

Download the repo

```
git clone git@github.com:bmsnook/wordle.git
cd wordle
```

and then either run the program in Docker

```
docker build -f Dockerfile-awk -t wordle-awk .
docker run -it wordle-awk
```
or 
```
docker build -f Dockerfile-pycli -t wordle-pycli .
docker run -it wordle-pycli
```

or just run it at the command line

```
./wordle.awk
```
or 
```
./wordle.py
```

*(The reason I use `Dockerfile-awk` is because I envision future versions in other languages and I don't know that I'd necessarily want to start them all at the same time, so I anticipate future use of `Dockerfile-python` and `Dockerfile-java`, for instance)*

### NOTE on building behind corporate firewalls/filters that use MITM to examine SSL/TLS traffic:

If you receive an error while building to the effect of "site couldn't be verified", you likely have a MITM device decrypting outbound traffic and it is returning a certificate path that the Docker container doesn't recognize. The workaround is to copy the local cacerts file your browser uses to recognize internal/corporate sites to `LOCAL-CACERTS.pem` and then use the file `Dockerfile-awk-MITM` instead of `Dockerfile-awk` to build (actually, the MITM file should work for either use case, since it uses a wildcard to copy the file and will silently fail if the file is not found locally, but I didn't want to clutter the file for basic use cases).

For example:
```
docker build -f Dockerfile-awk-MITM -t wordle-awk .
docker run -it wordle-awk
```

### NOTE on wordlists:

I've generated/downloaded wordlists two different ways. Feel free to use the included wordlists (in the `wordlists` directory) or generate/find your own.

First, I generated a wordlist from the aspell dictionary on Linux. I can't claim credit for the aspell commands, which I found here:

[https://superuser.com/questions/137957/how-to-convert-aspell-dictionary-to-simple-list-of-words]

I did write a script to massage the data to be usable for Wordle. Please see the script [`mkwords.sh`](https://github.com/bmsnook/wordle/blob/master/mkwords.sh)

Second, I used the following page

[https://www.pcmag.com/how-to/want-to-up-your-wordle-game-the-winning-word-is-right-on-the-page]

for inspiration in finding the script page used to store the wordlists. I wrote an awk script to download and digest the wordlist in case it changes in the future. Please see the script [`get_nyt_wordlists.awk`](https://github.com/bmsnook/wordle/blob/master/get_nyt_wordlists.awk)

Feel free to edit or use your own wordlists!

### FINALLY:

I realize the current notation for differentiating unguessed/wrong/misplaced/correct letters is somewhat abysmal. I've played around with using lowercase for unselected letters, but I didn't like it much better. Although I mostly wrote this as a scripting/programming exercise, and a framework to port over to Python for learning, I'm open to suggestions/feedback if anyone else actually finds and plays this.


## The Real Deal™

Of course, for the real experience of Wordle, you should check out the NYT version online

https://www.nytimes.com/games/wordle/index.html

and/or download one of the multiple versions available on device app stores.
