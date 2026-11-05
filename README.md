# Installing Dependencies
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


# Test Execution
```sh
python -m pytest ./test/* --cov
```