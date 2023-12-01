# Numan Python take-home assignment
This repository contains the Numan Python take-home exercise.
It is a small Django-based app that deals with blood tests.

There is a model called `BloodTestResults`, which represents a set of tests that the user
has ordered and which are supposed to be carried out by a lab.

There are three available endpoints at the moment.

- GET `api/results/`: Returns a list of blood tests for the current user (currently the only user in the database, as there's no authentication)
- GET `api/geolocation/`: Performs IP-based geolocation
- GET `api/lab/<country>/`: Returns a lab by city and country.

Please check the [instructions](/INSTRUCTIONS.md) for this technical challenge to see what are the expected deliverables.


## Running this thing
Running this thing is pretty easy. The difficulty level will depend on whether you have
Docker Compose, Poetry (the standard `pip` alternative these days), or neither installed
on your system.


### If you have Docker Compose:

If you are running the service for the first time, you'll first need to run the database migrations
and load the initial database entries, using:
```bash
$ docker-compose run --rm web /code/manage.py migrate
$ docker-compose run --rm web /code/manage.py loaddata initial_data.json
```

The start the service with:

```bash
$ docker-compose up
```

and then visit http://localhost:8000/ in your browser.

⚠️ You will have to add your IP Geolocation API Key to IP_GEOLOCATION_API_KEY environment variable to run docker correctly e.g.

```bash
$ export IP_GEOLOCATION_API_KEY=*KEY*
```

> ⚠️ If you get an error about permissions on PostgreSQL data not permitted, run this:
> ```
> $ sudo chown -R $(id -u):$(id -g) misc
> ```
> and run `docker-compose up` again.

To run a command in the Compose Django container, you can use the following command
line:

```bash
$ docker-compose run --rm web <your command>
```

### If you have Poetry:
Run:

```bash
$ poetry shell
$ poetry install --no-root
```

The first time you run this you'll first need to run the database migrations and load the initial
database entries, using:
```bash
$ ./manage.py migrate
$ ./manage.py loaddata initial_data.json
```

After the migrations have run, you need to start the server with:

```bash
$ ./manage.py runserver
```

and then visit http://localhost:8000/ in your browser.

⚠️ You will have to add your IP Geolocation API Key to IP_GEOLOCATION_API_KEY environment variable to run django correctly e.g.

```bash
$ export IP_GEOLOCATION_API_KEY=*KEY*
```


### If you have neither:
Install either [Docker Compose](https://docs.docker.com/compose/install/)
or [poetry](https://pypi.org/project/poetry/) and run the corresponding section.


## Database migrations
Every time the database schema changes, you need to create and apply the migrations.

With Docker Compose:

```bash
$ docker-compose run --rm web /code/manage.py makemigrations
$ docker-compose run --rm web /code/manage.py migrate
```

With Poetry:

```bash
$ poetry shell
$ ./manage.py makemigrations
$ ./manage.py migrate
```

## Admin console
You should then be able to log into the admin interface at http://localhost:8000/admin/
with the username `admin` and the password `admin`. This is a good place to look at the entries
of the database tables and create new ones.


## Brief rundown
The main bits of this app are in the `main` directory. The relevant files are
`models.py` (containing the models), `views.py` (the views), `urls.py` (the URL routes),
and `admin.py` (the admin models). `numan_python_takehome/settings.py` is also somewhat
important, as it contains various settings that are required to run the app.

You shouldn't have to change anything to run the app locally, it should all be ready out
of the box.

May the force be with you! 💪
