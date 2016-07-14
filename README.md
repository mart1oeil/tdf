INSTALL
=======

sudo apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
python tdf.py 8080
