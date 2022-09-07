from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from functools import partial
from kivy.core.window import Window
from kivy.graphics import Color
from random import randint, choice
from random import uniform as randfloat # random float num beetwen given range
# from threading import Timer

# timer
startTime = 0
endTime = 0
class PongGame(Widget):

    BORDER_WIDTH = NumericProperty(14)   # field's border
    border_r = NumericProperty(1)
    border_g = NumericProperty(1)
    border_b = NumericProperty(1)

    powerups = []
    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    PADDLE_SPEED = 10

    areRulesInverted = BooleanProperty(False) # when yellow powerup is taken, player have to let the ball bounce. If he touch it, the opponent scores a point
    isGameStarted = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player1.r = self.player1.paddle_high.r = self.player1.paddle_low.r = 0.06
        self.player1.g = self.player1.paddle_high.g = self.player1.paddle_low.g = 0.7
        self.player1.b = self.player1.paddle_high.b = self.player1.paddle_low.b = 0.98
        self.player2.r = self.player2.paddle_high.r = self.player2.paddle_low.r = 0.85
        self.player2.g = self.player2.paddle_high.g = self.player2.paddle_low.g = 0
        self.player2.b = self.player2.paddle_high.b = self.player2.paddle_low.b = 0
        Clock.schedule_once(self.create_powerup, randint(3, 10))

    def create_powerup(self, dt):
        if not self.isGameStarted:
            Clock.schedule_once(self.create_powerup, 5)
            return
        p = Powerup()
        p.pos = randint(100, self.width-100), randint(50, self.height-50)
        self.add_widget(p)
        self.powerups.append(p)
        Clock.schedule_once(self.create_powerup, randint(3, 10))
        # print("Powerup created")

    def update(self, dt):
        if self.isGameStarted:
            self.ball.move()

        # check collisions with wall
            res = self.check_ball_collisions()  # 1: player1 scored. 2: player2 scored
            if res == 1:
                self.player1.score += 1
                self.ball.reset()
            elif res == 2:
                self.player2.score += 1
                self.ball.reset()

            self.player1.update_pos()
            self.player2.update_pos()

            if self.player1.bounce_ball(self.ball):

                self.ball.lastCollide = self.player1

                if self.areRulesInverted:
                    self.player2.score += 1
                    self.areRulesInverted = False
                    self.ball.reset()

            elif self.player2.bounce_ball(self.ball):

                self.ball.lastCollide = self.player2

                if self.areRulesInverted:
                    self.player1.score += 1
                    self.areRulesInverted = False
                    self.ball.reset()
        # check collision with powerups
            isPowerupTaken, p = self.ball.is_touching_powerup(self.powerups)
            if isPowerupTaken:
                if p.color == "red":
                    p.increase_ball_speed(self.ball)

                elif p.color == "green":
                    p.decrease_opacity(self.ball, 0.15, resetOpacity=True)

                elif p.color == "yellow":
                    p.invert_rules(self, True)

                elif p.color == "purple":
                    p.increase_player_speed(self.ball.lastCollide, 8, resetSpeed=True)

                elif p.color == "blue":
                    if self.ball.lastCollide == self.player1:
                        pl = self.player2
                    else:
                        pl = self.player1
                    p.increase_player_speed(pl, -4, resetSpeed=True)

                self.remove_widget(p)
                self.powerups.remove(p)

# checks collisions with walls
    def check_ball_collisions(self):
        if (self.ball.y < 0+self.BORDER_WIDTH) or (self.ball.top > self.height-self.BORDER_WIDTH):
            self.ball.vel = (self.ball.vel_x, -self.ball.vel_y)
            return 0

        if (self.ball.x < 0):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                return 0
            return 2

        elif (self.ball.right > self.width):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                return 0
            return 1

    def on_touch_move(self, touch):
        if touch.x < self.width*1/3:
            player = self.player1
            self.player2.speed = 0
        elif touch.x > self.width*2/3:
            player = self.player2
            self.player1.speed = 0
        else:
            self.player1.speed = 0
            self.player2.speed = 0
            return

        # Any movement less than PADDLE_SPEED will not be taken into consideration to avoid vibration effect
        pl_offset_y = touch.y - (player.y + player.height/2)
        if pl_offset_y > -self.PADDLE_SPEED and pl_offset_y < self.PADDLE_SPEED:
            # print(f"Cannot move paddle. Offset: {pl_offset_y}")
            return
        
        # make sure the desired y to reach isn't outside the field
        if touch.y < self.BORDER_WIDTH + player.height/2:
            player.touch_y = self.BORDER_WIDTH + player.height/2
        elif touch.y > self.height - self.BORDER_WIDTH:
            player.touch_y = self.height - self.BORDER_WIDTH - player.height/2
        else:
            player.touch_y = touch.y
    
        # move the player up/down
        player_center_y = player.y + player.height/2
        if player_center_y < player.touch_y:
            player.speed = self.PADDLE_SPEED + player.speed_added
        else:
            player.speed = -(self.PADDLE_SPEED + player.speed_added)

    def on_touch_up(self, touch):
        self.player1.speed = 0
        self.player2.speed = 0

    def on_touch_down(self, touch):
        if not self.isGameStarted:
            self.isGameStarted = True
            self.ball.serve()

