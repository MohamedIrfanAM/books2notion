import schedule
import books2notion
import time

schedule.every(60).minutes.do(books2notion.main,mode="append")
schedule.every().day.at("00:00").do(books2notion.main,mode="sync-full")

while True:
    schedule.run_pending()
    time.sleep(60)
