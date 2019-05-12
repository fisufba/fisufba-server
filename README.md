# FisUFBA - Server

This repository contains the business logic and API behind FisUFBA.

## Getting Started

These instructions will guide you on how to deploy this application in
your local machine for development and testing purposes.<!-- See deployment-->
<!--for notes on how to deploy the project on a live system.-->

### Prerequisites

There're few prerequisites because all other python packages are handled
by pipenv.

- [PostgreSQL](https://www.postgresql.org/)
- [pipenv](https://docs.pipenv.org)
- [python3.7](https://www.python.org/downloads/release/python-370/)

### Setting the Environment

pipenv takes care of all python packages and dependencies of this
project. To configure its environment in development you must run:

```
$pipenv --install -d
```

To get inside the created pipenv environment, run:

```
$pipenv shell
```

You'll also need to set `$PYTHONPATH` environment variable pointed to
the project's root:

```
$export PYTHONPATH=/path/to/fisufba-server
```

Finally you'll have to configure the `env.ini` file. There's a example
in the project's root (`env.ini.example`), you can copy it. To do this,
you'll have to provide a Postgres database, an user (role) with
permissions over this database and its password.

### Running

You can start the application running:

```
$python /path/to/fisufba-server/api/main.py
```

It will listen and send information to
[http://localhost:5000](http://localhost:5000).

### Testing

```
TODO
```
