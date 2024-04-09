Discord Bot for University of Akron's RMC Robotics Club.
It synchronizes the Discord server's events information into a json file that can be displayed on a website.

## Events

The bot parses discord server events and stores them in a json file. The json file is then used to display the events on the website.
It also parses whether the event is mandatory or not.

## Contact Form

The bot also polls a contact form database and sends the information to the club's discord to act as a notification system.
It keeps a log of which messages have been sent to the discord server to prevent duplicates.

## Version

### 2.0.1

- Added more event context detection

### 2.0.0

- Removed broken auto-update feature in favor of using Repo-Update-Dispatcher

  - See Mapy542/Repo-Update-Dispatcher for more information

- Added more message and command options

### 1.4.0

- Add another mandatory event trigger condition

### 1.3.0

- Fix credentials file path issue

### 1.2.0

- Sort Events by Date

### 1.1.0

- Added Readme file
- Fixed Path issue

### 1.0.0

- Added Auto-Update feature