class PongBall(Widget):
    # those 2 are used to make the ball bounce off the walls. Every time the values inside "vel" change, they will do the same (they are binded to "vel")
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)       #! use always this to apply direction and speed to the ball
    opacity = NumericProperty(1)
    # those are used to keep the ball at a constant speed, since "vel_x" and "vel_y" are binded to "vel" and they will increase continuously
    SPEED_X = 10
    SPEED_Y = 10
    MAX_VEL = 15
    lastCollide = None  #! Do not use this to modify player variables!

    def move(self):
        self.pos = Vector(*self.vel) + self.pos

    def reset(self):
        self.pos = (
            self.parent.center_x - self.width/2,
            self.parent.center_y - self.height/2
        )
        self.vel = (0, 0)
        Clock.schedule_once(self.serve, 2)

    def serve(self, dt=0):
        self.vel_x = self.SPEED_X
        self.vel_y = self.SPEED_Y
        # random ball direction
        a = [1, -1, -1, 1]
        self.vel = (
            self.vel_x * a[randint(0, 10) % len(a)],
            self.vel_y * a[randint(0, 10) % len(a)]
        )

    def is_touching_powerup(self, powerups):
        for p in powerups:
            if self.collide_widget(p):
                return True, p
        return False, None
        
class PongPaddle(Widget):
    speed = 0       # speed of paddles
    touch_y = 0     # y point to reach when screen touched. Refers to the center of the paddle
    timer = 0
    score = NumericProperty(0)
    paddle_high = ObjectProperty(None)
    paddle_low = ObjectProperty (None)
    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)
    speed_added = 0             # increase or decrease paddle speed when touching purple/blue powerups

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_pos(self):

        if self.speed < 0 and self.y+self.height/2 < self.touch_y:
            self.speed = 0
            return
        if self.speed > 0 and self.y+self.height/2 > self.touch_y:
            self.speed = 0
            return

        next_y = self.y + self.speed    # y to reach next frame

        if next_y > self.parent.height - self.parent.BORDER_WIDTH - self.height:
            next_y = self.parent.height - self.parent.BORDER_WIDTH - self.height
            self.speed = 0
        elif next_y < 45:
            # //elif next_y < self.parent.BORDER_WIDTH:
            # //next_y = self.parent.BORDER_WIDTH
            next_y = 45     # 45 because that seems the top y of the bottom border
            self.speed = 0

        self.y = next_y
        

    def bounce_ball(self, ball):
        self.timer -= 1
        if self.timer <= 0:
            if self.collide_widget(ball):
                self.determine_ball_dir(ball)
                ball.vel = (-ball.vel_x, ball.vel_y)
                self.timer = 60         # avoid the ball getting stuck in the paddle
                return True
        return False

    def determine_ball_dir(self, ball):

        # if the ball touches the edges of the paddle, the angles made by the ball will be sharpest (does not apply in straight)
        hasTouchedEdge = self.paddle_high.collide_widget(ball) or self.paddle_low.collide_widget(ball)
        multiplier_min = 1.2 if hasTouchedEdge else 1
        multiplier_max = 1.5 if hasTouchedEdge else 1

        direction = self.speed      # paddle direction
        if direction > 0:
            sp_y = ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        elif direction < 0:
            sp_y = -ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        else:
            sp_x = (ball.SPEED_X * randfloat(1.2, 1.6)) if ball.vel_x > 0 else (-ball.SPEED_X * randfloat(1.2, 1.6))    # preserve direction
            ball.vel = (sp_x, randfloat(-1, 1))
        

class PongPaddleEdge(Widget):
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)


class Powerup(Widget):
    powerup_types = {
        "red": 1,
        "purple": 2,
        "blue": 3,
        "green": 4,
        "yellow": 5
    }
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = choice( list(self.powerup_types.keys()) )
        self.color = "yellow"
        if self.color == "red":
            self.r = 1
            self.g = 0
            self.b = 0
        elif self.color == "yellow":
            self.r = 0.99
            self.g = 0.82
            self.b =  0.1
        elif self.color == "purple":
            self.r = 0.55
            self.g = 0 
            self.b = 0.76
        elif self.color == "green":
            self.r = 0.37
            self.g = 0.83 
            self.b = 0.03
        else:
            self.r = 0
            self.g = 0.15
            self.b = 1

    # red powerup
    def increase_ball_speed(self, ball):
        ball.vel = (
            ball.vel_x * randfloat(1.2, 2),
            ball.vel_y * randfloat(1.2, 2)
        )

    # purple/blue powerup
    def increase_player_speed(self, player, sp, dt=0, resetSpeed=False):
        player.speed_added = sp
        if resetSpeed:
            Clock.schedule_once(partial(self.increase_player_speed, player, 0), 5)

    # green powerup
    def decrease_opacity(self, ball, opacity, dt=0, resetOpacity=False):
        ball.opacity = opacity
        if resetOpacity:
            Clock.schedule_once(partial(self.decrease_opacity, ball, 0), 0.2)
            Clock.schedule_once(partial(self.decrease_opacity, ball, 0.15), 0.5)
            Clock.schedule_once(partial(self.decrease_opacity, ball, 1), 1.3)
    
    # yellow powerup
    def invert_rules(self, game, canInvert):
        game.areRulesInverted = canInvert


class PongApp(App):
    WIN_W = 1280
    WIN_H = 720
    def build(self):
        game = PongGame()
        Window.size = (self.WIN_W, self.WIN_H)
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game

if __name__ == '__main__':
    PongApp().run()