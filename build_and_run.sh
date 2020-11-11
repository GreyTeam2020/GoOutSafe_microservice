#bin/bash bash

# Dev server

source venv/bin/activate
pip install -r requirements.txt
python setup.py develop
python app.py
## Production server
#flask run