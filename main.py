import argparse
import os

import discord


bot = discord.Client()
GUILD_ID = None


def save_message(message, file):
    file.write('{} @ {}\n'.format(message.author, message.created_at))
    for x in message.clean_content.split('\n'):
        file.write('{}: {}\n'.format(message.author, x))
    for x in message.attachments:
        file.write("""\
    'filename': {filename}
    'url': {url}
    'proxy_url': {proxy_url}
""".format(filename=x.filename, url=x.url, proxy_url=x.proxy_url))
    for x in message.embeds:
        file.write("""\
    'title': {title}
    'description': {description}
""".format(title=x.title, description=x.description))
    file.write('\n')


async def save_guild(guild_id):
    guild = bot.get_guild(guild_id)
    msgs = []

    async def save(channel):
        if len(msgs) == 0:
            return
        try:
            os.mkdir(str(guild_id))
        except OSError:
            pass
        with open('{}/{}'.format(guild_id, channel), encoding='utf-8', mode='a') as file:
            for message in msgs:
                save_message(message, file)
    chn = {}
    for x in guild.channels:
        if not isinstance(x, discord.TextChannel):
            continue
        if x.name not in chn:
            chn[x.name] = []
        chn[x.name].append(x)
        print("Got channel '{}'".format(x.name))

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


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.invisible)
    print('Saving {}...'.format(GUILD_ID))

    await save_guild(GUILD_ID)

    print('Done saving...')


def main():
    global GUILD_ID
    parser = argparse.ArgumentParser(description='Discord Server Downloader')
    parser.add_argument('bot_token', help='The Discord bot token.')
    parser.add_argument('guild_id', type=int, help='The ID of the Discord guild.')
    args = parser.parse_args()
    bot_token = args.bot_token
    GUILD_ID = args.guild_id

    bot.run(bot_token)


if __name__ == '__main__':
    main()
