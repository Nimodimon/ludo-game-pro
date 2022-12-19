import random
import time

import curses
from curses.textpad import Textbox

class Player:
    def __init__(self, field_size: int, player_name: str):
        self.field_size = field_size
        self.pawns_in_house = int((field_size - 3) / 2)
        self.player_name = player_name
        self.active_pawns = []
        self.blocked_cells = []

        self.set_start_limit()

    # Active pawns
    def add_pawn(self):
        medium = int((self.field_size - 1) / 2)

        if self.player_name == "a":
            self.active_pawns.append((0, medium + 1))
        elif self.player_name == "b":
            self.active_pawns.append((self.field_size - 1, medium - 1))

        self.pawns_in_house -= 1

    # Remove by index
    def remove_pawn(self, index: int):
        self.active_pawns.pop(index)

    def move_pawn_to_home(self, index: int):
        self.remove_pawn(index)
        self.pawns_in_house += 1

    def get_pawns(self) -> list[(int, int)]:
        return self.active_pawns

    def pawns_left(self):
        return self.pawns_in_house or self.active_pawns

    def get_pawns_in_house(self):
        return self.pawns_in_house

    # Blocked cells
    def set_blocked_cells(self):
        pawns = self.active_pawns
        self.blocked_cells = list(set([x for x in pawns if pawns.count(x) > 1]))
        self.set_start_limit()

    def set_start_limit(self):
        medium = int((self.field_size - 1) / 2)

        if self.player_name == "a":
            self.blocked_cells.append((medium - 1, medium))
        else:
            self.blocked_cells.append((medium + 1, medium))

    # Cells blocked by this player
    def get_blocked_cells(self) -> list[(int, int)]:
        return self.blocked_cells

    # Move
    def move_pawn(self, moves: int, blocked_cells: list[(int, int)]) -> bool:
        medium = int((self.field_size - 1) / 2)

        for ind, pawn in enumerate(self.active_pawns):
            new_position = pawn

            for _ in range(moves):
                new_position = self.get_next_position(new_position)

                if new_position in blocked_cells:
                    break
            else:
                if new_position[0] == medium and new_position[1] == medium:
                    self.remove_pawn(ind)
                else:
                    self.active_pawns[ind] = new_position
                    self.set_blocked_cells()
                return True

        return False

    def get_next_position(self, position: (int, int)):
        position = list(position)
        direction = self.get_direction(position)

        if direction == "right":
            position[1] += 1
        elif direction == "left":
            position[1] -= 1
        elif direction == "up":
            position[0] -= 1
        elif direction == "down":
            position[0] += 1

        return tuple(position)

    def get_direction(self, position: (int, int)):
        medium = int((self.field_size - 1) / 2)

        # Side direction points
        right_side_point = (
                position[0] == 0 and position[1] == medium - 1 or
                position[0] == medium - 1 and position[1] == 0 or
                position[0] == medium - 1 and position[1] == medium + 1
        )

        left_side_point = (
                position[0] == medium + 1 and position[1] == medium - 1 or
                position[0] == medium + 1 and position[1] == self.field_size - 1 or
                position[0] == self.field_size - 1 and position[1] == medium + 1
        )

        up_side_point = (
                position[0] == medium - 1 and position[1] == medium - 1 or
                position[0] == medium + 1 and position[1] == 0 or
                position[0] == self.field_size - 1 and position[1] == position[1] == medium - 1
        )

        down_side_point = (
                position[0] == 0 and position[1] == medium + 1 or
                position[0] == medium - 1 and position[1] == self.field_size - 1 or
                position[0] == medium + 1 and position[1] == medium + 1
        )

        right_side_row = (position[0] == 0 or position[0] == medium - 1)
        left_side_row = (position[0] == medium + 1 or position[0] == self.field_size - 1)
        up_side_column = (position[1] == 0 or position[1] == medium - 1)
        down_side_column = (position[1] == medium + 1 or position[1] == self.field_size - 1)

        medium_a = (position[1] == medium and position[0] != self.field_size - 1)
        medium_b = (position[1] == medium and position[0] != 0)

        if self.player_name == "a" and medium_a:
            return "down"
        elif self.player_name == "b" and medium_b:
            return "up"
        elif right_side_point:
            return "right"
        elif left_side_point:
            return "left"
        elif up_side_point:
            return "up"
        elif down_side_point:
            return "down"
        elif right_side_row:
            return "right"
        elif left_side_row:
            return "left"
        elif up_side_column:
            return "up"
        elif down_side_column:
            return "down"

