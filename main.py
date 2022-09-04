from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint
from time import sleep

class PongGame(Widget):

    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    PADDLE_SPEED = 6

    isGameStarted = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

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
            self.ball.vel_y *= -1.05 if self.ball.vel_y < self.ball.MAX_VEL else -1
            return 0
        if (self.ball.x < 0):
            self.ball.vel_x *= -1.05 if self.ball.vel_x < self.ball.MAX_VEL else -1
            return 2
        elif (self.ball.right > self.width):
            self.ball.vel_x *= -1.05 if self.ball.vel_x < self.ball.MAX_VEL else -1
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

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'w':
            self.player1.center_y += 10
        elif keycode[1] == 's':
            self.player1.center_y -= 10
        if keycode[1] == 'up':
            self.player2.center_y += 10
        elif keycode[1] == 'down':
            self.player2.center_y -= 10
        return True

class PongBall(Widget):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    MAX_VEL = 15

    def move(self):
        self.pos = Vector(*self.vel) + self.pos

    def reset(self):
        self.pos = self.parent.center
        self.serve()

    def serve(self):
        self.vel_x = randint(3, 10)
        self.vel_y = randint(3, 10)
        # random ball direction
        a = [1, -1, -1, 1]
        self.vel_x *= a[self.vel_x % len(a)]
        self.vel_y *= a[self.vel_y % len(a)]
        
class PongPaddle(Widget):
    speed = 0       # speed of paddles
    touch_y = 0     # y point to reach when screen touched
    timer = 0
    score = NumericProperty(0)
    paddle_high = ObjectProperty(None)
    paddle_low = ObjectProperty(None)

    def update_pos(self):
        self.y += self.speed if (
            (self.speed < 0 and self.center_y > self.touch_y) 
            or 
            (self.speed > 0 and self.center_y < self.touch_y)
        ) else 0

    def bounce_ball(self, ball):
        self.timer -= 1
        if self.timer <= 0:
            if self.collide_widget(ball):
                self.debug_output(ball)     #//* temp debug output
                ball.vel_x *= -1
                self.timer = 60         # avoid the ball getting stuck in the paddle
    
    def debug_output(self, ball):
        if self.paddle_high.collide_widget(ball):
            print("Collided high")
        if self.paddle_low.collide_widget(ball):
            print("Collided low")

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