import os
import json


def ParseEvents(client, Path):
    events = client.guilds[0].scheduled_events

    EventsJson = []

    for event in events:
        required = "0"
        if (
            "required attendance" in event.description.lower()
            or "attendance required" in event.description.lower()
            or "attendance is mandatory" in event.description.lower()
            or "mandatory attendance" in event.description.lower()
            or "required" in event.description.lower()
            or "mandatory" in event.description.lower()
        ):
            required = "1"

        try:
            coverImgURL = event.cover_image.url
        except:
            coverImgURL = ""

        EventsJson.append(
            {
                "event_name": event.name,
                "event_description": event.description,
                "event_date": event.start_time.timestamp(),
                "event_location": event.location,
                "event_required": required,
                "event_image_url": coverImgURL,
            }
        )

    try:
        with open(Path, "w") as f:
            f.write(json.dumps(EventsJson))
            f.close()

    except Exception as e:
        print("Error writing to file", e)


try:
    import discord
except ImportError:
    os.system("python3 -m pip3 install discord")
    print("Installed discord")

try:  # pull oauth token from file and other constants data
    with open("Creds.txt", "r") as f:
        data = f.read().splitlines()
        TOKEN = data[0].split("=")[1].strip()
        GUILD = data[1].split("=")[1]
        PATH = data[2].split("=")[1]

        print(TOKEN)
        f.close()
except Exception as e:
    print("Error reading file", e)

# initiate discord bot
client = discord.Client(intents=discord.Intents.all())


@client.event  # on ready post to console
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    ParseEvents(client, PATH)


@client.event  # on message
async def on_message(message):  # ignore self
    if message.author == client.user:
        return

    if ".help" in message.content:
        await message.channel.send(
            " Use .reloadEvents to sync events from the server to the website.\n"
        )

    if ".reloadEvents" in message.content:
        ParseEvents(client, PATH)
        await message.channel.send("Events reloaded.")


@client.event
async def on_scheduled_event_create(event):
    ParseEvents(client, PATH)


@client.event
async def on_scheduled_event_delete(event):
    ParseEvents(client, PATH)


@client.event
async def on_scheduled_event_update():
    ParseEvents(client, PATH)


client.run(TOKEN)
