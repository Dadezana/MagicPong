from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from functools import partial
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
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
    ball = ObjectProperty(None) # ball referenced in kv file
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    
    aiBall = ObjectProperty(None)
    powerup_aiball = None   # used every time the powerup is taken to recalculate the position of the paddle
    
    PADDLE_SPEED = 10
    MAX_POWERUPS = 10

    areRulesInverted = BooleanProperty(False) # when yellow powerup is taken, player have to let the ball bounce. If he touch it, the opponent scores a point
    isGameStarted = False

    particles = [[]]

    red_powerup_sound = SoundLoader().load("audio/RedPow.wav")
    yellow_powerup_sound = SoundLoader().load("audio/YellowTaken.wav")
    purple_powerup_sound = SoundLoader().load("audio/paddleAcc.wav")
    blue_powerup_sound = SoundLoader().load("audio/paddleSlow.wav")
    ball_collision_sound = [SoundLoader().load("audio/pong_colliding.wav") for i in range(5)]
    i = 0   # index of the collision sound to play

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player1.r = self.player1.paddle_high.r = self.player1.paddle_low.r = 0.06
        self.player1.g = self.player1.paddle_high.g = self.player1.paddle_low.g = 0.7
        self.player1.b = self.player1.paddle_high.b = self.player1.paddle_low.b = 0.98
        self.player2.r = self.player2.paddle_high.r = self.player2.paddle_low.r = 0.85
        self.player2.g = self.player2.paddle_high.g = self.player2.paddle_low.g = 0
        self.player2.b = self.player2.paddle_high.b = self.player2.paddle_low.b = 0
        self.powerup_aiball = AI_Ball()
        self.powerup_aiball.opacity = 0
        self.add_widget(self.powerup_aiball)
        Clock.schedule_once(self.create_powerup, randint(3, 10))
        bgMusic = SoundLoader().load("audio/BgMusic.wav")
        bgMusic.loop = True
        bgMusic.play()

    def create_powerup(self, dt):
        Clock.schedule_once(self.create_powerup, randint(3, 10))
        if len(self.particles) >= self.MAX_POWERUPS:
            return
        if not self.isGameStarted:
            return
        p = Powerup()
        p.pos = randint(200, self.width-200), randint(80, self.height-80)
        self.add_widget(p)
        self.powerups.append(p)

    def update(self, dt):
        if not self.isGameStarted:
            return

        self.ball.move()
        self.aiBall.move()
        self.powerup_aiball.move()

        # check collisions with wall
        if self.check_ball_collisions():
            self.play_ball_colliding_sound()

        self.aiBall.check_border_collisions(self)
        self.powerup_aiball.check_border_collisions(self)         

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
            self.powerup_aiball.gotoxy(self.ball)
            self.powerup_aiball.set_speed(self.ball)

            if p.color == "red":
                p.increase_ball_speed(self.ball)
                self.create_particles(
                    pos=(p.x, p.y), 
                    r=1, g=0, b=0,
                    repeat=True
                )
                self.red_powerup_sound.play()

            elif p.color == "green":
                p.decrease_opacity(self.ball, 0.15, resetOpacity=True)

            elif p.color == "yellow":
                p.invert_rules(self)
                self.create_particles(
                    pos=(p.x, p.y),
                    r=0.99, g=0.82, b=0.1
                )
                self.yellow_powerup_sound.play()

            elif p.color == "purple":
                p.increase_player_speed(self.ball.lastCollide, 8, resetSpeed=True)
                self.purple_powerup_sound.play()

            elif p.color == "blue":
                if self.ball.lastCollide == self.player1:
                    pl = self.player2
                else:
                    pl = self.player1
                p.increase_player_speed(pl, -4, resetSpeed=True)
                self.blue_powerup_sound.play()

            self.remove_widget(p)
            self.powerups.remove(p)

        self.handle_particles()

    # checks collisions with walls
    def check_ball_collisions(self, dt=0):
        if (self.ball.y < 0+self.BORDER_WIDTH):
            self.ball.vel = (
                self.ball.vel_x, 
                -self.ball.vel_y if (self.ball.y < self.height/2) and (self.ball.vel_y < 0) else self.ball.vel_y
            )
            return True
        elif (self.ball.top > self.height-self.BORDER_WIDTH):
            self.ball.vel = (
                self.ball.vel_x, 
                -self.ball.vel_y if (self.ball.y > self.height/2) and (self.ball.vel_y > 0) else self.ball.vel_y
            )
            return True

        if (self.ball.x < 0):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                self.aiBall.gotoxy(self.ball)
                self.aiBall.set_speed(self.ball)
                if self.isSinglePlayer:
                    self.player2.reset_paddle_pos()
                return True
            self.player2.score += 1
            self.ball.reset(self.aiBall)
            return True

        elif (self.ball.right > self.width):
            if self.areRulesInverted:
                self.ball.vel = (-self.ball.vel_x, self.ball.vel_y)
                self.areRulesInverted = False
                if self.isSinglePlayer:
                    self.player2.reset_paddle_pos()
                return True
            self.player1.score += 1
            self.ball.reset(self.aiBall)
            return True
        
        return False

    def play_ball_colliding_sound(self):
        self.ball_collision_sound[self.i].play()
        self.i = self.i+1 if self.i >= len(self.ball_collision_sound) else 0

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

    def create_particles(self, pos, r,g,b, min_speed=13, max_speed=14, repeat=False, dt=0):
        num = randint(25, 50)
        vel_offset = 360/num    # velocity offset beetwen two near particles
        wid_rotation = 0

        particle_group = []
        
        for n in range(num):
            p = Particle()
            p.init(
                pos=pos,
                r=r,g=g,b=b,
                min_speed=min_speed,
                max_speed=max_speed,
                rotation=wid_rotation
            )
            wid_rotation += vel_offset
            self.add_widget(p)
            particle_group.append(p)

        self.particles.append(particle_group)
        if repeat == True:
            Clock.schedule_once(partial(self.create_particles, pos, r,g,b, min_speed, max_speed), 0.05)

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
            self.ball.reset(self.aiBall, firstTime=True)
            if self.ball.vel_x < 0 and self.isSinglePlayer:
                self.aiBall.gotoxy(self.ball)
                self.aiBall.set_speed(self.ball)
        


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