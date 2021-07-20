import tkinter as tk
import random
from abc import ABC, abstractmethod
from collections import deque

class MainMenu(tk.Frame):

    def __init__(self, frame, game_columns, column_headers):
        super().__init__(frame)
        tk.Label(self, text='Game Options (Click)').grid(row=0, columnspan=2)
        for col, (header, games) in enumerate(zip(column_headers, game_columns)):
            tk.Label(self, text=header).grid(column=col, row=1)
            for i, game_type in enumerate(games):
                grid_row = i + 2 # options and headers take first two
                option_window = tk.Frame(self)
                option_window.grid(column=col, row=grid_row)
                GameOption(option_window, frame, game_type)



# Purpose: window where the game is managed.
#          They create a graphical user interface where the user can see the
#          game in a separate window

class SnakeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('660x660')
        self.title('Snake')
        game_columns = [[ClassicGame, EnemyClassicGame], [TwoPlayerGame, CompetitiveGame]]
        column_headers =  ['Single-Player (Arrow Keys)', 'Two-Player (WASD)']
        self.menu = MainMenu(self, game_columns, column_headers)                
        
    def forget_menu(self):
        self.menu.pack_forget()

    def invoke_menu(self):
        self.menu.pack()

    def run(self):
        self.invoke_menu()
        tk.mainloop()

# Purpose: GameOption objects represent an option for the SnakeGUI menu.

# Instance variables: 
#                     game - the game class which the GameSelectorFrame presents
#                     game_image - Tkinter PhotoImage, display for game_button
#                     game_button - Tkinter Button with game image belonging to game class, starts game mode
#                     game_title - string belonging to game class, is mode's title

class GameOption:
    def __init__(self, window, main_window, game_class):
        self.game = game_class
        self.game_image = tk.PhotoImage(file=self.game.image_file)

        game_button = tk.Button(window, image=self.game_image)
        def button_click():
            main_window.forget_menu()
            self.game(main_window, tk.Canvas(main_window, width = 660, height = 660))
        game_button.configure(command=button_click)
        game_button.pack()

        game_title = tk.Label(window, text=self.game.title)
        game_title.pack()

# Purpose: GameOverPopup objects represent a 'mini menu' which comes up upon ends of games.

class GameOverPopup:
    def __init__(self, window, game):
        # determine and add end-game message / scoring
        for message in game.results():
            msg_banner = tk.Label(window, text=message, font=('System', 30))
            msg_banner.pack()

        menu_button = tk.Button(window, text='MENU', font=('System', 15))
        menu_button.pack()
        menu_click = lambda: game.goto_menu()
        menu_button.configure(command=menu_click)

        restart_button = tk.Button(window, text='RESTART', font=('System', 15))
        restart_button.pack()
        restart_click = lambda: game.reset()
        restart_button.configure(command=restart_click)

        restart_str = tk.Label(window, text='Press \'R\' to restart')
        restart_str.pack()

# Purpose: ClassicGame objects represent an instance of the Snake Game itself.
#          They receive a tkinter canvas where the user can see the board and
#          GameObjects
#
#                  title - string representing game mode's title
#                  image_file - string which is name of the image file representing the game mode
#
# Instance variables: GUI - Object where ClassicGame is viewed - (original SnakeGUI object)
#                     canvas - displays/edits drawings/graphs, visual basis for game - tkinter.Canvas object
#                     player - reference representing player Snake - MainPlayer object
#                     snakes - list of snakes 'in' the game - list
#                     snakes_hidden - represents whether the snakes in the game are visible or not - tk BooleanVar
#                     pause_message - tk Label which conveys how to pause the game
#                     board - represents the boundary for the game - int -
#                             int serves as identifier for canvas widget
#                     pellet - represents a Food pellet - Food object
#                     game_over - Boolean that represents if game is over - True/False Boolean
#                     paused - Boolean that represents if snakes should move- True/False Boolean

