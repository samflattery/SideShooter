# SideShooter:

## Description:
My 15-112 Fundamentals of Programming term project. It is a multiplayer sidescroller shooter game with an infinite, randomly generated world.  The world is generated in such a way that it makes it more and more difficult for the player to traverse as they advance through the game.  The player gains score from killing enemies.  The game can be played single player on one computer, with two terminal instances of a terminal on one computer,  or with two players playing on different computers.  

## Pygame
If you do not have pygame installed on your computer, uncomment the first two lines of `client.py` and run the file.  Follow the instructions given.  The module manager is property of 15112 at CMU.

## How to Run:
Run:
```
python3 server.py
```
in a terminal instance.  Follow the prompts.

Open another terminal instance and run:
```
python3 client.py
```
Follow the prompts again.  Ensure the numbers match the output of the server file exactly.  If playing on two computers, run the `python3 client.py` line on the terminal of the other computer and follow the same prompts.

Be sure to `ctrl-C` the server process when done to ensure it does not continue to run in the background
