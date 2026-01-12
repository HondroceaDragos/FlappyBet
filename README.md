# FlappyBet

IMPORTANT: The game is too large to be archived even after removing all assets. Use the GitHub repository below to check the code!

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

- Built a section-based level system (spikes, tunnel, beams) with seamless transitions and distinct gameplay rules.
- Implemented progressive difficulty scaling by tuning spawn rates, obstacle density, and corridor/gap sizes over time.
- Designed a coin-based scoring and currency system used for progression and the slots mechanic.
- Refined spike sections for fair, readable obstacle patterns with controlled height and spacing.
- Implemented a walkable tunnel generator with smooth terrain, safe corridors, and integrated hazards.
- Tuned beam/pillar sections with smooth vertical variation and consistent spacing for fair navigation.
- Added game-feel and QoL improvements (sprite behavior, transitions, spawn safety, and polish).

### Hondrocea Dragoș

- Created the engine frame: physics engine, entities and sound manager
- Automated state creation and transition through a universal observer (GameMaster)
- Added debugging functionality for quality of life testing
- Designed interaction between entities (player and enemies)
- Randomized enemy spawn rate and attributes
- Drew custom player model and enemy sprites
- Added music and sound effects

### Tudose Radu

- Integrated the gacha/slots mechanic into core gameplay, including high-score handling.
- Implemented core UI states (main menu, pause, game over, help).
- Added user-friendly controls and interactions (custom buttons, key bindings).
- Handled general debugging and stability fixes across the project.


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
S: We integrated multiple levels into gameplay (spike dodging, cave diving). Also changed the gacha currency from actual score to a coin-based approach.# FlappyBet

IMPORTANT: The game is too large to be archived even after removing all assets. Use the GitHub repository below to check the code!

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

- Built a section-based level system (spikes, tunnel, beams) with seamless transitions and distinct gameplay rules.
- Implemented progressive difficulty scaling by tuning spawn rates, obstacle density, and corridor/gap sizes over time.
- Designed a coin-based scoring and currency system used for progression and the slots mechanic.
- Refined spike sections for fair, readable obstacle patterns with controlled height and spacing.
- Implemented a walkable tunnel generator with smooth terrain, safe corridors, and integrated hazards.
- Tuned beam/pillar sections with smooth vertical variation and consistent spacing for fair navigation.
- Added game-feel and QoL improvements (sprite behavior, transitions, spawn safety, and polish).

### Hondrocea Dragoș

- Created the engine frame: physics engine, entities and sound manager
- Automated state creation and transition through a universal observer (GameMaster)
- Added debugging functionality for quality of life testing
- Designed interaction between entities (player and enemies)
- Randomized enemy spawn rate and attributes
- Drew custom player model and enemy sprites
- Added music and sound effects

### Tudose Radu

- Integrated the gacha/slots mechanic into core gameplay, including high-score handling.
- Implemented core UI states (main menu, pause, game over, help).
- Added user-friendly controls and interactions (custom buttons, key bindings).
- Handled general debugging and stability fixes across the project.


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