#                     helper to initialize more variables and start the game
#         make_snakes - creates player snake and adds it to the game's snakes
#         bind_keys - binds keys to snake movement
#         start_game - initializes game board, objects, and states to defaults, starts gameloop
#         gameloop - makes all snakes execute move, determines how game should continue - main game 'driver'
#         reset_snakes - initializes all snakes in the game's snakes
#         reset - destroys/clears/initializes all objects, starts game again
#         pause - switches pause value, is method for a key binding
#         switch_snake_visibility - hides/unhides all snakes in the game's snakes, switches snakes_hidden value
#         death_sequence - hides/unhides all snakes 3 times, waiting a short period between each switch
#                          highlights game-ending move
#         goto_menu - destroys/clears all objects, invokes menu, DELETES SELF
class ClassicGame:

    title = "Classic Game"
    image_file = 'ClassicImage.png'

    def __init__(self, GUI, canvas):
        self.GUI = GUI
        self.canvas = canvas
        self.canvas.pack()
        self.make_snakes()
        self.bind_keys(['<Up>', '<Left>', '<Down>', '<Right>'], self.player)  # order compliments wasd
        self.GUI.bind('r', lambda _: self.reset())
        self.GUI.bind('<space>', lambda _: self.pause())
        self.start_game()

    def make_snakes(self):
        self.player = MainPlayer(self)
        self.snakes = [self.player]

    def bind_keys(self, key_list, snake):
        for key in key_list:
            self.GUI.bind(key, snake.set_dir_key)
    
    def start_game(self):
        self.pause_message = self.canvas.create_text(330, 15, text = 'Press Space to pause')
        self.board = self.canvas.create_rectangle(30, 30, 630, 630)
        pellet_x, pellet_y = random.choice([(i, j) for i in range(30, 600, 30) for j in range(30, 600, 30) if (i,j) != (330, 330)])  # prevents spawn on player
        self.pellet = Food(self, pellet_x, pellet_y, 'red')
        self.game_over, self.paused = False, False
        self.gameloop()
        
    def gameloop(self):
        if not self.paused and not all(snake.move() for snake in self.snakes): 
            self.paused = True  # keeps snakes from doing stuff during sequence
            self.canvas.delete(self.pause_message)
            self.end_sequence(times=6) # snake visibilty switches 6 times
        else: self.GUI.after(100, self.gameloop)

    def reset_snakes(self):
        for snake in self.snakes:
            snake.__init__(self)

    def reset(self):
        if not self.game_over: return
        self.over_frame.destroy()
        self.canvas.delete(tk.ALL)
        self.reset_snakes()
        self.start_game()

    def pause(self):
        self.paused = not self.paused

    def place(self):
        return (0.36, 0.36)

    def results(self):
        return ["GAME OVER", f"SCORE: {len(self.player.segments)}"]

    def switch_visibility(self, snake, state):
        for segment in snake.segments:
            self.canvas.itemconfig(segment, state=state)

    def end_sequence(self, times):
        if times == 0: 
            self.over_frame = tk.Frame(self.GUI, bd=4, relief='raised')
            popup_x, popup_y = self.place()
            self.over_frame.place(relx=popup_x, rely=popup_y)
            GameOverPopup(self.over_frame,self)
            self.game_over = True
            return
        new_state = "normal" if times % 2 else "hidden"
        for snake in self.snakes: self.switch_visibility(snake, new_state)
        self.GUI.after(200, lambda: self.end_sequence(times-1))        

    def goto_menu(self):
        self.over_frame.destroy()
        self.canvas.destroy()
        self.GUI.invoke_menu()

class EnemyClassicGame(ClassicGame):

    title = "Classic Game with Enemy"
    image_file = 'EnemyImage.png'

    
    def make_snakes(self):
        super().make_snakes()
        self.enemy = Enemy(self)
        self.player.clash(self.enemy)
        self.snakes.append(self.enemy)
        
    def reset_snakes(self):
        super().reset_snakes()
        self.player.clash(self.enemy)


class TwoPlayerGame(ClassicGame):

    title = "Two-Player Game - Passive"
    image_file = 'TwoPlayerImage.png'

    def make_snakes(self):
        super().make_snakes()
        self.player2 = Player2(self)
        self.snakes.append(self.player2)


    def start_game(self):
        self.bind_keys(['<w>', '<a>', '<s>', '<d>'], self.player2)  # order compliments wasd
        super().start_game()

    def place(self):
        return (0.28, 0.35)

    def results(self):
        winner = None
        scores = [len(player.segments) for player in self.snakes]
        p1_score, p2_score = scores
        if p1_score > p2_score: winner = "PLAYER 1"
        elif p1_score < p2_score: winner = "PLAYER 2"
        win_str = f"{winner} WINS!" if winner else "DRAW!"
        messages = [win_str]
        for i, score in enumerate(scores):
            messages.append(f"PLAYER {i+1} SCORE: {score}")
        return messages

class CompetitiveGame(TwoPlayerGame):

    title = "Two-Player Game - Aggresive"
    image_file = 'CompetitiveImage.png'

    def make_snakes(self):
        super().make_snakes()
        self.player.clash(self.player2)

    def reset_snakes(self):
        super().reset_snakes()
        self.player.clash(self.player2)

class GameObj(ABC):
    @abstractmethod
    def __init__(self, game, start_x, start_y, color):
        self.game = game
        self.x = start_x
        self.y = start_y
        self.color = color
        self.canvas = game.canvas

