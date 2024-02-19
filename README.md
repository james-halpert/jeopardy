# jeopardy
A jeopardy like game

Feb 18, 2024 Update
Question processing system rebuilt to use 41,193 Categories (20,959 Standard Jeopardy - 20,234 Double Jeopardy) bringing the total number of questions up to 205,965.
The processing tool is now included in the tools folder as well for future updates with JSON datasets.
If a category name has been used repeatedly, the tool will take the extra questions after the initial 5 and create a duplicate category with a -n variable in the category name and append the next 5 questions with sequential dollar values.
This can be accessed with the Sanitized_Questions.zip

UI Update to Player Input Screen
![image](https://github.com/james-halpert/jeopardy/assets/35898814/3509b14d-9331-43c6-8baf-f87546b8c577)

UI and Scoreboard updated for better visibility
![image](https://github.com/james-halpert/jeopardy/assets/35898814/12f510fc-8374-4b60-9e24-89bffdad2190)

After the question and answers are shown, the players specify who was the first to answer correctly (or "Wrong Answer - Next Question" if everyone missed it)
![image](https://github.com/james-halpert/jeopardy/assets/35898814/a1d0858f-d52f-4eee-ad76-cbc37d75542c)

Players can now start a new game with various options after finishing a round
![image](https://github.com/james-halpert/jeopardy/assets/35898814/9fba807c-03af-4ec4-84a4-34f6bcb1b413)


Feb 17, 2024 Update
jeopardy_audio.py released
This version features audio events such as announcing dollar amounts, winner announcement, incorrect response, etc.


Feb 16, 2024 Update
New version of jeopardy that allows for 1-4 players with names, photos and an interactive scoreboard.
Game over screen declaring a winner now appears at the end of the game.

Settings for the game may be accessed by pressing the back-tick ~ key
Scoreboard can be toggled with = key

I took the 200k jeopardy archive questions and removed all incomplete categories, organized (14,503) standard jeopardy and (13,413) double jeopardy questions.
The zip file contains txt files formatted for this game, containing 27,916 Categories and 139,580 questions and answers.

![image](https://github.com/james-halpert/jeopardy/assets/35898814/3716e242-20c3-4052-811d-290e90901f64)
![image](https://github.com/james-halpert/jeopardy/assets/35898814/69cec1f3-4df1-48b5-a95f-811c8b4b0846)

Award points manually by choosing who got the answer correct first:
![image](https://github.com/james-halpert/jeopardy/assets/35898814/69b51932-dff6-4559-aa7b-9303025bca3f)

Keep track of the scores with the new scoreboard feature:
![image](https://github.com/james-halpert/jeopardy/assets/35898814/565c71fb-5973-4027-8143-1e6cf1d1e20d)

![image](https://github.com/james-halpert/jeopardy/assets/35898814/d86e074f-6a1e-4dd8-918f-9bf1a76fb84d)