class Game:
    def __init__(self, terminal):
        self.terminal = terminal
        self.field_size = terminal.field_size
        self.field = terminal.matrix

        self.player = Player(self.field_size, "a")
        self.another_player = Player(self.field_size, "b")

        self.player.add_pawn()
        self.another_player.add_pawn()

        self.turn = ""
        self.get_start_turn()

    def get_start_turn(self):
        while True:
            a_cube = int(random.random() * 6 + 1)
            b_cube = int(random.random() * 6 + 1)

            if a_cube > b_cube:
                return self.print_field("A moves first")
            elif a_cube < b_cube:
                self.change_turn()
                return self.print_field("B moves first")

    def change_turn(self):
        self.turn = self.another_player.player_name
        self.player, self.another_player = self.another_player, self.player

    def print_field(self, message: str = None):
        matrix = [list(row) for row in self.terminal.matrix]

        for player in (self.player, self.another_player):
            for pawn in player.get_pawns():
                matrix[pawn[0]][pawn[1]] = player.player_name.upper()

        self.terminal.print_matrix(matrix)

        if message:
            self.terminal.print_log(message)

    # Move
    def move_pawn(self, move: int) -> bool:
        did_move = self.player.move_pawn(move, self.another_player.get_blocked_cells())

        if did_move:
            self.try_to_bit_pawn()

        return did_move

    def six_move(self):
        if self.player.get_pawns_in_house():
            self.player.add_pawn()
            self.print_field(f"Player {self.player.player_name} adds new pawn")
        else:
            self.move_pawn(6)

    def make_move(self):
        for i in range(3):
            move = int(random.random() * 6 + 1)
            self.print_field(f"{self.player.player_name} got {move} on the cube")

            if move != 6:
                did_move = self.move_pawn(6)

                if not did_move:
                    self.print_field(f"No possible moves for {self.player.player_name}")

                break

            self.six_move()

        self.change_turn()

    def someone_won(self):
        return not self.player.pawns_left() or not self.another_player.pawns_left()

    def try_to_bit_pawn(self):
        same_pawn = list(set(self.player.get_pawns()) & set(self.another_player.get_pawns()))

        if same_pawn:
            pawn_ind = self.another_player.get_pawns().index(same_pawn[0])
            self.another_player.move_pawn_to_home(pawn_ind)
            self.print_field(f"Player {self.player.player_name} bit pawn of {self.another_player.player_name}")

class Terminal:
    def __init__(self, window: curses.window):
        self.window = window

        self.field_size = None
        self.matrix = None

    def input(self, prev_string: str):
        self.window.clear()
        self.window.addstr(prev_string)

        win = curses.newwin(1, 10, 0, len(prev_string))
        box = Textbox(win)

        self.window.refresh()

        return box.edit()

    def print(self, message: str):
        self.window.clear()
        self.window.addstr(message)
        self.window.refresh()

    def print_log(self, message: str):
        for ind, char in enumerate(message):
            self.window.addstr(self.field_size + 2, ind, char)
            self.window.refresh()
            time.sleep(0.10)

        time.sleep(1.25)

    def set_matrix(self, field_size: int):
        half = int((field_size - 1) / 2)

        matrix = [self.symmetry_row(" " * (half - 1) + "*", "*")]

        for i in range(half - 2):
            matrix.append(self.symmetry_row(" " * (half - 1) + "*", "D"))

        matrix.append(self.symmetry_row("*" * half, "D"))

        matrix.append(self.symmetry_row("*" + "D" * (half - 1), "X"))

        matrix.extend([list(i) for i in matrix][-2::-1])

        self.field_size = field_size
        self.matrix = matrix

    def print_matrix(self, matrix):
        numbers_list = [str(i % 10) for i in range(self.field_size)]

        horizontal_numbers = " " + self.get_spaced_row([""] + numbers_list)
        rows = [self.get_spaced_row([numbers_list[ind]] + row) for ind, row in enumerate(matrix)]

        self.print("\n".join([horizontal_numbers] + rows))

    @staticmethod
    def get_spaced_row(row) -> str:
        return (" " * 2).join(row)

    @staticmethod
    def symmetry_row(string_val: str, medium_char: str):
        return list(string_val + medium_char + string_val[::-1])

# Main
def set_size(terminal: Terminal) -> int:
    while True:
        size = terminal.input("Enter field size: ")
        correct_size, err = size_is_correct(size)

        if correct_size:
            return int(size)

        if err == "not_int":
            terminal.print("Field size must be int!")
            time.sleep(1)
        elif err == "too_many":
            terminal.print("Sorry, it`s too many for me")
            time.sleep(1)
        elif err == "val_props":
            terminal.print("Field size must be uncountable and more than 5")
            time.sleep(2)

        terminal.print("Try again")
        time.sleep(0.5)

def size_is_correct(size: str) -> (bool, str):
    size = size[:-1]

    if not size.isdigit():
        return False, "not_int"

    elif int(size) > 21:
        return False, "too_many"

    elif int(size) < 5 or int(size) % 2 == 0:
        return False, "val_props"

    return True, ""

def game(terminal: Terminal):
    game_instance = Game(terminal)

    while not game_instance.someone_won():
        game_instance.make_move()

    game_instance.print_field(f"{game_instance.another_player.player_name} player won")

def main(window: curses.window):
    terminal = Terminal(window)

    field_size = set_size(terminal)
    terminal.set_matrix(field_size)

    game(terminal)
    window.getch()

if __name__ == '__main__':
    curses.wrapper(main)
