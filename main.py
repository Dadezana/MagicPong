from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint
from random import uniform as randfloat # random float num beetwen given range
from time import sleep

class PongGame(Widget):

    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    PADDLE_SPEED = 10

    isGameStarted = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
            
            self.player1.bounce_ball(self.ball)
            self.player2.bounce_ball(self.ball)

# checks collisions with walls
    def check_ball_collisions(self):
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.vel = (self.ball.vel_x, -self.ball.vel_y)
            return 0
        if (self.ball.x < 0):
            self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
            return 2
        elif (self.ball.right > self.width):
            self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
            return 1

    def on_touch_move(self, touch):  
        if (touch.x < self.width*1/3):
            self.player1.touch_y = touch.y
            pl_y = self.player1.y + self.player1.height/2 # center of the paddle

            if(pl_y < self.player1.touch_y):
                self.player1.speed= self.PADDLE_SPEED
            
            elif(pl_y > self.player1.touch_y):
                self.player1.speed = -self.PADDLE_SPEED

        elif(touch.x > self.width*2/3):
            self.player2.touch_y = touch.y
            pl_y = self.player2.y + self.player2.height/2 # center of the paddle
            
            if(pl_y < self.player2.touch_y):
                self.player2.speed = self.PADDLE_SPEED
            
            elif(pl_y > self.player2.touch_y):
                self.player2.speed = -self.PADDLE_SPEED

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
    # those are used to keep the ball at a constant speed, since "vel_x" and "vel_y" are binded to "vel" and they will increase continuously
    SPEED_X = 10
    SPEED_Y = 10
    MAX_VEL = 15

    def move(self):
        self.pos = Vector(*self.vel) + self.pos

    def reset(self):
        self.pos = self.parent.center
        self.serve()

    def serve(self):
        self.vel_x = self.SPEED_X
        self.vel_y = self.SPEED_Y
        # random ball direction
        a = [1, -1, -1, 1]
        self.vel = (
            self.vel_x * a[self.vel_x % len(a)],
            self.vel_y * a[self.vel_y % len(a)]
        )
        
class PongPaddle(Widget):
    speed = 0       # speed of paddles
    touch_y = 0     # y point to reach when screen touched
    timer = 0
    score = NumericProperty(0)
    paddle_high = ObjectProperty(None)
    paddle_low = ObjectProperty(None)


    def update_pos(self):
        if not (self.speed < 0 and self.center_y > self.touch_y) and not (self.speed > 0 and self.center_y < self.touch_y):
            self.speed = 0
            
        self.y += self.speed

    def bounce_ball(self, ball):
        self.timer -= 1
        if self.timer <= 0:
            if self.collide_widget(ball):
                self.debug_output(ball)     #* temp debug output
                
                self.determine_ball_dir(ball)

                ball.vel = (-ball.vel_x, ball.vel_y)
                self.timer = 60         # avoid the ball getting stuck in the paddle

    def determine_ball_dir(self, ball):

        # if the ball touches the edges of the paddle, the angles made by the ball will be sharpest (does not apply in straight)
        hasTouchedEdge = self.paddle_high.collide_widget(ball) or self.paddle_low.collide_widget(ball)
        multiplier_min = 1.2 if hasTouchedEdge else 1
        multiplier_max = 1.5 if hasTouchedEdge else 1

        direction = self.speed      # paddle direction
        print(f"ball_vel: {ball.vel}")
        if direction > 0:
            sp_y = ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        elif direction < 0:
            sp_y = -ball.SPEED_Y * randfloat(1.1, 1.5) * randfloat(multiplier_min, multiplier_max)
            ball.vel = (ball.vel_x, sp_y)
        else:
            sp_x = (ball.SPEED_X * randfloat(1.2, 1.6)) if ball.vel_x > 0 else (-ball.SPEED_X * randfloat(1.2, 1.6))    # preserve direction
            ball.vel = (sp_x, randfloat(-1, 1))

    
    def debug_output(self, ball):
        if self.paddle_high.collide_widget(ball):
            print("Collided high")
        elif self.paddle_low.collide_widget(ball):
            print("Collided low")
        # if self.speed > 0:
        #     print("Direction: up")
        # elif self.speed < 0:
        #     print("Direction: down")
        # else:
        #     print("Direction: stop")
        

class PongPaddleEdge(Widget):
    pass

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