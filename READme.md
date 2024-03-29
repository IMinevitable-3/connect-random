# Connect Random

### Connect random people with a click of the button

## Installation

clone the repo and `cd` into root folder.Following all dependencies need different terminals.

**setting up rabbit and redis**

```sh
docker compose build
docker compose up
```

**setting up server**

make sure to use [virtual environment](https://www.geeksforgeeks.org/python-virtual-environment/) for python and activate before continuing .

```sh
cd server
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

**setting up pairing server**

```sh
cd pairing_server && python3 pairing_server.py
```

**setting up celery worker**

```sh
 celery -A server worker --queues=paired_queue --loglevel=info
```

### [End points](https://zerobin.org/?fe70058332018577#57kFsSgmuRJBv51iN8ohCpkLB6LcXT3aGR9YiRy8qkkd)
