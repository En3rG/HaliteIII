# Thanks!

Again, thanks to Two Sigma for the awesome competition.  This is my third halite competition and I am looking forward for the 4th one!

# Bot Summary

Heres a quick summary of how my bot works:

* Initialization: (before sending ready to the game engine). Quickly analyze the map, get cell distances, get averages of each cell, and determine best dock locations.  
* Gather map data per turn:  Generate the data structure to be used throughout the bot.
* Retreat:  Determine whether its time to retreat (end game). 
* Stuck: Determine ships that are unable to move.
* Build: Determine ships that will be building a dock.
* Explore Target: Determine each ships target cell.
* Deposit: Move ships returning/depositing.
* Harvest: Move ships harvesting at its current position.
* Attack: Move ships and support ships toward a certain target.
* Explore: Move remaining ships to its target locations.
* Spawn: Determine if we are spawning a ship.

## Initialization

Each bot has 30 seconds to precompute or analyze the map.  I didnt really get to utilize this time that much.  I do generate a map of the distances of each cell to one another, get averages of each cell, and determine where are the highest halite with high average, to build docks.

## Gather Data

Here I generate a lot of parameters/variables that are used throughout the bot.  But mostly, this is where I generate a lot of numpy arrays, such as:
* Ship locations
* Dock locations
* Ship cargo
* Halite amount
* Cost amount
* Harvest amount (with inspiration)
* Cells close to enemy
* Dock manhattan (area around a dock to be built soon)
* Potential enemy collisions (counts how many potential enemy ships can go to each cell)

## Retreat

Here I determine the distance of all ships to the closest dock.  I have a parameter called retreat.extra_turn, that is added to the furthest ship.  If this number is greater or equal to the remaining turns left in the game, all ships will be commanded to retreat.  One disadvantage to this is that very close ships to the dock will also be commanded to go home, where it can really harvest more halite.  I didnt get a chance to make this better.

## Stuck

Here I determine each ships that cannot move, due to insufficient halite cargo.

## Build

Here I determine each ships that are to build docks.  I have 3 kinds of docks.  One, that was determine during the initialization.  If a ship is close to that location and it has a certain amount of cargo, it will move towards that location and wait until there is enough halite to build a dock.  Once this ship is commanded that its going to build (in the future), I pretend that a dock is already built there.  This causes the swarm or forecast that other players had as well.  The second type of dock is when a ship is on a cell that has halite greater than a certain number (I used 3500).  If so, it'll just build a dock there without taking into account if there are docks close by.  The third dock is similar to the second one, but it only look for cells with greater than 1500.  The difference here is that it will check whether a dock is at a certain distance away.  If there exist a dock close by, it will not build a dock.  Most parameters are located in the values.py, where all these can just be updated to a different value.  My bot acts a lot different by just changing a lot of these values around.

## Explore Target

Here I determine the target of each ships.  I also take into account the ships moved above, such as stuck and building ships.  Ship that are closest to the target gets priority.  A score is determined by halite amount divided by the distance from the ship and distance to home.  If that target has a high 'score', other ships may also target that cell. This depends on the perecent_deduction parameter, where it specifies how much score we are deducting from that cell.  If the percent_deduction is really high, then most likely only one ship will target a cell.  If the percent_deduction is small, multiple ships may target a cell with high score which causes a swarm like effect that helps take over high collision areas.

## Deposit

Here ships determined to be depositing from explore target will be moved.  It also include ships that were returning/depositing from the previous turn.  There is a parameter on when we can start returning to base, for my final submission this was set to 950.  If its target cell has a harvest amount thats too much (go over 1000) it will just go towards home.  Depositing ships may harvest while going home, if the cell it steps on has enough halite, based on what value we set the parameter to.  I believe this is the only place where I used A* in determining the path.  Using it with the other movement didnt seem to have that much of an effect, from my testing at least.

## Harvest

Here ships stepping on a cell that has a certain halite, will harvest this turn.

## Attack

Here ships that are attacking with support, or just doing kamikaze will be determined.  A lot of these are again based on whatever value is set in the parameter.  It basically determines if a ship attack and potentially dies, could the support ship gain a certain percentage, if so do attack.  The kamikaze ship attacks even with no support.  This is to prevent enemy from harvesting a high halite cell. 

## Explore

Here the remaining ships are moved base on their target.

## Spawn

Here I determine if we are to spawn a ship or not.  If its safe to spawn, have enough halite, and there is still a certain number of turns left, then we spawn a ship.  I usually spawn ships until theres only 40% of the original overall halite left.  But for a 2 player games, it will keep spawning if my ships are below the enemy ships, unless there are only 25% turns left.  

# Regrets/Improvements
* Better workflow/Tools.  I didnt really use any debugging tools or made ones like the others.  I did make a replay parser so I can run my bot with my logs locally against the others, based on the online game. But I saw reCurs3 battlefront, and that was quite impressive.  Maybe I should've at least used flourine by Fohristiwhirl too.  Improving the workflow and getting to debug your code better is definitely a big advantage.
* Better algorithm in determining dock locations.  I only determine the dock locations in the beginning of the game.  I was thinking to do this per turn, so its more accurate and game state dependant.  I was able to optimize calculating the averages of each cell, but didnt get a chance to use it much.
* Better 4 player games.  I notice that most of the time I have the most collisions in a 4 player game, causing me to have the least ships.  
* Better attack algorithm.  I notice top players have other ships 'blocking' the enemy so that other ships can harvest the high halite cell. This seems very effective against most players.  Also, some players have an algorithm that surround an enemy, basically cornering it before it collides to it.  This is very efficient, because it prevents the 'chasing' movement that can be very costly.
