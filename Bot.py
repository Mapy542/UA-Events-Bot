import os
import json
import urllib3
import random
import tinydb
import re


def ParseEvents(client, Path):
    """Parse events from the discord server and write them to a json file.

    Args:
        client (discord.Client): The discord client object.
        Path (str): The path to the json file to write the events to.
    """
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
            or "must attend" in event.description.lower()
            or "must be present" in event.description.lower()
            or "must be there" in event.description.lower()
            or "expect you to be" in event.description.lower()
            or "expect you there" in event.description.lower()
            or "expect you at" in event.description.lower()
            or "expect you present" in event.description.lower()
            or "expect to see you" in event.description.lower()
            or "expect to see everyone" in event.description.lower()
            or "expect to see all" in event.description.lower()
            or "sub-team" in event.name.lower()
            or "subteam" in event.name.lower()
            or "sub team" in event.name.lower()
            or "sub-team" in event.description.lower()
            or "subteam" in event.description.lower()
            or "sub team" in event.description.lower()
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

    EventsJson = sorted(EventsJson, key=lambda k: k["event_date"])

    try:
        with open(Path, "w") as f:
            f.write(json.dumps(EventsJson))
            f.close()

    except Exception as e:
        print("Error writing to file", e)


def ParseContactMessages(client, CONTACTFORM, COUCHAUTH, database):
    """Parse messages from the contact form and write them to the database as well as return any new messages.

    Args:
        client (Discord.Client): The discord client object.
        CONTACTFORM (NONE?): _description_
        COUCHAUTH (str): authentication for the couch db.
        database (tinydb.TinyDB): The database object to write the messages to.

    Returns:
        list: A list of messages to send to the discord channel.
    """
    try:
        alreadySent = database.table("contact_form").all()

        couchHeaders = urllib3.make_headers(basic_auth=COUCHAUTH)
        http = urllib3.request(
            method="GET",
            url="http://leboeuflasing.ddns.net:5984/contact/_all_docs",
            headers=couchHeaders,
        )

        allDocs = json.loads(http.data.decode("utf-8"))

        allDocs = [x for x in allDocs["rows"] if x["id"] not in [x["_id"] for x in alreadySent]]

        messagesToSend = []
        for doc in allDocs:
            http = urllib3.request(
                method="GET",
                url=f"http://leboeuflasing.ddns.net:5984/contact/{doc['id']}",
                headers=couchHeaders,
            )
            docData = json.loads(http.data.decode("utf-8"))
            # await message.channel.send(
            #    f"New message from {docData['name']} at {docData['email']}:\n{docData['message']}"
            #

            database.table("contact_form").insert(docData)

            pattern = r"(?i)(unsubscribe)(?-i)"  # match word unsubscribe in any case
            if not re.search(
                pattern, docData["message"]
            ):  # if the message does not contain the word unsubscribe post it
                messagesToSend.append(
                    f"New message from {docData['name']} at {docData['email']}:\n{docData['message']}"
                )

        return messagesToSend
    except Exception as e:
        return [
            "Error parsing messages from contact form. Exception: "
            + e.__str__
            + "Please check the couchdb."
        ]


database = tinydb.TinyDB(
    path=os.path.join(
        os.path.join(os.path.realpath(os.path.dirname(__file__)), ".."), "messagesDB.json"
    ),
    storage=tinydb.storages.JSONStorage,
)

try:
    import discord
except ImportError:
    os.system("python3 -m pip3 install discord")
    print("Installed discord")

try:  # pull oauth token from file and other constants data
    with open(
        os.path.join(os.path.join(os.path.realpath(os.path.dirname(__file__)), ".."), "Creds.txt"),
        "r",
    ) as f:
        data = f.read().splitlines()
        TOKEN = data[0].split("=")[1].strip()
        GUILD = data[1].split("=")[1]
        PATH = data[2].split("=")[1]
        CONTACTFORM = data[3].split("=")[1]
        COUCHAUTH = data[4].split("=")[1]

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

    if (
        ".help" in message.content
        or ".commands" in message.content
        or "/help" in message.content
        or "/commands" in message.content
    ):
        await message.channel.send(
            """ Use .reloadEvents to sync events from the server to the website.\n
            Use .reloadMessages to sync messages from the contact form to the website."""
        )

    if ".reloadEvents" in message.content:
        ParseEvents(client, PATH)
        await message.channel.send("Events reloaded.")

    if random.random() > 0.05:  # 5% chance of running to rate limit...
        ParseEvents(client, PATH)

    if random.random() > 0.2:  # 20% chance of running to rate limit...
        # poll couch db for new messages
        toSend = ParseContactMessages(client, CONTACTFORM, COUCHAUTH, database)
        allChannels = client.guilds[0].channels
        newMessageChannel = [x for x in allChannels if x.name == CONTACTFORM][0]
        for messageToSend in toSend:
            await newMessageChannel.send(messageToSend)

    if ".reloadMessages" in message.content:
        toSend = ParseContactMessages(client, CONTACTFORM, COUCHAUTH, database)
        allChannels = client.guilds[0].channels
        newMessageChannel = [x for x in allChannels if x.name == CONTACTFORM][0]
        for messageToSend in toSend:
            await newMessageChannel.send(messageToSend)


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
