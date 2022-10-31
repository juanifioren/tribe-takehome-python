# tribe-takehome-python

`tribe-takehome-python` is a django app that collects [HackerNews](https://news.ycombinator.com/) 
items using the [HackerNews API](https://github.com/HackerNews/API) and serves them via a simple
REST API.

The objective of the project is to implement the missing methods so that:
- Unit tests pass
- There are no flake8/black errors
- POST-ing to `/hackernews/load` fetches new items from the HackerNews API
- Going to `/hackernews/items` returns a JSON list of HackerNews items
- Going to `/hackernews/users` returns a JSON list of aggregated stats about HackerNews users

After all tests in `python manage.py test` pass, please zip this project back up and email it back to us! 


## Build Setup

The project requires a python3 environment set up, with dependencies specified in
`requirements.txt` installed.  While there are multiple ways of doing so, we recommend 
installing [pyenv](https://github.com/pyenv/pyenv#installation) and
[pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) to manage
your python environment. 

Note: if you have an existing pyenv installation, you may need to update it to to a 
new version in order to get python 3.9.5.  If so, you may need to update your shell
profile file to call `eval "$(pyenv init --path)"` instead of `eval "$(pyenv init -)"`

Then run the following commands to set up the project: 

```
# install and set up a python 3.9.5 virtual environment using pyenv/virtualenv
# (other python versions may work as well, depending on language features in use)
$ pyenv install 3.9.5
$ pyenv virtualenv 3.9.5 takehome
$ pyenv local takehome
$ pip install -r requirements.txt

# Set up the sqlite database
$ python manage.py migrate
```

Once set up, some useful commands:
```
# Run the app at localhost:8000/hackernews 
$ python manage.py runserver

# While the app is running, trigger a load of hackernews items (from another terminal)
$ curl http://localhost:8000/hackernews/load -d '{"type": "top", "limit": 10}' -H "Content-Type: application/json"

# While the app is running, get a page of hackernews items from the db (from another terminal)
$ curl http://localhost:8000/hackernews/items

# How to run all tests
$ python manage.py test
```


## Project Instructions

- Implement the `load_items_from_hackernews` function in [load.py](hackernews/load.py). This function
  will allow clients to load data from the [HackerNews API](https://github.com/HackerNews/API) into the 
  sqlite database.
  - Only HackerNews `Item`s should be stored in the database.

- Implement the functions in [views.py](hackernews/views.py). These functions will allow clients
  to retrieve information stored in the sqlite database.
  - Stored `Item`s can be retrieved by id, or listed in bulk.
  - Information about stored `Item`s, aggregated by username can be retrieved.
  - Endpoints returning lists should support simple pagination where the client can control
    the maximum size of the returned list, and iterate through all pages of data.
  
- Ensure all tests pass (`python manage.py test`):
  - [test_load.py](hackernews/tests/test_load.py)
  - [test_views.py](hackernews/tests/test_views.py)

- Run `black` and `flake8` and fix any reported errors:
```
$ black .
$ flake8 .
```
