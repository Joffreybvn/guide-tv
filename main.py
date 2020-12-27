
from apscheduler.schedulers.blocking import BlockingScheduler
from b2sdk.v1 import InMemoryAccountInfo, B2Api
from pytz import timezone
from os import environ
import subprocess

# Initialize apscheduler and setup the timezone.
scheduler = BlockingScheduler()
tz = timezone('Europe/Brussels')

# Initialize BackBlaze B2 API
info = InMemoryAccountInfo()
api = B2Api(info)

# Load the environment variables
B2_ID = environ.get('B2_ID')
B2_KEY = environ.get('B2_KEY')
B2_BUCKET = environ.get('B2_BUCKET')


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


if __name__ == '__main__':

    # Schedule a grab every day @ 1h50
    @scheduler.scheduled_job('cron', day_of_week="mon-sun", hour=1, minute=30, timezone=tz)
    def update_guide():

        print("[!] Guide retrieval Started")
        grab_guide()
        upload_guide()

    # Run a grab on script start
    update_guide()
