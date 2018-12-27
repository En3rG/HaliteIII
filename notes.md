# Notes to consider


## TO DO FOR IMPROVEMENT
- AT END GAME, SOMETIMES IF EXPLORE DIRECTION IS BLOCKED, JUST SITS THERE ON 0 HALITE

- DONT HARVEST NEXT TO IT IF ITS LOW? OR SURROUNDED BY ENEMY
- CALL BACKUP WHEN HARVESTING NEXT TO ENEMY?
- IF LOSING AND HAS A LOT MORE SHIPS THAN ENEMY, ATTACK??

- BETTER TIMING FOR WHEN TO BUILD/SAVE
- BETTER TIMING FOR WHEN TO STOP SPAWNING
- BETTER TIMING WHEN TO STOP BUILDING DOCKS
- BETTER TIMING TO WHEN TO DEPOSIT (EVEN NOT FULL)
- BETTER ATTACK (TRAP HIGH CARGO ENEMY SHIPS)
- BETTER HARVEST (WHEN NEXT TO HIGH HALITE, MAY JUST SIT THERE)

- IMPROVE RETREAT? (AVOID HIGH HALITE?) (STILL HARVEST IF CLOSE TO DOCKS?)



## Machine Learning
* Training
* Predicting


## Initialization
* Maximize use of 30 secs initialization time
    * Determine rich areas
    * Determine best dock placement
    * Determine most efficient approach to rich areas (tunneling?)
        * Need to consider going back home (shipyard/dock)


## Movements
* Types of movements:
    * Harvesting
        * Immediate Movement (next neighbor)
        * Further goal when immediate movement is relatively low
        * When a lot of ships are together, one might move first to a spot where a ship exists, but that ship later cannot move anywhere (stuck) will cause collision!!!!
    * Inspired Harvesting
    * Returning
        * Ships that are full should have priority?
        * Currently still colliding when 3 returning to home, 1 going to shipyard, but 3 move first to 2s position, then 2 cannot move thus stays and collide with 3
        * Should harvest if cell has too much halite and can carry some more
    * Building (create dock)
    * Attacking (get enemy with high halite)
        * Attacker
        * Stealer
        * Backup
    * Spawn
        * Not use .occupied this checks if its occupied at current turn, but ship will spawn next turn
* Prevent collisions with ally
* Prevent collisions with enemy


## Gather Statistics
* Halite gained
* Halite burned
* Halite dropped
* Halite spent


## End game
* All ships must return to shipyard/docks to maximize halite harvested
    * Avoid collisions
    * Move ships closest to shipyard/docks first
        * Select cheapest cell to move to (not imlemented!!!!!!!!!!)
        * If no other ships taking its spot, can still mine instead of going home right away
        * If no other ships around or close by, and still very close to shipyard/dock, go harvest



# COSTS

* MAX HALITE CARRY = 1000
* SHIP = 1000
* DOCK = 4000
* HARVEST = 25%
* MULTIPLE HARVEST = 75% of previous harvest
* BONUS HARVEST = 200% (HALITE CELL STILL ONLY GET DEDUCTED 25% OF ITS ORIGINAL AMOUNT, EVEN THOUGH SHIP GETS 75%)
* INSPIRATION RADIUS = 4 (MUST BE 2 OR MORE ENEMY CLOSE BY)
* COST TO LEAVE = 10% (IF SHIP DOESNT HAVE ENOUGH, IT CANNOT MOVE!!!)
* COST TO LEAVE IS HARVESTING = 75% of previous cost





