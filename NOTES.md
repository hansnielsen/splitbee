# Architecture
- Flow for a new bill:
  - One user enters amount of bill and short description (futher on down the road: picture?)
    - Description
    - Pre-tax amount
    - Sales tax %age (can later be guessed from geolocation)
  - App generates a new ID for the bill, displays + QR code on the screen
  - Each bill splitter enters the amount of each of their items
  - App calculates the total amount each user owes based on their components and the sales tax
  - Confirms with each bill splitter that the amount is OK with everyone (consensus)
  - Once consensus is reached, the app finds the user that has the most negative balance to
    all the other current bill-splitters, and tells them to pay.

- Total flow: enter, split, confirm, pay

# Detailed Architecture
- Creation:
  - New "Bill" object
    - Unique ID
    - Total amount
    - Sales tax
    - Tip?
    - State
  - Once each user signs up, have a "BillItem" object
    - User
    - Bill
    - Amount of item
  - UserConfirm - records that user x confirmed bill at time z (+ location?)

- A bill has states, ordered according to the lifecycle
  - Created     (created, not split yet)
  - Split       (users have started splitting the bill)
  - ***TODO***  (might need more here, to determine whether the bill split is finished?)
  - Confirmed   (all users have confirmed that the bill split is correct, ready to pay)
  - Paid        (splitting confirmed, paying confirmed)

- This should probably have an API, since if I'm ever going to take this anywhere, I'll need
  to write a mobile app, eventually


## API
----------
POST   /bills                 - creates a new bill
GET    /bills/ID              - gets info about a bill

POST   /bills/ID/items        - creates an item on the given bill
GET    /bills/ID/items        - gets all items from a given bill
DELETE /bills/ID/items/ITEM   - deletes an item from a bill

POST   /bills/ID/confirm      - confirms a bill for the current user

GET    /bills/ID/watch        - long-polling feed for bill events
    - item added
    - item removed
    - (on modification, emit removal and then adding)
    - item added after confirming (un-confirm bill)
    - bill is confirmed
    - bill is paid

GET    /bills/ID/qr           - get the QR code for the given bill


# Later Ideas
- View total eatery history
- Geolocation of current restaurant
- Intelligent time-of-day determining breakfast/lunch/dinner based on local time of user and
  the time of day (7-9, 11-3, 5-9)
- Take picture of bill, can save for later
- Total is zero-sum, so we can look for relationships among users and allow two users that
  have never met to determine what their relative balances are - also allowing them to go out
  for food, one pays, and have it 'credit' the other user.
