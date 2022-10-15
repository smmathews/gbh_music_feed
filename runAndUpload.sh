python3 -m pip install -r requirements.txt
python3 jazz_feed.py
python3 in_concert_feed.py
python3 bso_feed.py
aws s3 sync ./feeds/ s3://gbh-feed/ --profile gbhfeed