# Deck Operations

    GET /get_deck/<deck_id>

## Description
Retrieves the contents of a deck
***

## Requires authentication
Session 
***

## Parameters


## Return format
A json object with the deck of the form
- **creator** the creator of the deck
- **name** the name of the deck
- **desc** the deck's description

***

## Errors

   HTTP 400 - Session was invalid or the provided filename was invalid
   
***

## Example
**Request**	
   http://flashyapp.com/api/deck/get_deck/1

**Return**
``` json
{
  "cards": [
    {
      "sideB": "Card one contents", 
      "sideA": "Card one contents"
    }, 
    {
      "sideB": "Card two contents", 
      "sideA": "Card two contents"
    }
  ], 
  "creator": "Creator", 
  "name": "Flash Card Deck", 
  "desc": "A sample Description"
}
```
