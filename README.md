# Home task 11 (Flask Blog RESTfull App. Used SQLAlchemy, Marshmallow, JWT auth)

## 1: Initial Setup

#### Clone project in a new directory:
```bash
cd path/to/a/new/directory
git clone https://github.com/MaksNech/pylab2018_ht_11_restfull.git
```

## 2: Getting Started

#### Start backend:
Inside project create virtual environment:
```bash
virtualenv -p python3 env
```
Then start virtual environment:
```bash
source env/bin/activate
```
Install packages using pip according to the requirements.txt file:
```bash
pip install -r requirements.txt
```
Inside project directory run app with terminal commands:
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

## 3: API
##### Admin login info: username = admin, password = 123
##### If you want to change Admin login info: open 'app.py', change values in the line 91: "create_admin_first_time('admin', '123')". 
##### Main notes: 

##### 'methods' - method of HTTP request; 
##### 'param' - parameter; 
##### 'body' - body of request, example of JSON data; 
##### '@token_required' - decorator: needed login procedure through '/login' route and setting new generated token to 'x-access-token' header.
### Routes:

##### 1. Get all users:
##### methods = 'GET';
##### @token_required;
```bash
/user
```

##### 2. Get one user by 'public_id' field:
##### methods = 'GET';
##### @token_required;
##### param: 'public_id';
```bash
/user/<public_id>
```

##### 3. Create new user:
##### methods = 'POST';
##### @token_required;
##### body = {"username":"admin","password":"123"}
```bash
/user
```

##### 4. Set admins rights to the user by 'public_id' field:
##### methods = 'PUT';
##### @token_required;
##### param: 'public_id';
```bash
/user/<public_id>
```

##### 5. Delete the user by 'public_id' field:
##### methods = 'DELETE';
##### @token_required;
##### param: 'public_id';
```bash
/user/<public_id>
```

##### 6. Login:
##### Authorization type: Basic Auth
##### methods = 'GET';
```bash
/login
```

##### 7. Get all posts:
##### methods = 'GET';
```bash
/post
```

##### 8. Get all own posts:
##### methods = 'GET';
##### @token_required;
```bash
/post/own
```

##### 9. Get one post by 'post_id' field:
##### methods = 'GET';
##### @token_required;
##### param: 'post_id';
```bash
/post/<post_id>
```

##### 10. Create new post:
##### methods = 'POST';
##### @token_required;
##### body = {"title":"First Post Title","body":"Post body info"}

```bash
/post
```

##### 11. Change the post by 'post_id' field:
##### methods = 'PUT';
##### @token_required;
##### param: 'post_id';
##### body = {"title":"First Post Title Changed","body":"Post body info Changed"}

```bash
/user/<post_id>
```

##### 12. Delete the post by 'post_id' field:
##### methods = 'DELETE';
##### @token_required;
##### param: 'post_id';
```bash
/user/<post_id>
```

## 3: DataBase

#### If DataBase ('db.sqlite' file) is deleted then you should to create a new database with next commands:
Start virtual environment:
```bash
source env/bin/activate
```
Start python3 shell:
```bash
python3
```
In python3 shell enter next:
```bash
from app import db
```
```bash
db.create_all()
```
Exit from python3 shell:
```bash
exit()
```
Then you could open your db with:
```bash
sqlite3 db.sqlite
```
To show tables in db:
```bash
.tables
```
There should be: 'post' and 'user'.
   


