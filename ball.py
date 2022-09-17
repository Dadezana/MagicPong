from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from random import randint, uniform as randfloat
from kivy.vector import Vector
from functools import partial
from kivy.core.audio import SoundLoader

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

    crash_sound = SoundLoader().load("audio/BallCrash.wav")
    
    def move(self):
        self.pos = Vector(*self.vel) + self.pos

    def reset(self, aiBall, firstTime=False):
        if not firstTime:
            self.crash_sound.play()
        self.pos = (
            self.parent.center_x - self.width/2,
            self.parent.center_y - self.height/2
        )
        self.vel = (0, 0)
        Clock.schedule_once(partial(self.serve, aiBall), 2)

    def serve(self, aiBall, dt=0):
        self.vel_x = self.SPEED_X
        self.vel_y = self.SPEED_Y
        # random ball direction
        a = [1, -1, -1, 1]
        self.vel = (
            self.vel_x * a[randint(0, 10) % len(a)],
            self.vel_y * a[randint(0, 10) % len(a)]
        )
        aiBall.gotoxy(self)
        # if self.vel_x < 0:
        aiBall.set_speed(self)
        

    def is_touching_powerup(self, powerups):
        for p in powerups:
            if self.collide_widget(p):
                return True, p
        return False, None



class AI_Ball(Widget):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)

    def move(self):
        self.pos = Vector(*self.vel) + self.pos

    def gotoxy(self, ball):
        self.pos = (ball.x, ball.y)
    
    def set_speed(self, ball):
        isBallInvisible = ball.opacity < 0.5
        minError = 0.7 if isBallInvisible else 0.95
        maxError = 1.25 if isBallInvisible else 1.05

        error = randfloat(minError, maxError)
        self.vel = (ball.vel_x * 2 * error, ball.vel_y * 2)

    def check_border_collisions(self, field):
        if (self.y < 0+field.BORDER_WIDTH) or (self.top > field.height-field.BORDER_WIDTH):
            self.vel = (self.vel_x, -self.vel_y)
            return 0

        elif (self.right > field.width-field.player2.width):
            self.vel = (0, 0)
            self.move_ai_paddle(field)
            self.pos = (0, 0)
            return 1
    
    def move_ai_paddle(self, field):
        paddle = field.player2

        # if rules are inverted the AI will move the paddle to avoid the ball
        if not field.areRulesInverted:
            paddle.touch_y = self.y
        else:
            if self.y > field.height*2/3:
                paddle.touch_y = randint(0, field.height*1/3)
            elif self.y < field.height*1/3:
                paddle.touch_y = randint(field.height*2/3, field.height)
            else:
                paddle.touch_y = randint(field.height*2/3, field.height-paddle.height/2) if paddle.y+paddle.height/2 > 0 else randint(paddle.height/2, field.height*1/3)


        # move the player up/down
        paddle_center_y = paddle.y + paddle.height/2
        if paddle_center_y < paddle.touch_y:
            paddle.speed = field.PADDLE_SPEED + paddle.speed_added 
        else:
            paddle.speed = -(field.PADDLE_SPEED + paddle.speed_added)