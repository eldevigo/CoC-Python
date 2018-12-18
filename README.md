# Corruption of Champions: now in python!

This is a ground-up rewrite of the original (pre-mod) Corruption of Champions game. If you are unfamiliar with the game, caveat emptor: this is strictly adult entertainment. The game content, and thus the source, contains lots of very explicit and vulgar content. Not suitable for children, workplaces, or people with good taste.


## Project goals

At a high level, here's some things I want this project to achieve:
- Provide a widely compatible cross-platform client with which to explore the original game experience.
- Support the future development of bolt-on clients that can present the same game experience with different interfaces, including possibly a multiple-concurrent-user server agent (not interactive multiplayer, just hosted CoC-as-a-Service).
- Be maintainable for the foreseeable future, so that we can continue to play CoC after Flash is dead and buried.
- Encourage developing and expanding the existing game world (incl. reimplementing the community mod of CoC), and potentially create entire new worlds of fresh content, with minimal or no modification of engine code.


## Playing the game

I develop and test on Linux, so this is the most likely platform to work well. However I do want this project to run on Windows as well, so I encourage you to try, and report any errors you get as a project issue. Windows-related feature and patch contributions are especially welcome! If you try running this on Windows and get stuck, try installing [Cygwin](https://www.cygwin.com/) and running it there.

Installing and running on Linux should be as simple as following these steps. Commands, where given, need to be entered into a terminal.
- If you don't have Python 3, please install Python 3 and Pip 3. I recommend the [Python Foundation Installation Guide](https://packaging.python.org/guides/installing-using-linux-tools/).
- Download the project.
  - If you have git installed, you can run `git clone https://github.com/eldevigo/CoC-Python.git`
  - If you don't have git, or you prefer not to use it, run the following:
  - `wget https://github.com/eldevigo/CoC-Python/archive/master.zip && unzip master.zip && rm master.zip`
    - On some distros you may need to install `wget` and/or `unzip`. If you're running one of these, I assume you know how to do this.
- Enter the project directory: `cd CoC-Python-master`
- Install project dependencies: `pip3 install -r requirements.txt`
- Call the terminal interface: `./coc-tui`
  - The TUI client will create a directory and a reference file to save your games in when you first run it. By default, it uses the path `~/.coc/`, but you can overide it with the `-s` option. Call `./coc-tui --help` for more info.


## Contributing

I'm open to any and all contributions of course. Please fork and issue PRs. For fixes and feature implementations please link to an open issue (open one if there's none). Please don't be discouraged if I request changes on a PR, it's not that I don't want your help, I just want to try to keep the codebase manageable.

At this point in the process I'm not likely to be able to respond to user issues, but I encourage you to file issues with any bugs you find and I'll prioritize them as I can.


### Development choices and priorities

Here's some opinions I have about how this project is going to go down, at least in its initial phases. Subject to change at my whim, or if enough people argue with me.

- Use idiomatic, object-oriented Python with good coding practices, wherever possible.
- Store all text world assets and all context-sensitive choices (i.e. all dialogues, dialogue parameterization, and player decision options) as serialized YAML objects, within a directory structure called a "world schema". The world schema should describe the NPCs, monsters, locales, and other content in the world, as well as describing what sort of state a player can have.
- World schemas should be immutable at runtime. Whenever a game user makes a choice that affects the state of the world, any associated state is stored in the "player file". This allows new PCs to be created and run in parallel.
- The first world schema will be the "classic" version of CoC, as written by Fenoxo and other original contributors. This will serve as a proof of concept, and provide a base that can be forked to apply mods. Wherever possible, the behavior of the original CoC should be replicated as closely as possible, except where this would require exceptionally odious coding choices that will interfere with game code maintainability down the line. Minor content changes such as typo fixes may also be accepted, where it doesn't represent a meaningful change in game experience.
- Whenever possible, it is preferable to write the game engine code in as "generic" a manner as possible, to support reusing and expanding the engine to support other game worlds that may be developed in the future. It's expected that this will be difficult in some areas given the somewhat "artisanal" coding styles used in the original engine (apologies to all original developers, no offense intended), so exceptions will be made where the only other choice is to make the world schema infeasibly complex.
- Document all schemas as thoroughly as possible. One of the things that makes CoC fun is its complexity, which in turn means that any attempt to replicate it must support a staggering variety of conditionals, asset rendering, and behavior chains. Any schema capable of representing that is going to be hefty, and it needs to be documented if it's going to be usable.
- The proof-of-concept interface will be a `curses`-based text terminal interface. We all like the adorable little 8-bit sprite assets from the original game, but they aren't a huge part of play, and without them this game is basically a text adventure game. I'm using this as an excuse to not have to learn any graphical UI libraries. Windows users who want to test or develop may need to play in a Cygwin shell for the time being. Sorry guys, this is a big job and I'm a Linux user, I want to get this working before I start trying to make it portable.
