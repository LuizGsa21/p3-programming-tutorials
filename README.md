# p3-programming-tutorials
Project 3 programming tutorials


## Prerequisites:
 - Python
 - Vagrant
 - Web client IDs:
    - [Google](https://developers.google.com/identity/sign-in/web/devconsole-project)
    - [Facebook](https://developers.facebook.com/docs/facebook-login/login-flow-for-web/v2.4)
    - [Github](https://developer.github.com/v3/oauth/)

## Instructions:
```sh
# Clone this repo and navigate to project folder
$ git clone https://github.com/LuizGsa21/p3-programming-tutorials
$ cd p3-programming-tutorials/
```
Add your Web Client IDs to `app/config.py`. If you are having trouble, look for the comment `# ADD WEB CLIENT IDs HERE`. 
    
Also in the project root folder include `google-secret.json` file provided by the [tutorial](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount).

After adding your client IDs:
```sh
# start up vagrant
$ vagrant up
# Wait for installation to complete, then SSH into virtual machine
$ vagrant ssh
$ cd /vagrant/
$ python runserver.py
# done :)
```


## Project Files Overview:

`runserver.py` creates the application using `create_app` factory method in `app/app.py`.

`create_app` configures all the blueprints, extensions and database model.

Flask blueprints located in `app/views/`:
- `frontend.py`
- `user.py`
- `api.py`
- `oauth.py`

Database Models located in `app/models`:
- `article.py`
- `category.py`
- `comment.py`
- `user.py`

## OAuth Login implementation:
Python: `app/views/oauth.py`

JavaScript: `app/static/js/app/helpers/LoginManager.js`

## Non-OAuth login implementation:
Python: `app/views/frontend.py`

## Questions and Answers!
##### How do I edit/add/delete categories?
Try logging in as admin.

##### How do I edit/delete other users?
Try logging in as admin ;)

##### How do I login as admin?
- username: `admin`
- password: `password`

##### Why don't I see anything when I click on the tutorials dropdown?
Try adding a category.
