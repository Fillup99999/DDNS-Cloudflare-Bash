# import modules
from dotenv import load_dotenv
from os import getenv
import asyncio
import dns.resolver
import urllib.request
from cloudflare import Cloudflare
from telegram import Bot

# load .env
load_dotenv()
# .env variables
dns_record = getenv("dns_record")
zoneid = getenv("zoneid")
cloudflare_zone_api_token = getenv("cloudflare_api_token")
telegram_chat_id = getenv("telegram_chat_id")
telegram_bot_API_Token = getenv("telegram_bot_API_Token")

# Cloudflare Update
def cloudflare_dns(token,new_ip,a_record,zone):
    client = Cloudflare(api_token=token)
    list_zone = client.dns.records.list(zone_id=zone)
    record_id = ""
    for record in list_zone:
        if record.name == a_record:
            print("UPDATING IP FROM: "+record.content+" TO "+new_ip)
            record_id = record.id
    client.dns.records.edit(dns_record_id=record_id,zone_id=zone,name=a_record,type="A",content=new_ip)
    list_zone = client.dns.records.list(zone_id=zone)
    for record in list_zone:
        if record.name == a_record:
            print("IP CHANGED: "+record.content)

# Send Message to Telegram
async def bot_send_message(chat_id,message,apitoken):
    bot = Bot(token=apitoken)
    await bot.send_message(chat_id,message)
# Send Photo to Telegram
#photo = open("download.jpeg","rb")
#async def bot_send_photo(chat_id,photo,apitoken):
#    bot = Bot(token=apitoken)
#    await bot.send_photo(chat_id,photo)
#asyncio.run(bot_send_photo(telegram_chat_id,photo,telegram_bot_API_Token))


def main():
    # dns request for fqdn, hold ip in a variable.
    for rdata in dns.resolver.resolve(dns_record, "A"):
        dig_ip = rdata.address

    # curl wan ip
    with urllib.request.urlopen("https://api.ipify.org") as response:
        public_ip = response.read().decode()
    
    # message console
    message = f"The domain ip was {dig_ip} & the current ip is {public_ip}, so I just updated it for you :3"

    # if they don't match, update the cloudflare dns record
    if public_ip != dig_ip:
        print("They aren't equal! Oh NOOOOOOOO!!!!!!!!")
        # Update the Cloudflare DNS with the new IP
        cloudflare_dns(cloudflare_zone_api_token,public_ip,dns_record,zoneid)
        asyncio.run(bot_send_message(telegram_chat_id,message,telegram_bot_API_Token))
    else:
        print("Everything looks good to me.")    
    
main()
