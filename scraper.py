import aiohttp
import asyncio
import requests
import os
import time

API_URL = os.environ['API_URL']
HOST = os.environ['HOST']

HEADERS = {"Accept":"*/*",
           "Accept-Encoding":"gzip, deflate, br",
           "Accept-Language":"it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
           "Connection":"keep-alive",
           "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
           "Host":HOST,
           "Referer":HOST,
           "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0"}

TOKEN = os.environ['TOKEN']
CHAT_ID = os.environ['CHAT_ID']
TL_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

async def scrape():
   async with aiohttp.ClientSession() as session:
      response = await session.get(url=API_URL, headers=HEADERS)
      json_output = await response.json()
      await lookForIn(json_output)

async def lookForIn(json):
   roomInfo = json['result']['pageContext']['room']
   room_commercial_conditions = roomInfo['commercialConditions']
   room_availability = roomInfo['availability']
   #
   roomName = roomInfo['name']
   discount_until = room_commercial_conditions['discountUntil'][:-15]
   min_stay_date = room_commercial_conditions['minStayDate'][:-15]
   discounted_price = room_commercial_conditions['discountedPrice']
   available_from = room_availability['availableFrom'][:-15]
   #
   if available_from == "2024-08-01":
      telegram_message = f"The room is still available. Price at {discounted_price}€ until {discount_until}\n---\nMinimum staying date: {min_stay_date}"
   else:
      telegram_message = f"The room has been booked :'("
   print(telegram_message)
   sendMessageToBot(telegram_message)

def sendMessageToBot(message):
   start_time = time.time()
   try:
      requests.post(TL_URL, json={'chat_id': CHAT_ID, 'text': message})
      time_diff = time.time() - start_time
      print(f'Telegram sending time: %.3f seconds.' % time_diff)
   except Exception as e:
      print(e)

async def main():
   start_time = time.time()
   tasks = []
   a_task = asyncio.create_task(scrape())
   tasks.append(a_task)
   await asyncio.gather(*tasks)
   time_diff = time.time() - start_time
   print(f'Global time: %.3f seconds.' % time_diff)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
