# Watchtower example

A proof of concept using **watchtower** as an analytics backend.

## Usage

### Installing

* Clone this repository
* Use `pyenv` for a python 3.7 environment, with the following commands:

```shell
pyenv install 3.7.x
pyenv virtualenv 3.7.x wtex
pyenv local wtex
```

* Install the requirements

`pip install -r requirements/base.txt`

* Create an `.env` file pointing to the flask entrypoint

```
FLASK_APP=wtex.application
FLASK_DEBUG=1
```

* Run flask on port `5001` so we can run `watchtower` on `5000`

`flask run --port 5001`
