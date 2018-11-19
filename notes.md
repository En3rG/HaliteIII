# Notes to consider


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
    * Inspired Harvesting
    * Returning
        * Ships that are full should have priority?
        * Currently still colliding when 3 returning to home, 1 going to shipyard, but 3 move first to 2s position, then 2 cannot move thus stays and collide with 3
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

###### ------------------------------------- DATA STRUCTURE

MoveShips
    - Moves
        - Data
            -Matrices


###### ------------------------------------- SCENARIOS

[
 [ 90  99  41 125 122 175 107  98 106  93 291  68  35  47 104 103 103 104  47  35  68 291  93 106  98 107 175 122 125  41  99  90]
 [ 76 216  90  96  68 256  98 182 177 172 121  92  73  95  67  54  54  67  95  73  92 121 172 177 182  98 256  68  96  90 216  76]
 [107 129 150  68  78 199 163 251 524 293 164 120 239 133  42  48  48  42 133 239 120 164 293 524 251 163 199  78  68 150 129 107]
 [133  58 102  71  87 204 214 226 257 337 193 131 290 292  49  47  47  49 292 290 131 193 337 257 226 214 204  87  71 102  58 133]
 [ 22  74 186 189  68 248 177 268 454 224 171 179 254 131  64  38  38  64 131 254 179 171 224 454 268 177 248  68 189 186  74  22]
 [ 44 150 283 118 164 179 132 239 258 244 182 232 218 116  98  67  67  98 116 218 232 182 244 258 239 132 179 164 118 283 150  44]
 [ 57  98 136  77  54 188 157 372 208 429 325 204 283 168 103 149 149 103 168 283 204 325 429 208 372 157 188  54  77 136  98  57]
 [250 134 157 131  58 300 259 546 316 569 227 233 157 126 131 185 185 131 126 157 233 227 569 316 546 259 300  58 131 157 134 250]
 [278 288 534 184  63 346 403 504 702 467 285 182 191 132 108 302 302 108 132 191 182 285 467 702 504 403 346  63 184 534 288 278]
 [219 216 219 338 121 419 624 503 450 336 266 277 182 182 115 262 262 115 182 182 277 266 336 450 503 624 419 121 338 219 216 219]
 [477 426 318 347  75 219 660 623 432 407 490 228 244 135 117 343 343 117 135 244 228 490 407 432 623 660 219  75 347 318 426 477]
 [480 505 281 140 109 363 284 417 747 383 339 240 138 163 348 259 259 348 163 138 240 339 383 747 417 284 363 109 140 281 505 480]
 [522 255 220 190 132 183 241 497 964 391 266 279 126 171 396 313 313 396 171 126 279 266 391 964 497 241 183 132 190 220 255 522]
 [348 317 210 322 177 169 280 392 686 435 294 397 163 169 350 445 445 350 169 163 397 294 435 686 392 280 169 177 322 210 317 348]
 [144 221 275 200 114 188 255 514 684 449 465 570 267 181 161 193 193 161 181 267 570 465 449 684 514 255 188 114 200 275 221 144]
 [190 361 309 201 160 335 249 396 560 432 331 335 285 342 184 188 188 184 342 285 335 331 432 560 396 249 335 160 201 309 361 190]
 [288 404 152 250 266 226 294 620  -3 664 301 350 612 293 286 442 442 286 293 612 350 301 664  -6 620 294 226 266 250 152 404 288]
 [189 180 129 297 178 329 335 555 352 554 433 265 277 306 234 338 338 234 306 277 265 433 554 352 555 335 329 178 297 129 180 189]
 [210 119  92 248 179 295 396 205 165 195 303 256 183 131 146 212 212 146 131 183 256 303 195 165 205 396 295 179 248  92 119 210]
 [160 193 172 127 150 146 300 337 128 155 174 122 173 138 132 194 194 132 138 173 122 174 155 128 337 300 146 150 127 172 193 160]
 [157 152 205 296 274 130  85  71  44 115 141  82 101 185 189  95  95 189 185 101  82 141 115  44  71  85 130 274 296 205 152 157]
 [ 67 218  86 175 123 270  60  46 104  42  44  48 100 135 151  83  83 151 135 100  48  44  42 104  46  60 270 123 175  86 218  67]
 [ 14 138  96  89  65 139  74  80  13  60  17  42  82  88 257  83  83 257  88  82  42  17  60  13  80  74 139  65  89  96 138  14]
 [ 95  78  50 109  91  64  81  50  12   8  47  11  82 114  55  48  48  55 114  82  11  47   8  12  50  81  64  91 109  50  78  95]
 [  1  18 106  76 242 115  28  63   1   3  12  27   1   5  35  27  27  35   5   1  27  12   3   1  63  28 115 242  76 106  18   1]
 [ 30  79  99  68 108 176  31  38  97  17  42  14  17  36  37  11  11  37  36  17  14  42  17  97  38  31 176 108  68  99  79  30]
 [  4  27  48  63  87 198  44 134 198  46  33  35 168  73 159  21  21 159  73 168  35  33  46 198 134  44 198  87  63  48  27   4]
 [ 89  40 105 142 220 115  68  70 220 180 144  50  50 214 181  31  31 181 214  50  50 144 180 220  70  68 115 220 142 105  40  89]
 [ 19 177 435 248 627 327  84  86 177  79 126 190  82  93 262  73  73 262  93  82 190 126  79 177  86  84 327 627 248 435 177  19]
 [ 44 157 126 136 276 341  91 161 147 125  72 200 197  76  98 104 104  98  76 197 200  72 125 147 161  91 341 276 136 126 157  44]
 [202  66  57 104  84  90 163  74  64  48  67  72 283 127 168  87  87 168 127 283  72  67  48  64  74 163  90  84 104  57  66 202]
 [148  72  60 227 124  82  83 113  99 129 154  69  82  62 131 158 158 131  62  82  69 154 129  99 113  83  82 124 227  60  72 148]]
