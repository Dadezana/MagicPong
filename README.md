# MagicPong

## How to play
MagicPong is the game of pong, but different. You can control ball's direction by moving the paddle while touching the ball: 
- if the paddle moves up, the ball goes up
- if the paddle moves down, the ball goes down
- if the paddle doesn't move, the ball goes straight

You can use this to your advantage to take different powerups to enhance the probability of scoring:

<img src="img/red.png"> <span style="position: absolute;margin-top:10px">It's like chili peppers... but for balls :)</span>

<img src="img/yellow.png" style="margin-left: -8px;"> <span style="position: absolute;margin-top:23px">This invert the rules till the ball touches borders. Avoid the ball instead of catching it!</span>

<img src="img/lime.png"> <span style="position: absolute;margin-top:20px">Do you have a good eyesight?</span>

<img src="img/purple.png"> <span style="position: absolute;margin-top:25px">What's better of being flash in a pong game?</span>

<img src="img/blue.png"> <span style="position: absolute;margin-top:20px">Who goes slowly, goes healthy and far</span>

## How to run
### Required dependencies
```
pip install kivy
```
On arch based distro I suggest to always use `pacman` to install python packages:
```bash
pacman -S python-kivy
```
### Run
```bash
python main.py
```