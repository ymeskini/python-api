# Setup

## Initialize local environment
```bash
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
pip install --upgrade pip
```

## Start the app
```bash
uvicorn main:app --reload
```


## Install a new package
```bash
pip install <package>
pip freeze > requirements.txt
```