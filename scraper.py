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
   discount_until = room_commercial_conditions['discountUntil']
   min_stay_date = room_commercial_conditions['minStayDate']
   discounted_price = room_commercial_conditions['discountedPrice']
   available_from = room_availability['availableFrom']
   #
   telegram_message = f"{roomName}\nPrice: {discounted_price}€\nUntil: {discount_until[:-15]}\nAvailable from: {available_from[:-15]}\nMin staying: {min_stay_date[:-15]}"
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
