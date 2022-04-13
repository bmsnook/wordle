# Wordle on the Command Line
## Using awk

Download the repo

```git clone git@github.com:bmsnook/wordle.git
cd wordle```

and run the program in Docker

```docker build -f Dockerfile-awk -t wordle-awk .
docker run -it wordle-awk```

or just run it at the command line

`./wordle.awk`


### NOTE:

I've generated/downloaded wordlists two different ways. Feel free to use the included wordlists (in the `wordlists` directory) or generate/find your own.

First, I generated a wordlist from the aspell dictionary on Linux. I can't claim credit for the aspell commands, which I found here:

[https://superuser.com/questions/137957/how-to-convert-aspell-dictionary-to-simple-list-of-words]

I did write a script to massage the data to be usable for Wordle. Please see the script `mkwords.sh`

Second, I used the following page

[https://www.pcmag.com/how-to/want-to-up-your-wordle-game-the-winning-word-is-right-on-the-page]

for inspiration in finding the script page used to store the wordlists. I wrote an awk script to download and digest the wordlist in case it changes in the future. Please see the script `get_nyt_wordlists.awk`

Feel free to edit or use your own wordlists!

### FINALLY:

I realize the current notation for differentiating unguessed/wrong/misplaced/correct letters is somewhat abysmal. I've played around with using lowercase for unselected letters, but I didn't like it much better. Although I mostly wrote this as a scripting/programming exercise, and a framework to port over to Python for learning, I'm open to suggestions/feedback if anyone else actually finds and plays this.

