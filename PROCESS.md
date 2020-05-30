# OSGA - Progress

This document is going to report progress on the implementation of project OSGA: One Site to Grieve them All.

## Progress (chronological order)

Date format: dd-mm-yyyy.

#### [11-05-2020]

Re-read DESIGN document with critical thinking on implementation of forms.
-> Add to favourite/add to blacklist menu in show settings in user panel: how does it work? Maybe some ideas [here](https://joshuajohnson.co.uk/Choices/?fbclid=IwAR0oEKzscrMGHUQ9iltrGW-7BevuBJre-tykSHfsLtBVB5n3re4R3xftRdI).

Should I go with a top-down approach and try to make everything modular from the beginning?
-> No, tried this with the Pizza project and didn't have enough knowledge -> Wasted a lot of time -> Going to implement the base of the project and only restructure if/when needed. Planning a strict control of code quality review every friday morning with refactor of what can be improved instead of adding new code that day. This should allow me to maintain the code a bit without spending too much time thinking about it beforehand while lacking knowledge.

[TODO] Questions without answers, to keep in mind:
- How should I deal with the scale regarding the amount of flowers/items on graves? (How can I make it look good whether 1, 100 or 10000 people click on a grave to add flowers)


#### [12-05-2020]

At what point should I start asking for assistants' help?
-> After I'm done with the basic things that I already know how to do (html pages / flask rendering), if wednesday evening I know that I will run into difficulties with the implementation of important or basic features

In prototype: I chose to simplify some parts of the interface.
Simplified things that will have to be changed for the first version of OSGA:
- Search bars (towards JS with choice suggestion)
- Images of graves etc.

Do I make a different page for logging-in or do I try to implement it so that the user (gets the impression that he/she) stays on the same page?
- Flask vs JS -> JS would be better, it fits better with my idea of making the website very quick and easy to use.


#### [13-05-2020]

Changing e-mail and password in user panel: is it better to make a pop-up, to validate one change at a time (password _or_ email _or_ profile preferences) or to make one button to validate it all at once?
- -> For now, one button for password, one button for e-mail, one button for profile preferences. Will see with usage if it would be better in a different way.

I keep using both words interchangeably but... Are a cemetary and a graveyard the same thing?
- -> According to the internet, a graveyard is connected to a church, so it's more relevant that I use the word "cemetary".

How will I deal with spam once users can subscribe and leave comments on graves?
- -> [TODO] CAPTCHA or checkbox "I'm not a robot" -> Will look at what is better, but implement it after the prototype anyway (it isn't part of the basic features and can easily be added in the interface)
- -> [TODO] In message moderation: IP ban? Should I save the IP address at which messages are posted like I did back in 2010? Or save the IP addresses users use? Is it still relevant nowadays (I think it's much more common to use a proxy or a VPN)? -> Will also look this up for after the prototype.

When should I start implementing security?
- -> As soon as I start implementing backend features. I will not wait for refactoring, I will directly add protection against injections for every form. So, as soon as I start programming features after the prototype is finished.

I realize I haven't specified this anywhere: how am I going to implement the "block user" feature? (In case of spam/illegal comment, for example)
- -> Just adding a boolean attribute "blocked" to the user table for now and changing this attribute to True if the button "block user" is pressed.
[TODO] Possible additional feature: a pop-up where the admin can write a reason why the user is blocked (which will be sent via email to the user) and select for how long the user will remained blocked.
Also, still in the admin panel: in my sketches I put a "delete" button, but I can better just "refuse" the comment: this way, it is not displayed, but it stays in the database and can still be viewed later, for example if I add a history of refused comments or to prove why a user has been banned.
Still in the admin panel: how do I deal with selecting the character to declare dead? -> select form or search form?
- -> Search/select for series just like other similar searches in OSGA
- -> For characters: only display the select form once the series has been choosen, and then only the characters within this series. -> This is something for Javascript.

Clicking on a grave to add a flower: how do I do this exactly? I only know it has to be done in JS. After further research, it seems AJAX is my solution to register the clicks and save how many flowers a grave has. Steps I'll need to take to implement this:
- Display of existing flowers: randomize position of flowers on grave so that they aren't all perfectly aligned -> Randomizing function within a specific area on the grave (-> how do I deal with screens of different dimensions? I guess I'll first implement it for my screen and test on other screens afterwards to see if I need to fix anything.)
- Click to add flower on grave: how do I create an element with JS? 
	- -> Oh, it seems it's really easy with a function like createElement()
- It would be amazing if I could make the flower "fall" on the grave by like 30px like on the Slate website -> how does this work?
	- -> Look at DOM animations on W3Schools
- For after the prototype: [TODO] Learn how to use AJAX
- [TODO] Use it to save 1 click in the database (doesn't need to be functional yet, I'm jist doing the prototype so far) -> But at least use pseudo code
	

#### [14-05-2020]

- Where do I put the link to the admin panel so that it's easily accessible to admins?
	- I can simply add a link in the drop menu in the navbar 
	- I can also put a link to "declaring character death" on the matchin cemetary pages


#### [15-05-2020]

- Which ones of the damn API packages/interfaces do I use?? Which doc should I read?? This is so confusing.
	- After trial and error (and frustration and help) I went for just the simple basic API, no specific Python package added, and I'm just doing simple requests.


#### [18-05-2020]

- Do I call the API in Python or in JS, for the list of series?
	- Pros Python: It's easy and clean: loading all the movies + passing in to the HTML page. + I already know how to do it -> time gain for me 
	- Pros JS (+ AJAX): I can dynamically call it for example only if the user has already typed 4 characters, to carry less data in the page
	- -> I'll first implement it in Python, it shouldn't take me long, and only if the page is slow to load I'll try a different solution.

- If I want to finish this project within 2 weeks, it can't be perfect. What do I "sacrifice"?
	- Things that aren't mandatory features: confirmation e-mail, user management by administrator...
	- Unnecessary JS (example: is_alnum() in Python to avoid code injections with username, it could be done in JS but would probably take me more time as I've never done it)
	- Graphics can be improved at the end, not everything needs to be super pretty in an alpha/beta version!

- Do I check the validity of the user's e-mail address? If so, how?
	- For now, I won't check it (not a basic feature of my app thus not a priority)
	- For later: regex? Python library specifically made for this (isn't it overkill?)? something else?


#### [19-05-2020]

- In order to protect Flask Admin, it's probably better that I use Flask Login (there is help available on forums and blogs to use a combination of both), but this could take precious time that I could use for other things... Should I still try to implement it while I've already spent a couple of hours implementing login/registration without it?
	- No, this isn't a mandatory feature. I'll add it in the future if I have no other solution AND if I want to publish OSGA for real.


#### [20-05-2020]

- Dynamic HTML in cemetaries: is it better to create the graves with a loop in jinja2 or in Javascript?
	- Pros jinja: template is easier to visualize in HTML file -> less risk for mistakes
	- Pros JS: more possibilities to dynamically modify the HTML elements 
	- -> Will first do it in jinja to reduce risk of mistakes / unnecessary waste of time. It shouldn't take too long to switch to JS if needed afterwards anyway.


#### [21-05-2020]

- I originally decided that an advantage for users with an account would be to be able to leave more flowers than users without an account... But:
	- It makes the website a lot less nice for newcomers who would be excited about being to pay tribute to all their favourite characters but would face mandatory registration after only a couple of flowers left
	- It's not fun to implement and others, more important, nicer features could be implemented with this time
	- -> So I will drop this "feature" and all users will be able to leave as many flowers as they want. Having an account will only be necessary to post messages, so that those messages can be moderated.


#### [22-05-2020]

- Adding shows/dead characters: there is no API of deceased characters in movies, so in any case, characters will have to be declared dead manually by admins. The current system makes the admin able to declare one character dead at a time, which is fine for maintainance, but this can't be a good solution for initialization of the database (way too many entries to add). I see two different (non exclusive) solutions to this problem:
	1. Writing all the data in a csv file (quick to fill in with a spreadsheet software) and importing it to the database via a python script;
	2. In a page in the admin panel, display all the characters from a show with checkboxes, so that the admin can select many characters at the same time and declare them all dead simultaneously.
	- -> Solution 1. is really something I would like to implement on the long term if I keep OSGA going, and it's probably not complicated (that kind of thing took me a couple of hours in all the other languages I tried to do it for the first time, it's not much), but if for some reason I don't manage to do it (or to make it injection-proof or so) as fast this time I could be wasting time unnecessarily...
	- -> Solution 2. would probably still take more time than a .csv import for the admin, but at least, it's easy to secure and I know that it won't take me more than 30 to 60 minutes to implement as it's just some form and API request. I will probably add this when I have time before the deadline.


#### [25-05-2020]

- How am I going to organize this week's work on OSGA?
	- Monday: fixing of the bugs discovered during presentation of alpha version
	- Mon/Tue/Wed: adding of last features: suggestions interface, admin authentification, improvement of the search function and of the emailing system, maybe adding pagination and some buttons to improve navigation
	- Thursday: improve display in cemetary: graves design, what if there are more than 10 flowers, etc. Prepare the db adding a couple of shows with their deceased characters, for display.
	- Friday: screencast, refactor of a couple of things if needed (helpers.py, general modularity), comments/docstrings.


#### [26-05-2020]

- Do I really need Flask admin? I currently use it a lot because I'm implementing the app and I need to check that data is properly inserted into the database, but once the app is finished, there isn't really any reason to use it if I implement things properly in my self-made admin_panel: all the features will be in there. So I can stop spending time looking for how to add authentification with basic auth, and just remove flask admin once I'm done implementing the app.


#### [27-05-2020]

- Today I will try to make it possible for users to leave more flowers without them being displayed outside of the grave. I can see several possible implementations, but I find it difficult to decide which one is the best:
	- Solution that means saving each flower as an entry in the database: each user click, its coordinate and the selected flower are registered in the database. When a cemetary loads, all the flowers are added as HTML elements where the user placed them. This would probably be very heavy for the database and slow to load (so many elements per cemetary)!
	- The same, but lighter on the database: coordinates aren't registered, and flowers are added randomly when the DOM is loaded. This is lighter on the database, but would probably make loading the page even slower...
	- Even lighter: the amount of click per grave is saved, but only the last N flowers are saved (N will be the max number of flowers to add on a grave before it becomes aesthetically irrelevant or absurd to add more - for example when the grave is so full that adding more won't look any different). If N is 50, even if 5000 users click on the grave, that will make a huge difference for the database. 
	- The lightest: no flowers are registered in the database. Only N flowers max are displayed on the grave, randomly, when the page loads. This is easy to implement and fast to work, but it's not as nice for users who won't be able to see the flowers they have left after refreshing.

	After writing this, I think I will go for the third point: it has both the advantages to display the last flowers registered where the visitors placed them, and is probably not too heavy for the database nor the page loading.


#### [28-05-2020]

- What features do I still want to add in the time I have before the deadline for beta version?
	- Improvement of grave design / aesthetic of the website in general
	- Finish implementing search text field with drop-down menu
	- If possible, display the flowers where the user clicks
	- Import csv files to put characters in db so that it has at least characters from 3-4 shows for display/screencast

- After struggling for days on the search/dropdown thing, is it a good idea to try something else or should I continue?
	- Try to google for other solutions


#### [29-05-2020]

- I still have a little bit of time, I have to choose between:
	- improving the database structure (maybe risky time wise, but would hugely improve loading of the pages, which at the moment is too slow)
	- improving the rest of the navigation (adding buttons/texts to make browsing the website more user-friendly)
	- -> I think I will spend one hour trying to improve the database, and after that (Saturday) polish all the pages HTML to improve browsing experience and screencast. Sunday will be for code-cleaning (and sleep).

## Author

Charlotte "Milocéane" is a CS student from France and the Netherlands, currently studying at the University of Amsterdam.
This application was made as "end project" for the Web Apps part of the minor "Fulltime Programmeren".