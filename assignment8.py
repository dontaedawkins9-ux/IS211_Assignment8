
import argparse
import random
import time


class Player:
    """Base class for all players."""

    def __init__(self, name):
        self.name = name
        self.score = 0

    def choose_action(self, turn_total):
        raise NotImplementedError


class HumanPlayer(Player):
    """Human player chooses roll or hold."""

    def choose_action(self, turn_total):
        while True:
            choice = input("Roll (r) or hold (h)? ").strip().lower()
            if choice in ("r", "h"):
                return choice
            print("Invalid choice. Enter r or h.")


class ComputerPlayer(Player):
    """Computer holds at min(25, 100 - score)."""

    def choose_action(self, turn_total):
        target = min(25, 100 - self.score)
        if turn_total >= target:
            print(f"{self.name} chooses hold.")
            return "h"
        print(f"{self.name} chooses roll.")
        return "r"


class PlayerFactory:
    """Factory pattern for creating players."""

    @staticmethod
    def create_player(player_type, name):
        if player_type == "human":
            return HumanPlayer(name)
        if player_type == "computer":
            return ComputerPlayer(name)
        raise ValueError("Unknown player type")


class Die:
    """Standard six-sided die."""

    def roll(self):
        return random.randint(1, 6)


class PigGame:
    """Manage a normal game of Pig."""

    def __init__(self, player1="human", player2="human"):
        self.players = [
            PlayerFactory.create_player(player1, "Player 1"),
            PlayerFactory.create_player(player2, "Player 2")
        ]
        self.die = Die()
        self.current_player = 0

    def play_turn(self, deadline=None):
        player = self.players[self.current_player]
        turn_total = 0

        while True:
            if deadline is not None and time.monotonic() >= deadline:
                return False

            print(f"\n{player.name} | Turn total: {turn_total} | "
                  f"Game score: {player.score}")

            choice = player.choose_action(turn_total)

            if deadline is not None and time.monotonic() >= deadline:
                return False

            if choice == "h":
                player.score += turn_total
                print(f"{player.name} holds. Score: {player.score}")
                break

            roll = self.die.roll()
            print(f"{player.name} rolled {roll}.")

            if roll == 1:
                print(f"{player.name} loses the turn's points!")
                break

            turn_total += roll

        return player.score >= 100

    def winner(self):
        return max(self.players, key=lambda player: player.score)

    def announce_winner(self, timed_out=False):
        if timed_out:
            print("\nTime is up!")

        if self.players[0].score == self.players[1].score:
            print(f"It's a tie! Both have "
                  f"{self.players[0].score} points.")
        else:
            winner = self.winner()
            print(f"\n{winner.name} wins with "
                  f"{winner.score} points!")

    def play(self):
        print("Welcome to Pig! First player to 100 wins.")

        while True:
            if self.play_turn():
                self.announce_winner()
                return

            self.current_player = (
                self.current_player + 1
            ) % len(self.players)


class TimedGameProxy:
    """Proxy pattern that adds a 60-second time limit."""

    def __init__(self, player1="human", player2="human"):
        self.game = PigGame(player1, player2)
        self.duration = 60

    @property
    def players(self):
        return self.game.players

    @property
    def current_player(self):
        return self.game.current_player

    def play_turn(self, deadline=None):
        return self.game.play_turn(deadline)

    def winner(self):
        return self.game.winner()

    def announce_winner(self, timed_out=False):
        return self.game.announce_winner(timed_out)

    def play(self):
        print("Welcome to timed Pig! You have 60 seconds.")

        deadline = time.monotonic() + self.duration

        while time.monotonic() < deadline:
            if self.play_turn(deadline):
                self.announce_winner()
                return

            if time.monotonic() >= deadline:
                break

            self.game.current_player = (
                self.game.current_player + 1
            ) % len(self.players)

        self.announce_winner(timed_out=True)


def main():
    parser = argparse.ArgumentParser(
        description="Play the dice game Pig."
    )

    parser.add_argument(
        "--player1",
        choices=["human", "computer"],
        default="human"
    )

    parser.add_argument(
        "--player2",
        choices=["human", "computer"],
        default="human"
    )

    parser.add_argument(
        "--timed",
        action="store_true",
        help="Play a 60-second game."
    )

    args = parser.parse_args()

    if args.timed:
        game = TimedGameProxy(args.player1, args.player2)
    else:
        game = PigGame(args.player1, args.player2)

    game.play()


if __name__ == "__main__":
    main()
