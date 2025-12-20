from enum import Enum


def red(text):
    return f"\033[31m{text}\033[0m"


def green(text):
    return f"\033[32m{text}\033[0m"


class Debugger:
    HITBOXES = False
    STATE = None

    _isRunning = False

    _debugOptions = {"1": "Show hitboxes", "2": "Custom game state"}

    @classmethod
    def _hitbox(cls):
        if Debugger.HITBOXES:
            print(f"\nHitboxes are now {red('dissabled')}\n")
            print(
                f"To {green('enable')} them, {green('reselect')} this debugging option\n"
            )
            cls.HITBOXES = False
        else:
            print(f"\nHitboxes are now {green('enabeled')}\n")
            print(
                f"To {red('dissable')} them, {red('reselect')} this debugging option\n"
            )
            cls.HITBOXES = True

    @classmethod
    def _states(cls):
        possibleStates = {"1": "mainMenu", "2": "gameInProgress"}

        print("\nSelect your custom game state:")
        print(
            "\n".join(f"[{key}]: {value}" for key, value in possibleStates.items())
            + "\n"
        )

        state = input()
        if state in possibleStates:
            cls.STATE = possibleStates[state]
            print(f"\nProgram will start on: {green(cls.STATE)}\n")
        else:
            print(f"\nInvalid argument: {red(state)}\n")

    @classmethod
    def _toggle(cls):
        cls._isRunning = not cls._isRunning

    @classmethod
    def _prompt(cls):
        print("Please select your desired debugging options:")
        print(
            "\n".join(
                f"[{key}]: {value}" for key, value in Debugger._debugOptions.items()
            )
        )

        print(f"\nPress {red('q')} to quit\n")

    @classmethod
    def enable(cls):
        print("\tWelcome to the debugger for\n")
        print("\t=========FlappyBet=========\t\n")
        Debugger._prompt()

        cls._toggle()

        while cls._isRunning:
            action = input()
            match (action):
                case "1":
                    cls._hitbox()
                    Debugger._prompt()
                case "2":
                    cls._states()
                    Debugger._prompt()
                case "q":
                    cls._toggle()
                case _:
                    print(f"\nInvalid option: {red(action)}\n")
                    Debugger._prompt()
