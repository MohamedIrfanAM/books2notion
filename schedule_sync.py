import schedule
import books2notion
import time

schedule.every(60).minutes.do(books2notion.main)

while True:
    schedule.run_pending()
    time.sleep(60)
