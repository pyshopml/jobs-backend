jobs-backend
===

How-to run local copy of project

Begin
---

Create directory for project's files:

    mkdir backend
    virtualenv -p python3 venv
    source venv/bin/activate


Git
---

Clone repo from github:

    git clone https://github.com/pyshopml/jobs-backend.git
    cd jobs-backend/
    git checkout develop

For local development we should create "static" folder, to serve static files locally by django dev server.
In production this role will be provided by Nginx:

    mkdir jobs_backend/static


Requirements
---

Install required python packages:

    pip install -r requirements/local.txt


Database
---

Install PostGIS extension for PostgreSQL (postgresql-x.x-postgis package on
Debian/Ubuntu).
Configure PostgreSQL to serve remote connections.
Make new user that will be owner of our database.
Create database named "**jobs_backend**" (by default),
or specify another name at ".env" by `DATABASE_URL` directive.
Enable PostGIS extension on database:

    $ psql <db name>
    > CREATE EXTENSION postgis;


Configuration
---

Copy "env.example" to "settings" folder:

    cp env.example config/settings/.env

Define minimal config parameters:

    DJANGO_SETTINGS_MODULE=config.settings.local

    DATABASE_URL=postgis:///my_fancy_dbname
    POSTGRES_USER=postgresuser
    POSTGRES_PASSWORD=mysecretpass

This is all what you need for start.


Database migrations
---

Apply migrations to create database structure:

    python manage.py migrate


Import django-cities data
---

Import data:

    python manage.py cities --import=country,region,subregion,city,alt_name


Run
---

Start Django development server:

    python manage.py runserver

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web-browser
