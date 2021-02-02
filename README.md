# Checklist Webapp in Django

[![Build Status](https://travis-ci.com/cagandhi/Checklist-Webapp-Django.svg?branch=master)](https://travis-ci.com/cagandhi/Checklist-Webapp-Django)
![GitHub](https://img.shields.io/github/license/cagandhi/Checklist-Webapp-Django)
<br>
![GitHub](https://img.shields.io/badge/language-python-blue.svg)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/cagandhi/Checklist-Webapp-Django)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/cagandhi/Checklist-Webapp-Django)

Implemented a checklist manager webapp by utilizing the Django REST framework to help users create, search, upvote and bookmark checklists, connect with other users and share lists on social media. The webapp is hosted on Heroku and uses AWS S3 for file storage and AWS Lambda to reduce profile image size upon upload. The project started with the idea to create a [<strong>checkli.com</strong>](https://www.checkli.com/) style web app.

Website: https://django-checklist.herokuapp.com/

## Primary Features of the web app
* Email as well as social media based authorization along with password reset functionality
* Perform CRUD operations on own checklists
* View other users' checklists with no of upvotes
* Upvote/Bookmark checklists by other users and view them
* Search checklists by title and description
* Share checklists on social media such as Facebook, LinkedIn, Reddit, Twitter
* Save draft checklists and come back anytime to edit and publish them
* Follow other users and be notified when they publish a new checklist
* Save and edit others' published checklists to make them your own!
* Assign topics to checklists and view checklists by topics

## Features in Pipeline
* Notifications functionality - when a user follows you, checklist upvoted
* Follow a checklist and notify a user if a change is made by the author
* Recommendations for checklists displayed below each list
* Automatically infer category from checklist title and description

  > <strong>Note:</strong> The web-app is already hosted on Heroku for use by anyone so these steps are only required if you are cloning the project on local.

## Installation
1. Clone the project.
2. Create a new virtual environment with: ```python3 -m venv <path_to_new_env>```
3. Activate the newly created virtualenv as: ```source <path_to_new_env>/bin/activate```
4. Run command: ```pip install -r requirements.txt```
5. To create database tables based on the migrations, run: `python manage.py migrate`
6. To load categories data into the categories table in database, run the command: `./manage.py shell < load_categories.py`

## Usage
1. To run the webapp on your local machine, execute the command: ```python manage.py runserver```
