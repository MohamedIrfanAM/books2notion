import schedule
import books2notion
import time
import os

schedule.every(60).minutes.do(books2notion.main)

if "API_TOKEN" in os.environ:
    while True:
        schedule.run_pending()
        time.sleep(60)
else:
    books2notion.main()
