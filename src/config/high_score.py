import json
import os


class HighScoreManager:
    @staticmethod
    def _path() -> str:
        # Path relative to this file -> ../data/highScore.json
        base = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(base, "../data/highScore.json"))

    @staticmethod
    def load() -> int:
        path = HighScoreManager._path()
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return int(data.get("highestScore", 0))
        except FileNotFoundError:
            HighScoreManager.save(0)
            return 0
        except Exception:
            # If file is corrupted, don't crash the game
            return 0

    @staticmethod
    def save(score: int) -> None:
        path = HighScoreManager._path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"highestScore": int(score)}, f, indent=4)