#                     deadly_snakes - list of snakes dangerous to self - dangerous implies game-ending collision
#                     vx - velocity in the x direction - int, 30, -30, or 0
#                     vy - velocity in the y direction - int, 30, -30, or 0
#                     segments - list of references to segments of snake - list of ints which are rectangle IDs for canvas
#
# Methods: __init__ - overload method, provides additional code;
#                     initializes variables, creates first segment
#         forward - changes position according to velocity
#         move_valid - checks whether snake's move is valid (not out of bounds or a dangerous collision) - returns Boolean
#         update - adds segment, creates pellet if one was consumed, otherwise deletes last segment
#         move - makes snake execute a game move, where it moves forward, it is determined if the move is valid, and if so updates
#                returns Boolean representing move-validity
#         set_dir - changes velocity to a specific direction
#         switch_visibility - hides/unhides the snake by doing so for all of its segments
#         clash - makes two snakes 'dangerous' to one another, appends each to each other's dangerous_snakes
class Snake(GameObj): 

    velocities = {'Up': (0, -30), 'Left': (-30, 0),
                  'Down': (0, 30), 'Right': (30, 0),
                  
                  'w': (0, -30), 'a': (-30, 0),
                  's': (0, 30), 'd': (30, 0),}
    @abstractmethod
    def __init__(self, game, start_x, start_y, color):
        super().__init__(game, start_x, start_y, color)
        self.deadly_snakes = []
        self.vx, self.vy = self.velocities['Right']
        self.segments = deque()
        self.segments.append(self.canvas.create_rectangle(self.x, self.y, self.x + 30, self.y + 30, fill=self.color))

    def forward(self):
        self.x = self.x + self.vx
        self.y = self.y + self.vy

    def move_valid(self):
        if (self.x < 30 or self.x > 600) or (self.y < 30 or self.y > 600):  # check bounds
            return False
        for snake in self.deadly_snakes:  # check if self-snake has intersected deadly snake, can include self
            for segment in snake.segments:
                    seg_x, seg_y, *_ = self.canvas.coords(segment)
                    if (self.x, self.y) == (seg_x, seg_y):
                            return False
        return True

    def update(self):
        self.segments.append(self.canvas.create_rectangle(self.x, self.y, self.x + 30, self.y + 30, fill=self.color)) # update - add segment at pos
        pellet = self.game.pellet
        if (self.x, self.y) == (pellet.x, pellet.y): pellet.create_pellet()
        else: self.canvas.delete(self.segments.popleft())

    def move(self):
        self.forward()
        if self.move_valid():
            self.update()  # updates food as well
            return True

    def set_dir(self, direction):
        self.vx, self.vy = self.velocities[direction]

    def clash(self, other):
        self.deadly_snakes.append(other)
        other.deadly_snakes.append(self)

# Methods: __init__ - overload method, provides additional code;
#                     makes snake dangerous to itself (basic Snake configuration)
#         set_dir_key - changes velocity to a direction determined by a binded key
class MainPlayer(Snake):

    def __init__(self, game, start_x=330, start_y=330, color='green'):
        super().__init__(game, start_x=start_x, start_y=start_y, color=color)
        self.deadly_snakes.append(self)

    def set_dir_key(self, event):
        key_direction = event.keysym  # keysym is instance var of KeyPress obj, ex. 'Up'
        if len(self.segments) > 1:
            invoked_vx, invoked_vy = Snake.velocities[key_direction]
            if invoked_vx != self.vx and invoked_vy != self.vy:  # checks that velocity is not opposite or same (in which case changing isn't necessary)
                self.set_dir(key_direction)
        else:
            self.set_dir(key_direction)

# Methods: __init__ - overload method, provides additional code;
#                     changes default color and start position
#         find_dir - lets enemy determine where food is located
#         move - overload method, provides additional code;
#                determines food direction before executing move
class Enemy(Snake):
    
    def __init__(self, game, start_x=30, start_y=30, color='purple'):
        super().__init__(game, start_x, start_y, color)

    def find_dir(self):
        if self.x < self.game.pellet.x: return 'Right'
        elif self.x > self.game.pellet.x: return 'Left'
        elif self.y > self.game.pellet.y: return 'Up'
        return 'Down'

    def move(self):
        direction = self.find_dir()
        self.set_dir(direction)
        return super().move()

# instance - reference to oval representing pellet - int which is ID for game canvas
# create_pellet - randomly chooses available spot, deletes instance and makes new one at spot
class Food(GameObj):

    def __init__(self, game, start_x, start_y, color):
        super().__init__(game, start_x, start_y, color)
        self.instance = self.canvas.create_oval(self.x, self.y, self.x + 30, self.y + 30, fill='red')

    def create_pellet(self):
        available_spots = {(i, j) for i in range(30, 600, 30) for j in range(30, 600, 30)}
        for snake in self.game.snakes:
            for segment in snake.segments:
                *unavailable_spot, _, _ = snake.canvas.coords(segment) # first two elements
                if tuple(unavailable_spot) in available_spots:  # check is necessary because consecutive food gathering/collisions cause errors
                    available_spots.remove(tuple(unavailable_spot))
        self.x, self.y = random.choice(tuple(available_spots))
        self.canvas.delete(self.instance)
        self.instance = self.canvas.create_oval(self.x, self.y, self.x + 30, self.y + 30, fill='red')

class Player2(MainPlayer):

    def __init__(self, game, start_x=300, start_y=330, color='blue'):
        super().__init__(game, start_x, start_y, color)
        self.vx = -30

if __name__ == '__main__':
    SnakeApp().run()