# Bang Backend
How to get started
## Development
Create a virtual env
```bash
python3 -m venv PATHTOENV
```
activate the new environment
```bash
souce PATHTOENV/bin/activate
```

now with the current directory in the backend folder install the dependencies
```bash
pip install -r requirements.txt
```

then you can start the python file `__init__.py`, I recommend you use *nodemon* for that, as it will automatically reload the server on new changes. If you don't already have it, you can install nodemon with
```
npm i -g nodemon
```
then you will be able to start the server with
```
nodemon __init__.py
```