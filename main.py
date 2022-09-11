from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from functools import partial
from kivy.core.window import Window
from random import randint

from particle import Particle
from powerup import Powerup
from ball import PongBall, AI_Ball
from paddle import PongPaddle

class PongGame(Widget):

    BORDER_WIDTH = NumericProperty(14)   # field's border
    border_r = NumericProperty(1)
    border_g = NumericProperty(1)
    border_b = NumericProperty(1)

    isSinglePlayer = True

    powerups = []
    MAX_POWERUPS = 10
    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    
    aiBalls = []

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
        Clock.schedule_interval(self.check_ball_collisions, 2.0/60.0)

    def create_powerup(self, dt):
        Clock.schedule_once(self.create_powerup, randint(3, 10))

        if not self.isGameStarted or len(self.powerups) >= self.MAX_POWERUPS:
            return

        p = Powerup()
        p.pos = randint(100, self.width-100), randint(50, self.height-50)
        self.add_widget(p)
        self.powerups.append(p)

    def update(self, dt):
        if not self.isGameStarted:
            return

        self.ball.move()
        self.move_ai_balls()
        self.check_ai_balls_collisions()

        self.player1.update_pos()
        self.player2.update_pos()


        if self.player1.is_colliding_with(self.ball):

            self.ball.lastCollide = self.player1

            if self.areRulesInverted:
                self.player2.score += 1
                self.areRulesInverted = False
                self.ball.reset()
                Clock.schedule_once(self.create_ai_ball, 2.1)

            self.create_ai_ball()

        elif self.player2.is_colliding_with(self.ball, self.isSinglePlayer):

            self.ball.lastCollide = self.player2

            if self.areRulesInverted:
                self.player1.score += 1
                self.areRulesInverted = False
                self.ball.reset()
                Clock.schedule_once(self.create_ai_ball, 2.1)
    # check collision with powerups
        isPowerupTaken, p = self.ball.is_touching_powerup(self.powerups)
        if isPowerupTaken:
            self.create_ai_ball()

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
                p.invert_rules(self)

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


    def move_ai_balls(self):
        for ai_ball in self.aiBalls:
            ai_ball.move()

    def check_ai_balls_collisions(self):
        for ai_ball in self.aiBalls:
            is_out_of_field = ai_ball.check_border_collisions(self)    # if the ball is out of the field
            if is_out_of_field:
                self.aiBalls.remove(ai_ball)
                self.remove_widget(ai_ball)

    def create_ai_ball(self, dt=0):
        ai_ball = AI_Ball()
        ai_ball.opacity = 0

        ai_ball.gotoxy(self.ball)
        ai_ball.set_speed(self.ball)

        self.aiBalls.append(ai_ball)
        self.add_widget(ai_ball)

    # checks collisions with walls
    def check_ball_collisions(self, dt=0):
        if (self.ball.y < 0+self.BORDER_WIDTH) or (self.ball.top > self.height-self.BORDER_WIDTH):
            self.ball.vel = (self.ball.vel_x, -self.ball.vel_y)
            if self.ball.vel_x > 0:
                self.create_ai_ball()
            return

        if (self.ball.x < 0):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                self.create_ai_ball()
                if self.isSinglePlayer:
                    self.player2.reset_paddle_pos()
                return
            self.player2.score += 1
            self.ball.reset()
            Clock.schedule_once(self.create_ai_ball, 2.1)

        elif (self.ball.right > self.width):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                if self.isSinglePlayer:
                    self.player2.reset_paddle_pos()
                return
            self.player1.score += 1
            self.ball.reset()
            Clock.schedule_once(self.create_ai_ball, 2.1)

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

    def create_particles(self, pos, color=(1, 1, 1), min_speed=5, max_speed=20, repeat=False, dt=0):
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
            self.ball.reset()
            Clock.schedule_once(self.create_ai_ball, 2.1)
            # if self.ball.vel_x < 0 and self.isSinglePlayer:
            #     self.aiBall.gotoxy(self.ball)
            #     self.aiBall.set_speed(self.ball)
        


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