### Scal
Scal is a friendly scam alert app that checks for scam texts, messages, and emails through a friendly chameleon pal named Scal. If you think a message is a scam or aren't sure about something, ask Scal! Scal acts as your personal scam detector and can become your friend or families with the family circle feature! As of right now, it is in its prototype stage, so Scal is only able to look at what messages you give it, but hopefully it'll be able to look at messages by itself in later updates.

### How to Use Scal
Simply download/copy the repository, create your own .env file with your choice of AI model API Key, and edit out whatever model you want in analyzer.py to run the app! For this version, I am using Gemini's 3.8 Flash, but you are free to switch out for any model you want. Just remember to change the API key in the .env file to match it with the model you are using.

###Check
In the "check" tab, users are able to paste into text bar whatever message, text, or email they want to check. From there 2 types of checks will occur: quick-scan and thorough-scan
Quick-Scan:
- Uses python logic and rules
- Is meant to give quick feedback as the thorough scan runs and formulates a response
Thorough-Scan:
- Uses AI to check the message/text
- Will determine whether it is safe, suspicious, or a scam.

After the thorough-scan is complete, a response from Scal will return whether or not the message is a scam, suspicious, or safe, with full guidelines on why it was a scam or suspicious, and what to do after.
From there, users are able to notify their family through the family circle feature. If users have a hard time trying to read the text, there is an option to read to them the guidelines. This was implemented to make the    app more senior friendly, as I know they have hard times trying to either listen or read.

As for the treats, they are there to act as a placeholder for the future development where the treats act like reinforcement learning, where for every time that Scal identifies a correct scam, the user is able to give it a treat to reward it, and as more treats build up, Scal learns more and more to identify sneakier scams and do it without necessary approval of the user, if of course, the user permits it.

###Family
In the "My Family" tab, users are able to create their own circles or join them through a 6-digit code that each family circle has and gets. From there, users within that same circle can notify each other whether they have found a scam. This will be a pretty big feature, especially once the app is able to look through emails and messages by itself for you.

