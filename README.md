## Twitch FTL Score Tracker

Uses Twitch Websocket wrapper by CubieDev.

Will track score guesses by users in chat, namely any amount of digits at the start of a message.
The guesses will be stored temporarily alongside the user who made the guess.

A user of Moderator+ status can then issue a `!score` command followed by the correct score to identify the user who guessed the closest.

The guesses are then removed entirely, making space for a new guessing chain.