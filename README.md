# Checklist-django
This is a demo project to learn Django web app framework and create a [<strong>checkli.com</strong>](https://www.checkli.com/) style web app

Website: https://django-checklist.herokuapp.com/

## Features implemented
* upvote a post by a user
* show upvotes on posts
* Show upvotes count
* restrict user to upvote again
* View checklists w/o upvote functionality on logout
* Restrict user from upvoting own checklist - button disabled with upvotes as count shown
* Upvote retracted if user presses upvote again <br><br>

* Add/remove bookmarks functionality - bookmark is not public, so no need to display how many bookmarks for a certain checklist
* Show bookmarks page
* privacy setting in bookmarks - user B cannot see user A’s bookmarks
* User cannot upvote/bookmark own post by navigating through URL
* Remove bookmark option in my bookmarks page <br><br>

* Pagination
* Bookmark and upvote option in user checklist view
* Bookmark and upvote option in checklist detail view
* upvote option in show bookmarks screen
* Display upvoted checklists
* Show how many upvotes for each checklist in show upvoted lists screen
* Actual checklist editing options in text editor
* Dropdown navbar
* Search checklists by title, content <br><br>

* Assign topics to checklists
* Display topics assigned on all checklists
* Hyperlink topic to display checklists that have the same topic
* Search checklists by topic / Display categories for checklists <br><br>

* Google, Facebook login
* share checklist link on social media <br><br>

* DEPLOY <br><br>

* AWS lambda function to reduce profile picture size on upload
* Priority setting for checklist
* Change password from profile page
* Ability to save Drafts while creating checklists
* Disable display of draft checklists in all listviews
* Add navbar option to view drafts
* Post draft checklists —> PUSHED TO HEROKU AS WELL <br><br>

## Features in Pipeline
* Follow other users; show followed users checklists on top
* Access control for checklists; use of visibility model field
* Disable advanced options in checklist content field in create form
* Exception handling everywhere

## Features on Hold
* Don’t throw error if profile pic not found - NOT USEFUL for now - this ERROR does not happen when deployed on Heroku
* Save checklist pdf
* Read more in checklist text something like quora long answers
* Search checklists by text contained in items - feature NOT REQUIRED - not feasible when dataset becomes large
* Automated tests
* limit number of lambda function calls per month
* More comprehensive profile page for user
