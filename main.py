
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from b2sdk.v1 import InMemoryAccountInfo, B2Api
from functools import partial
from threading import Thread
from pytz import timezone
from flask import Flask
from os import environ
import subprocess

# Initialize the dummy API
app = Flask(__name__)

# Initialize apscheduler and setup the timezone.
scheduler = AsyncIOScheduler()
tz = timezone('Europe/Brussels')

# Initialize BackBlaze B2 API
info = InMemoryAccountInfo()
api = B2Api(info)

# Load the environment variables
B2_ID = environ.get('B2_ID')
B2_KEY = environ.get('B2_KEY')
B2_BUCKET = environ.get('B2_BUCKET')
PORT = int(environ.get("PORT", 3000))


def grab_guide():
    """
    Execute the tv_grab_fr_telerama via command line to grab
    all tv guide and save them into a "all.xml" file.
    """

    subprocess.run(["./assets/tv_grab_fr_telerama", "--quiet", "--days", "3", "--output", "all.xml"])
    print("[+] Guide retrieval completed")


def upload_guide():
    """Upload the "all.xml" file to BackBlaze B2"""

    # Login to BackBlaze
    api.authorize_account("production", B2_ID, B2_KEY)
    bucket = api.get_bucket_by_name(B2_BUCKET)

    # Upload the "all.xml" file, which contain the tv guide
    bucket.upload_local_file(local_file="all.xml", file_name="all.xml")
    print("[+] Guide upload completed")


# Schedule a grab every day @ 1h50
@scheduler.scheduled_job('cron', day_of_week="mon-sun", hour=1, minute=30, timezone=tz)
def update_guide():

    print("[!] Guide retrieval Started")
    grab_guide()
    upload_guide()


# Create a "Hello World" route on root
@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':

    # Start the dummy API
    partial_run = partial(app.run, host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
    Thread(target=partial_run).start()

    # Init the scheduler
    scheduler.start()

    # Run a grab on script start
    update_guide()
