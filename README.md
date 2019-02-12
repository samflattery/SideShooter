# SideShooter
Multiplayer infinite sidescroller game made with Python

Description:
My project is called SideShooter.  It is a multiplayer sidescroller shooter game with an infinite, randomly generated world.  The world is generated in such a way that it makes it more and more difficult for the player to traverse as they advance through the game.  The player gains score from killing enemies.  The game can be played single player on one computer or with two players playing on different computers.  

How to Run:
Open the server.py file in a python program and change the PORT number at the top of the file.  Run the file.
Open the client.py file and follow the instructions in the capital letter comments between the double hash signs - ## COMMENTS LIKE THESE ##
The setup for the game will depend on whether or not you want to play on two different computers.  
For me, running the client.py file in Sublime gave me a broken pipe error, whereas opening it in Pyzo worked fine.  If you get a broken pipe error directly upon opening the file in a python program, I have included a shell script that runs the client file from the terminal, which worked for me.  
For ease of use, put this shell script in the directory that your terminal automatically opens when it launches.  On Mac, this is usually the home folder with your name on it.  Type "vim main.sh" and  edit the path after the "cd" to the path where your SideShooter folder is located.  Then, to run the file, all you must do is open the terminal and type "./main.sh".
Alternatively, you can use the terminal to navigate to the SideScroller directory and type "python3 client.py".  
To play single player, follow the above steps.  The PORT number will be automatically read from the server.py file.  
To play multiplayer, download the SideScroller directory onto another computer.  Run the server.py file as above on one computer, and change the MULTIPLAYERPORT variable in the client.py file on both computers to the PORT number in the server.py file.  Run the two client.py files as above.  

Pygame:
If you do not have pygame on your computer, uncomment the two module_manager lines on the top of the client.py file and follow the instructions it gives.  The module_manager file is the property of 15112 at CMU. 

CPU Intensive:
The server put quite a strain on my computer's CPU and after testing the game a few times in a row, my fan would start and my computer and the game would slow down.  To prevent this, I use the Activity Monitor on Mac to close the python program after every time I play, which speeds up gameplay and avoids lag as much as possible.   

Image Credits:
https://www.flaticon.com/free-icon/bullet_224681
https://www.codeproject.com/KB/HTML/756189/MasterChiefOriginal.png
https://www.deviantart.com/cosbydaf/art/Tank-spritesheet-587230376
http://probertson.tumblr.com/post/53324495092/tributegames-pixeltao-heres-a-few-classic
https://www.google.com/search?q=sprite+background+sky&source=lnms&tbm=isch&sa=X&ved=0ahUKEwjV2raW2IvfAhWD2FkKHUCaCr4Q_AUIDigB&biw=1103&bih=697&dpr=2#imgrc=VlmKOdVPEjEaHM:
https://www.google.com/search?as_st=y&hl=en&tbm=isch&sa=1&ei=cVcJXMKXJses5wK2i6yYAQ&q=parallax+mountains&oq=parallax+mountains&gs_l=img.3..0.14139.16226..16373...0.0..0.68.1125.18......1....1..gws-wiz-img.......35i39j0i67j0i30j0i5i30j0i8i30j0i24.UN1vzgGqFWY&tbas=0#imgrc=6DkQG13U2cZ9MM:
