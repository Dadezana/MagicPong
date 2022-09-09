from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from functools import partial
from kivy.core.window import Window
from kivy.graphics import Color
from random import randint, choice
from random import uniform as randfloat # random float num beetwen given range
from kivy.graphics.vertex_instructions import Ellipse
from kivy.graphics.context_instructions import Color
from kivy.graphics import PushMatrix, PopMatrix, Rotate

# timer
startTime = 0
endTime = 0
class PongGame(Widget):

    BORDER_WIDTH = NumericProperty(14)   # field's border
    border_r = NumericProperty(1)
    border_g = NumericProperty(1)
    border_b = NumericProperty(1)

    isSinglePlayer = True

    powerups = []
    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    aiBall = ObjectProperty(None)
    PADDLE_SPEED = 10

    areRulesInverted = BooleanProperty(False) # when yellow powerup is taken, player have to let the ball bounce. If he touch it, the opponent scores a point
    isGameStarted = False

    particles = [[]]

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
        if not self.isGameStarted:
            return

        self.ball.move()
        self.aiBall.move()

    # check collisions with wall
        self.aiBall.check_border_collisions(self)
        res = self.check_ball_collisions()  # 1: player1 scored. 2: player2 scored
        if res == 1:
            self.player1.score += 1
            self.ball.reset(self.aiBall)
        elif res == 2:
            self.player2.score += 1
            self.ball.reset(self.aiBall)

        self.player1.update_pos()
        self.player2.update_pos()


        if self.player1.bounce_ball(self.ball):

            self.ball.lastCollide = self.player1

            if self.areRulesInverted:
                self.player2.score += 1
                self.areRulesInverted = False
                self.ball.reset(self.aiBall)
            
            self.aiBall.gotoxy(self.ball)
            self.aiBall.set_speed(self.ball)

        elif self.player2.bounce_ball(self.ball, self.isSinglePlayer):

            self.ball.lastCollide = self.player2

            if self.areRulesInverted:
                self.player1.score += 1
                self.areRulesInverted = False
                self.ball.reset(self.aiBall)
    # check collision with powerups
        isPowerupTaken, p = self.ball.is_touching_powerup(self.powerups)
        if isPowerupTaken:
            # recalculate final position after a powerup is taken
            self.aiBall.gotoxy(self.ball)
            self.aiBall.set_speed(self.ball)

            if p.color == "red":
                p.increase_ball_speed(self.ball)
                self.create_particles(
                    pos=(p.x, p.y), 
                    color=(1, 0, 0), 
                    min_speed=13, 
                    max_speed=14, 
                    repeat=True
                )

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

        self.handle_particles()

# checks collisions with walls
    def check_ball_collisions(self):
        if (self.ball.y < 0+self.BORDER_WIDTH) or (self.ball.top > self.height-self.BORDER_WIDTH):
            self.ball.vel = (self.ball.vel_x, -self.ball.vel_y)
            return 0

        if (self.ball.x < 0):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                self.aiBall.gotoxy(self.ball)
                self.aiBall.set_speed(self.ball)
                return 0
            return 2

        elif (self.ball.right > self.width):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                return 0
            return 1

    def handle_particles(self):
        for particle_group in self.particles:
            for p in particle_group:
                p.move()
                p.fade()
                if p.opacity < -0.2:
                    for i in particle_group:
                        self.remove_widget(i)
                    self.particles.remove(particle_group)
                    break

    def create_particles(self, pos, color=(1, 1, 1), min_speed=5, max_speed=20, repeat=False):
        num = randint(25, 50)
        vel_offset = 360/num    # velocity offset beetwen two near particles
        wid_rotation = 0

        particle_group = []
        
        for n in range(num):
            p = Particle()
            p.init(
                pos=pos,
                color=color,
                min_speed=min_speed,
                max_speed=max_speed,
                rotation=wid_rotation
            )
            wid_rotation += vel_offset
            self.add_widget(p)
            particle_group.append(p)

        self.particles.append(particle_group)
        if repeat == True:
            Clock.schedule_once(partial(self.create_particles, pos, color, min_speed, max_speed), 0.05)

    def on_touch_move(self, touch):
        if touch.x < self.width*1/3:
            player = self.player1
            self.player2.speed = 0
        elif touch.x > self.width*2/3:
            if self.isSinglePlayer:
                return
            player = self.player2
            self.player1.speed = 0
        else:
            self.player1.speed = 0
            self.player2.speed = 0
            return

        # Any movement less than PADDLE_SPEED will not be taken into consideration to avoid vibration effect
        pl_offset_y = touch.y - (player.y + player.height/2)
        if pl_offset_y > -self.PADDLE_SPEED and pl_offset_y < self.PADDLE_SPEED:
            return

        player.touch_y = touch.y
    
        # move the player up/down
        player_center_y = player.y + player.height/2
        if player_center_y < player.touch_y:
            player.speed = self.PADDLE_SPEED + player.speed_added
        else:
            player.speed = -(self.PADDLE_SPEED + player.speed_added)

    def on_touch_up(self, touch):
        self.player1.speed = 0
        self.player2.speed = 0 if not self.isSinglePlayer else self.player2.speed

    def on_touch_down(self, touch):
        if not self.isGameStarted:
            self.isGameStarted = True
            self.ball.reset(self.aiBall)
            if self.ball.vel_x < 0 and self.isSinglePlayer:
                self.aiBall.gotoxy(self.ball)
                self.aiBall.set_speed(self.ball)
        
       
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

    def reset(self, aiBall):
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
            sp_x = (ball.SPEED_X * randfloat(1.2, 1.6)) if ball.vel_x > 0 else (-ball.SPEED_X * randfloat(1.2, 1.6))    # preserve direction
            ball.vel = (sp_x, randfloat(-1, 1))
        
    def reset_paddle_pos(self):
        if not self.y+self.height/2 < self.parent.height*1/3 and not self.y+self.height/2 > self.parent.height*2/3:
            return
        
        self.touch_y = randint(self.parent.height*1/3, self.parent.height*2/3)
        self.speed = (self.parent.PADDLE_SPEED + self.speed_added) if self.touch_y > self.y+self.height/2 else -(self.parent.PADDLE_SPEED + self.speed_added)
        

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
        minError = 0.7 if isBallInvisible else 0.9
        maxError = 1.25 if isBallInvisible else 1.1

        error = randfloat(minError, maxError)
        self.vel = (ball.vel_x * 2 * error, ball.vel_y * 2)

    def check_border_collisions(self, field):
        if (self.y < 0+field.BORDER_WIDTH) or (self.top > field.height-field.BORDER_WIDTH):
            self.vel = (self.vel_x, -self.vel_y)
            return 0

        elif (self.right > field.width):
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

class Particle(Widget):
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    vel = ReferenceListProperty(vel_x, vel_y)
    size = (5, 5)
    color = (1, 0, 0)
    opacity_decrease = 1.0/30.0

    # both "pos" and "color" must be a list
    def init(self, pos, color, rotation, min_speed, max_speed):
        randSize = randint(2, 5)
        self.size = (randSize, randSize)
        self.color = color
        self.pos = pos
        self.vel_x = randint(min_speed, max_speed)
        self.vel_y = 0
        self.opacity = 1
        # rotate the particle
        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=rotation, origin=pos)    # "pos" is the point where the particles are generated
        # if you don't use this, all the widget will rotate
        with self.canvas.after:
            PopMatrix()

    def fade(self):
        self.opacity -= self.opacity_decrease

    def move(self):
        self.pos = Vector(*self.vel) + self.pos


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