import os
import json
import Auto_Update
import urllib3
import random
import tinydb


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


Auto_Update.UpdateSoftware()  # check for update and update if needed

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

    if ".help" in message.content:
        await message.channel.send(
            " Use .reloadEvents to sync events from the server to the website.\n"
        )

    if ".reloadEvents" in message.content:
        ParseEvents(client, PATH)
        await message.channel.send("Events reloaded.")

    if random.random() > 0.0:
        # poll couch db for new messages
        allChannels = client.guilds[0].channels
        newMessageChannel = [x for x in allChannels if x.name == CONTACTFORM][0]
        print(newMessageChannel)

        alreadySent = database.table("contact_form").all()

        couchHeaders = urllib3.make_headers(basic_auth=COUCHAUTH)
        http = urllib3.request(
            method="GET",
            url="http://leboeuflasing.ddns.net:5984/contact/_all_docs",
            headers=couchHeaders,
        )

        allDocs = json.loads(http.data.decode("utf-8"))

        print(allDocs)
        allDocs = [x for x in allDocs["rows"] if x["id"] not in [x["_id"] for x in alreadySent]]
        print(allDocs)

        for doc in allDocs:
            http = urllib3.request(
                method="GET",
                url=f"http://leboeuflasing.ddns.net:5984/contact/{doc['id']}",
                headers=couchHeaders,
            )
            docData = json.loads(http.data.decode("utf-8"))
            print("data " + str(docData))
            # await message.channel.send(
            #    f"New message from {docData['name']} at {docData['email']}:\n{docData['message']}"
            # )
            await newMessageChannel.send(
                f"New message from {docData['name']} at {docData['email']}:\n{docData['message']}"
            )

            database.table("contact_form").insert(docData)


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
