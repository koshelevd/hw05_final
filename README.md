# "Yatube" project.
Social network for publishing personal diaries.

A service where the user can create profile. In the author's profile
all records and personal data are available.
Users are able to go to other people's pages, subscribe to authors and 
comment on their posts.
The author can choose a name and a unique address for his page.

Django templates, post pagination and caching are used.
User registration with data verification, password change and recovery via 
mail.
Tests have been written to check the operation of the service.

## Installing on a local machine 

This project requires python3.8 and sqlite.

- Install requirements:
  ```
  $ python -m venv venv
  $ source ./venv/scripts/activate
  ```
  ```
  $ python manage.py migrate
  $ python manage.py collectstatic
  $ python manage.py createsuperuser
  ```
- Testing:
  ```
  $ pytest
  ```
- Development server:
  ```
  $ python manage.py runserver
  ```
