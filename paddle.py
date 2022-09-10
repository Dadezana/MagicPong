from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import NumericProperty, ObjectProperty
from random import choice, randint, uniform as randfloat


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
            next_y = 45     # 45 because that seems the top y of the bottom border
            self.speed = 0

        self.y = next_y
        

    def bounce_ball(self, ball, randomDir=False):
        self.timer -= 1
        if self.timer <= 0:
            if self.collide_widget(ball):
                self.determine_ball_dir(ball, randomDir)
                ball.vel = (-ball.vel_x, ball.vel_y)
                self.timer = 60         # avoid the ball getting stuck in the paddle
                if randomDir:
                    self.reset_paddle_pos()
                return True
        return False

    def determine_ball_dir(self, ball, randomDir=False):

        # if the ball touches the edges of the paddle, the angles made by the ball will be sharpest (does not apply in straight)
        hasTouchedEdge = self.paddle_high.collide_widget(ball) or self.paddle_low.collide_widget(ball)
        multiplier_min = 1.2 if hasTouchedEdge else 1
        multiplier_max = 1.5 if hasTouchedEdge else 1

        direction = self.speed      # paddle direction

        if randomDir:
            dirs = [-1, 0, 1]   # -1: down, 0: straight, 1: up
            direction = choice(dirs)

        if direction > 0:
            sp_y = ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        elif direction < 0:
            sp_y = -ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        else:
            sp_x = (ball.SPEED_X * randfloat(1.5, 2)) if ball.vel_x > 0 else (-ball.SPEED_X * randfloat(1.5, 2))    # preserve direction
            ball.vel = (sp_x, randfloat(-1.3, 1.3))
        
    def reset_paddle_pos(self):
        if not self.y+self.height/2 < self.parent.height*1/3 and not self.y+self.height/2 > self.parent.height*2/3:
            return
        
        self.touch_y = randint(self.parent.height*1/3, self.parent.height*2/3)
        self.speed = (self.parent.PADDLE_SPEED + self.speed_added) if self.touch_y > self.y+self.height/2 else -(self.parent.PADDLE_SPEED + self.speed_added)
        

class PongPaddleEdge(Widget):
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)

