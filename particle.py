from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.clock import Clock
from random import choice, randint, uniform as randfloat
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.vector import Vector


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