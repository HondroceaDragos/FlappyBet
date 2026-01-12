
# FlappyBet

FlappyBet is a casual arcade game which boasts an interesting twist: score-based betting. At it's core, this project was inspired by the classic mobile game "Flappy Bird", where the player has to traverse a series of obstacles in order to achieve their highest score possible.

In FlappyBet, an abandoned canary bird has to escape a collapsing mine before it's too late! In its quest, this bird has to face multiple challenges, including precise maneuvering through tight tunnels and low altitude flying.


## Features

- Minimal game engine design (physics engine, audio manager, finite-state machine)
- Score-betting system (gacha mechanic integration)
- Custom sprites for entities and the environment
- Debugger integration
- Rich copyright-free soundtrack and sound effects
- Custom interactable menus and buttons


## Implementation

This project was created using the 'pygame' module for Python. All functional parts of this game were created from scratch.

### Main components

- Full Object Oriented Programming integration
- Object interaction is validated by a manager
- State is an abstract class; each new node of the state machine implements its own functionality
- The manager invokes general methods from states (answers questions such as: what should be displayed? how do objects behave?)
- Entities behave according to a physics engine, which controls world constants (gravity, speed, collision)
- Sound is played through separate supervisor; they are stored in a single place
- Assets are stored as image files


## Github Repository Link
[![github](https://img.shields.io/badge/github-FFFFFF?style=for-the-badge&logo=github&logoColor=black)](https://github.com/HondroceaDragos/FlappyBet/tree/main)


## Deployment

To deploy this project:

1. Create a virtual environment for your local machine

2. Inside the virtual environment, run:

 ```bash
    (venv) pip install pygame
 ```

3. Go to the /src/ directory:

 ```bash
    (venv) cd ./src
 ```

4. To play the project, run (use 'py' for Windows):

 ```bash
    (venv) python3 ./main.py
 ```


## Authors

### Bejenescu Ștefan

- Integrated the gacha mechanic into core gameplay
- Adjusted entity spawn rate and type (difficulty scaling and diversity)
- Quality of life improvements (game feel and sprites)
- Created a coin-based dynamic scoring system, which is used as currency for slots

### Hondrocea Dragoș

- Created the engine frame: physics engine, entities and sound manager
- Automated state creation and transition through a universal observer (GameMaster)
- Added debugging functionality for quality of life testing
- Designed interaction between entities (player and enemies)
- Randomized enemy spawn rate and attributes
- Drew custom player model and enemy sprites
- Added music and sound effects

### Tudose Radu

- Created menu and helper states (main menu, pause menu, game over screen)
- Added user-friendly interaction features (custom buttons and key presses)
- General debugging


## Conflict Resolution

Development Checkpoint - DC
Solution - S

### DC: No prior knowledge of the pygame module
S: We started reading the official ['pygame documentaion'](https://www.pygame.org/news) and general game making videos [such as this one](https://www.youtube.com/watch?v=_eK26atXTds&t=850s)

### DC: Time management
S: We assigned specific feature design to each member of the team

### DC: Display Optimization
S: We started by implementing a virtual screen (similar to how mainstream game engines handle different operating system kernels and display sizes), but quickly realized the implications (i. e. higher frequency monitors would run the game faster). In the end, we opted for a fixed screen size, which sclaes with the user's monitor dimensions

### DC: Game Feel
S: We integrated multiple levels into gameplay (spike dodging, cave diving). Also changed the gacha currency from actual score to a coin-based approach.