# FisUFBA - Server

This repository contains the business logic and API behind FisUFBA.

## Getting Started

These instructions will guide you on how to deploy this application in
your local machine for development and testing purposes.<!-- See deployment-->
<!--for notes on how to deploy the project on a live system.-->

### Development Environment Setup

#### Prerequisites

- [PostgreSQL](https://www.postgresql.org/)
- [pipenv](https://docs.pipenv.org)
- [python3.7](https://www.python.org/downloads/release/python-370/)


#### Environment Setup

pipenv takes care of all python packages and dependencies of this
project. To configure its environment in development you must run:

```
$ pipenv install -d
```

To get inside the created pipenv environment, run:

```
$ pipenv shell
```

You'll also need to set `$PYTHONPATH` environment variable pointed to
the project's root:

```
$ export PYTHONPATH=/path/to/fisufba-server
```

Finally you'll have to configure the `env.ini` file. There's an example
in the project's root (`env.ini.example`), you can copy it. To do this,
you'll have to provide a Postgres database, an user (role) with
permissions over this database and its password.

After you complete the environment setup, you must create the database
tables by running:

```
$ python /path/to/fisufba-server/db/main.py
```

#### Running

You can start the application running:

```
$ python /path/to/fisufba-server/api/main.py
```

It will listen and send information through
[http://localhost:5000](http://localhost:5000).


### Deployment Environment Setup

For deployment purposes, you need Docker and PostgreSQL only. Make sure you have a `fisufba` table already created in PostgreSQL.

Configure `env.ini` as explained in the development section.

Build the container by using.

```
$ docker build -t fisufba-server .
```

Then create the database tables by running:

```
$ docker run --net=host fisufba-server python /app/db/main.py
```

Finally execute the actual web application:

```
$ docker run -d --name fisufba-server --rm -p 8000:8000 --net=host fisufba-server
```

To redeploy, execute the following:

```
$ docker container kill fisufba-server
$ docker build -t fisufba-server .
$ docker run -d --name fisufba-server --rm -p 8000:8000 --net=host fisufba-server
```

TODO remove `--net=host` and explain how to properly setup a network between the container and PSQL.

### Testing

```
TODO
```
