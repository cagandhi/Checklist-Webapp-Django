# Checklist-django
Implemented a checklist manager webapp by utilizing the Django REST framework to help users create, search, upvote and bookmark checklists, connect with other users and share lists on social media. The webapp is hosted on Heroku and uses AWS S3 for file storage and AWS Lambda to reduce profile image size upon upload. The project started with the idea to create a [<strong>checkli.com</strong>](https://www.checkli.com/) style web app.

Website: https://django-checklist.herokuapp.com/

## Features implemented
* Email-based authorization as well as Social media based authorization with ability to request password reset
* Perform CRUD operations on own checklists
* View checklists published by other user with no. of upvotes displayed for each list
* Upvote/Bookmark checklists published by other users and view these lists
* Search checklists by title and description
* Easily share checklists on social media such as Facebook, LinkedIn, Reddit, Twitter
* Save draft checklists and come back anytime to edit and publish them
* Follow other users and view their checklists
* Save and edit others' published checklists to make it your own!
* See your own published checklists
* Assign topics to checklists and view checklists by topics

## Features in Pipeline
* Recommendations for checklists below each checklist
* Automatically infer category from checklist title and description
* Follow a checklist and notify a user if a change is made by the author
* Notifications functionality - when a user follows you, checklist upvoted

## Usage Information
  > <strong>Note:</strong> The web-app is already hosted on Heroku for use by anyone so these steps are only required if you are cloning the project on local.

1. Clone the project.
2. Create a new virtual environment with: ```python3 -m venv <path_to_new_env>```
3. Activate the newly created virtualenv as: ```source <path_to_new_env>/bin/activate```
4. Run command: ```pip install -r requirements.txt```
5. To run the webapp on your local machine, execute the command: ```python manage.py runserver```
