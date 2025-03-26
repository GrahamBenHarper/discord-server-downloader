import argparse
import os

import discord

intents = discord.Intents().default()
intents.messages = True
bot = discord.Client(intents=intents)

# write a message object message to a file object file
# log format is currently:
#   AUTHOR @ TIME
#   AUTHOR: MESSAGE
# (additionally, for attachments)
#       'filename': FILENAME
#       'url': URL
#       'proxy_url': PROXY_URL
# (additionally, for embeds)
#       'title': TITLE
#       'description': DESCRIPTION
def save_message(message, file):
    # first write an AUTHOR @ TIME line
    file.write('{} @ {}'.format(message.author, message.created_at))
    if message.interaction != None:
        file.write(' interaction "{}" by {}'.format(message.interaction.name, message.interaction.user))
    file.write('\n')

    # then write content
    for x in message.clean_content.split('\n'):
        file.write('{}: {}\n'.format(message.author, x))

    # then write attachment info
    for x in message.attachments:
        file.write("""\
    'filename': {filename}
    'url': {url}
    'proxy_url': {proxy_url}
""".format(filename=x.filename, url=x.url, proxy_url=x.proxy_url))

    # then write embed info
    for x in message.embeds:
        file.write("""\
    'title': {title}
    'description': {description}
""".format(title=x.title, description=x.description))
    file.write('\n')

# save all channels of a guild given by string guild_id
async def save_guild_messages(guild_id):
    guild = bot.get_guild(int(guild_id))
    msgs = []

    # define an async to save to each channel's file, calling save_message
    async def save(channel):
        if len(msgs) == 0:
            return
        try:
            os.mkdir(str(guild_id))
        except OSError:
            pass
        with open('{}/{}.txt'.format(guild_id, channel), encoding='utf-8', mode='a') as file:
            for message in msgs:
                save_message(message, file)

    # loop over guild channels and save a name, channel dictionary
    chn = {}
    for x in guild.channels:
        if not isinstance(x, discord.TextChannel):
            continue
        if x.name not in chn:
            chn[x.name] = []
        chn[x.name].append(x)
        print("Got channel '{}'".format(x.name))

    # call the save(channel) for each channel now
    for name, channels in chn.items():
        msgs = []
        print('Saving {}...'.format(name))
        for z in channels:
            try:
                async for a in z.history(limit=None):
                    msgs.append(a)
            except discord.errors.Forbidden:
                print('Failed {} {}'.format(name, z.id))
        msgs.sort(key=lambda q: q.created_at)
        await save(name)

# save all emojis into the "emojis" subfolder for the guild
async def save_guild_emojis(guild_id):
    guild = bot.get_guild(int(guild_id))

    emojis = guild.emojis
    if len(emojis) == 0:
        return

    print(f"Got {len(emojis)} emojis!")

    try:
        os.mkdir(str(guild_id)+"/emojis")
    except OSError:
        pass

    for emoji in emojis:
        # since emoji.format is not available
        extension = emoji.url.split(".")[-1]
        await emoji.save('{}/emojis/{}.{}'.format(guild_id, emoji.name, extension))

# save all stickers into the "stickers" subfolder for the guild
async def save_guild_stickers(guild_id):
    guild = bot.get_guild(int(guild_id))

    stickers = guild.stickers
    if len(stickers) == 0:
        return

    print(f"Got {len(stickers)} stickers!")

    try:
        os.mkdir(str(guild_id)+"/stickers")
    except OSError:
        pass

    for sticker in stickers:
        # sticker.format is available, but do it this way instead
        extension = sticker.url.split(".")[-1]
        await sticker.save('{}/stickers/{}.{}'.format(guild_id, sticker.name, extension))

# save all soundboard entries into the "soundboard" subfolder for the guild
async def save_guild_soundboard(guild_id):
    guild = bot.get_guild(int(guild_id))

    soundboard = guild.soundboard_sounds
    if len(soundboard) == 0:
        return

    print(f"Got {len(soundboard)} sounds!")

    try:
        os.mkdir(str(guild_id)+"/soundboard")
    except OSError:
        pass

    for sound in soundboard:
        # sound.format is not available, so we save without an extension
        await sound.save('{}/soundboard/{}'.format(guild_id,sound.name))

@bot.event
async def on_ready():
    print('Saving {}...'.format(GUILD_ID))

    print("Saving messages...")
    await save_guild_messages(GUILD_ID)
    print("Saving emojis...")
    await save_guild_emojis(GUILD_ID)
    print("Saving stickers...")
    await save_guild_stickers(GUILD_ID)
    print("Saving soundboard...")
    await save_guild_soundboard(GUILD_ID)

    print('Done saving...')


# the main routine: load the discord key from a .env file, which must contain the following as lines somewhere:
# DISCORD_KEY="YOUR_KEY_HERE"
# SERVER_ID="SERVER_ID_HERE"
def main():
    # the guild id to pull all logs from
    global GUILD_ID

    # yes, I could use dotenv here, but it was incompatible with my setup
    # get DISCORD_KEY and SERVER_ID from file to prevent accidentally leaking credentials
    f = open(".env","r")
    lines = f.readlines()
    for line in lines:
        if "DISCORD_KEY" in line:
            bot_token = line.split("\"")[1]

        if "SERVER_ID" in line:
            GUILD_ID = line.split("\"")[1]
    f.close()

    # run the main routine
    bot.run(bot_token)


if __name__ == '__main__':
    main()
