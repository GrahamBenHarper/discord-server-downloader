# Discord Server Downloader 
Small script to download all the messages in a Discord Server.

## Installation
Install the prerequisites (currently just `discord`):
```
$ pip3 install -r requirements.txt
```

## Usage
To use this script, create a `.env` text file in the same folder as `main.py`,
and set the following variables in the file with this same formatting
```
DISCORD_KEY="YOUR_KEY_HERE"
SERVER_ID="SERVER_ID_HERE"
```
Once you've set your credentials in a `.env` file, simply run the script via
```
python3 main.py
```
