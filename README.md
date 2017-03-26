# [LAN Grid Game](https://www.youtube.com/watch?v=hrKXdNcnNQw)
Game played over local wifi connection

Player 1                   |  Player 2
:-------------------------:|:-------------------------:
![](https://github.com/bfaure/wifi_grid_game/blob/master/resources/pictures/screenshot_mac.png)  |  ![](https://github.com/bfaure/wifi_grid_game/blob/master/resources/pictures/screenshot_windows.PNG)

## Instructions
Arrow keys to move, spacebar to shoot. Blocks are descructible, gems may be hidden underneath. 

# Installation
Run `python main.py` to open UI. Click on `Connect` menu option under `Connections` to enter the IP of another user.

## Dependencies
*  `Python 2.7`
* `PyQt4`

# Binaries
Binaries for Windows and Mac can be found in the /bin directory. For Windows you can just double click the main.exe file, for Mac you may have to open terminal, navigate to the bin/Mac folder and run `./main` to get the game to open correctly. The folders in /bin can be created by calling `python build.py` so long as you have pyinstaller installed already.
