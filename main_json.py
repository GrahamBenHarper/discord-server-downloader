import argparse
import os

import discord
import json

intents = discord.Intents().default()
intents.messages = True
bot = discord.Client(intents=intents)

# create a JSON message object which stores the message contents
def save_message(message, channel_name):
    msg = {}
    msg['author'] = message.author.name
    msg['date'] = str(message.created_at)
    msg['content'] = message.clean_content
    msg['channel'] = channel_name

    # check interactions
    if message.interaction != None:
        msg['interaction'] = {'name' : message.interaction.name, 'user' : message.interaction.user.name}
    else:
        msg['interaction'] = None

    # check attachments
    if message.attachments != []:
        msg['attachments'] = []
        for att in message.attachments:
            msg['attachments'].append({"filename" : att.filename, "url" : att.url, "proxy_url" : att.proxy_url})
    else:
        msg['attachments'] = None
    
    # check embeds
    if message.embeds != []:
        msg['embeds'] = []
        for emb in message.embeds:
            msg['embeds'].append({"title" : emb.title, "description" : emb.description})
    else:
        msg['embeds'] = None
    
    # check reactions
    if message.reactions != []:
        msg['reactions'] = []
        for i, react in enumerate(message.reactions):
            msg['reactions'].append({})
            msg['reactions'][i]['count'] = react.count
            # grab the people who reacted
            # (this doesn't work because it needs async because it requires a new fetch to read emoji reactions...)
            #msg['reactions'][i]['authors'] = []
            #async for react_author in react.users():
            #    msg['reactions'][i]['authors'].append(react_author.name)
            # grab the emoji that was used (can be string or emoji type)
            if isinstance(react.emoji,str):
                msg['reactions'][i]['emoji'] = react.emoji
            elif isinstance(react.emoji, discord.Emoji) or isinstance(react.emoji, discord.PartialEmoji):
                msg['reactions'][i]['emoji'] = react.emoji.name
            # this shouldn't happen?
            else:
                error("Woof")
    else:
        msg['reactions'] = None

    return msg

# save all channels of a guild given by string guild_id
async def save_guild_messages(guild_id):
    guild = bot.get_guild(int(guild_id))
    msgs = []

    # define an async to save to each channel's file, calling save_message
    async def save(channel):
        j = []
        if len(msgs) == 0:
            return
        try:
            os.mkdir(str(guild_id))
        except OSError:
            pass
        for message in msgs:
            j.append(save_message(message, channel))
        f = open('{}/{}.json'.format(guild_id, channel), encoding='utf-8', mode='a')
        print(j)
        json.dump(j, f, sort_keys=True, indent=2, ensure_ascii=False)
        f.close()

    # loop over guild channels and save a name, channel dictionary
    chn = {}
    for x in guild.channels:
        if not isinstance(x, discord.TextChannel): # TODO: voice channels still have text
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
                async for a in z.history(limit=None): # TODO: this seems like it triggers rate-limits now?
                    msgs.append(a)
            except discord.errors.Forbidden:
                print('Failed {} {}'.format(name, z.id))
        msgs.sort(key=lambda q: q.created_at)
        print('Formatting {}...'.format(name))
        await save(name)
        print('{} done!'.format(name))

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
