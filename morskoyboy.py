from random import randint


class Error(Exception):
    pass


class BoardOutException(Error):
    def __str__(self):
        return "Shot outside board!"


class UsedCellException(Error):
    def __str__(self):
        return "This cell already shot!"


class WrongValueException(Error):
    def __str__(self):
        return "Invalid coordinates specified!"


class CannotPlaceShip(Error):
    def __str__(self):
        return "No suitable space for ship!"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, head, direction, length):
        self.head = head
        self.direction = direction
        self.length = length
        self.hp = length

    @property
    def dots(self):
        ship_cells = []
        for i in range(self.length):
            new_x, new_y = self.head.x, self.head.y
            if self.direction == 1:
                new_x += i
            elif self.direction == 2:
                new_y += i
            ship_cells.append(Dot(new_x, new_y))
        return ship_cells


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.alive = 6
        self.map = [['  ', '1', '2', '3', '4', '5', '6',],
                    ['1 ', '.', '.', '.', '.', '.', '.',],
                    ['2 ', '.', '.', '.', '.', '.', '.',],
                    ['3 ', '.', '.', '.', '.', '.', '.',],
                    ['4 ', '.', '.', '.', '.', '.', '.',],
                    ['5 ', '.', '.', '.', '.', '.', '.',],
                    ['6 ', '.', '.', '.', '.', '.', '.',],
                    ]

        self.used = []
        self.ships = []

    @staticmethod
    def outside(i):
        return False if (i.x in range(1, 7) and i.y in range(1, 7)) else True

    def add_ship(self, ship):

        for cell in ship.dots:
            if self.outside(cell) or cell in self.used:
                raise CannotPlaceShip()
        for cell in ship.dots:
            self.map[cell.x][cell.y] = "■"
            self.used.append(cell)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, cnt=False):
        contour_ = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1), (0, 0), (0, 1),
                    (1, -1), (1, 0), (1, 1)]
        for i in ship.dots:
            for a, b in contour_:
                c = Dot(i.x + a, i.y + b)
                if not (self.outside(c)) and c not in self.used:
                    if cnt:
                        self.map[c.x][c.y] = "0"
                    self.used.append(c)

    def show(self):
        for i in range(1):
            for j in range(7):
                if self.hid:
                    for a in range(7):
                        for b in range(7):
                            if self.map[a][b] == "■":
                                self.map[a][b] = "."
                print("|".join(self.map[j]) + "|")

    def hit(self, s):
        if self.outside(s):
            raise BoardOutException()
        if s in self.used:
            raise UsedCellException()
        self.used.append(s)
        for ship in self.ships:
            if s in ship.dots:
                ship.hp -= 1
                self.map[s.x][s.y] = "X"
                if ship.hp == 0:
                    self.alive -= 1
                    self.contour(ship, cnt=True)
                    print(f"Ship destroyed! {self.alive} ships left!")
                    print()
                    return True
                else:
                    print("Ship damaged!")
                    print()
                    return True

        self.map[s.x][s.y] = "0"
        print("Shot missed!")
        return False

    def check(self):
        self.used = []


class Player:
    def __init__(self, board, opp):
        self.board = board
        self.opp = opp

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.opp.hit(target)
                return repeat
            except Error as e:
                print(e)


class AI(Player):
    def ask(self):
        cords = Dot(randint(1, 6), randint(1, 6))
        print(f"AI shoots {cords.x}, {cords.y}")
        return cords


class User(Player):
    def ask(self):
        while True:
            cords = input("Specify x and y: ").split()
            if len(cords) != 2:
                raise WrongValueException()
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                raise WrongValueException()
            x, y = int(x), int(y)
            return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        board_1 = self.random_board()
        board_2 = self.random_board()
        board_2.hid = True
        self.user = User(board_1, board_2)
        self.ai = AI(board_2, board_1)

    def create_ships(self):
        ships = (3, 2, 2, 1, 1, 1, 1)
        board = Board(size=self.size)
        a = 0
        for i in ships:
            while True:
                a += 1
                if a > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), randint(1, 2), i)
                try:
                    board.add_ship(ship)
                    break
                except CannotPlaceShip:
                    print(f"Trying to create ship with length {i} one more time")
        board.check()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.create_ships()
        return board

    @staticmethod
    def greet():
        print("___________________")
        print("|   SEA  BATTLE   |")
        print("|*****************|")
        print("| Specify x and y |")
        print("|_____to shoot____|")

    def loop(self):
        turns = 0
        while True:

            print("User:")
            self.user.board.show()
            print("#" * 20)
            print("AI:")
            self.ai.board.show()
            if turns % 2 == 0:
                print("#" * 20)
                print("Make a turn")
                repeat = self.user.move()
            else:
                print("#" * 20)
                print("AI makes a turn")
                repeat = self.ai.move()
            if repeat:
                turns -= 1
            if self.ai.board.alive == 0:
                print("#" * 20)
                print("You win!")
                break
            elif self.user.board.alive == 0:
                print("-" * 20)
                print("AI wins!")
                break
            turns += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()