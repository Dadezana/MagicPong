from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from random import choice, uniform as randfloat
from functools import partial

class Powerup(Widget):
    powerup_types = {
        "red": 1,
        "purple": 2,
        "blue": 3,
        "green": 4,
        "yellow": 5
    }
    
    img = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = choice( list(self.powerup_types.keys()) )
        if self.color == "red":
            self.img = "img/red.png"

        elif self.color == "yellow":
            self.img = "img/yellow.png"

        elif self.color == "purple":
            self.img = "img/purple.png"

        elif self.color == "green":
            self.img = "img/lime.png"

        else:
            self.img = "img/blue.png"

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
    def invert_rules(self, game):
        game.areRulesInverted = True