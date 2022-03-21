import discord
from random import randint
from discord.ext import commands
from tabulate import tabulate
from csv import reader, writer


players = {}
stuff = {'player':  ":railway_car:",
         'empty':  ":white_large_square:",
         'enemy':  ":space_invader:", 'bullet': ":exclamation:"}
leaderboards = {}
if len(list(reader(open('leaderboard.csv', 'r')))) != 0:
    leaderboards = {r[0]: r[:2]+[int(r[2])] for r in list(
        reader(open('leaderboard.csv', 'r')))}


async def left(dictionary, inst_replace, inst_player, pos):
    """ Function to move player left """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]]).pop(pos[1]-1)
    (dictionary[pos[0]]).insert(pos[1]-1, inst_player)


async def right(dictionary, inst_replace, inst_player, pos):
    """ Function to move player right """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]]).pop(pos[1]+1)
    (dictionary[pos[0]]).insert(pos[1]+1, inst_player)


async def up(dictionary, inst_replace, inst_player, pos):
    """ Function to move bullet up """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]-1]).pop(pos[1])
    (dictionary[pos[0]-1]).insert(pos[1], inst_player)


async def down(dictionary, inst_replace, inst_player, pos):
    """ Function to move enemy down """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]+1]).pop(pos[1])
    (dictionary[pos[0]+1]).insert(pos[1], inst_player)


def spawn_enemy(x, room):
    """ Function to spawn enemy """

    room[1].pop(x)
    room[1].insert(x, stuff['enemy'])


def increase_score(user: discord.User):
    players[user.id]['score'] += 10
    score = players[user.id]['score']
    if str(user.id) in leaderboards:
        score += leaderboards[str(user.id)][2]
    leaderboards[str(user.id)] = [
        str(user.id), f'{user.name}#{user.discriminator}', score]
    players[user.id]['tscore'] = leaderboards[str(user.id)][2]


def update_leaderboard():
    lboards = sorted(leaderboards.values(),
                     key=lambda x: int(x[2]), reverse=True)
    with open('leaderboard.csv', 'w') as board:
        csvwriter = writer(board)
        csvwriter.writerows(lboards)


def shoot(room, playerPos):
    """ Function to shoot a bullet """

    (room[playerPos[0]-1]).pop(playerPos[1])
    (room[playerPos[0]-1]).insert(playerPos[1], stuff['bullet'])


async def gamemap(user, ctx):
    """ Function to update the game map """

    to_send = 'loading...'
    if user.id not in players:
        embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:",
                              description=to_send, color=discord.Color.purple())
        sent = await ctx.send(embed=embed)

        await sent.add_reaction("◀️")
        await sent.add_reaction("⬅️")
        await sent.add_reaction("🔴")
        await sent.add_reaction("➡️")
        await sent.add_reaction("▶️")

        room = {1: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                2: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                3: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                4: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                5: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                6: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                7: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                8: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
                9: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ]}

        for i in room:
            for ii in range(0, 10):
                room[i].pop(ii)
                room[i].insert(ii, stuff['empty'])

        room[9].pop(5)
        room[9].insert(5, stuff['player'])
        room[1].pop(5)
        room[1].insert(5, stuff['enemy'])

        players[user.id] = {
            'game': sent.id,
            'room': room,
            'score': 0,
            'tscore': 0,
            'playerPos': [],
            'enemy_poses': [],
            'bullet_poses': []
        }

        if str(user.id) in leaderboards:
            players[user.id]['tscore'] = leaderboards[str(user.id)][2]

    to_send = f"""
Use the arrows below to move around and :red_circle: to shoot.
You can also use ◀️ ▶️ to go left and right.
Player: **{user.display_name}**
Score: **{players[user.id]['tscore']:,}**"""

    players[user.id]['bullet_poses'].clear()
    players[user.id]['enemy_poses'].clear()

    if randint(0, 10) > 5:
        for i in range(randint(1, 3)):
            spawn_enemy(randint(0, 9), players[user.id]['room'])

    for i in range(1, 10):

        if stuff['enemy'] in players[user.id]['room'][i]:
            if i == 9:
                embed = discord.Embed(title="__**GAME OVER**__ :space_invader:",
                                      description=f"Your score: {players[user.id]['tscore']:,}", color=discord.Color.red())
                embed.set_footer(
                    text=f"Better luck next time! Use $play to play again.")

                # Edits the "Now playing" message to the "Game over" message
                message = await ctx.fetch_message(players[user.id]['game'])
                await message.edit(content=None, embed=embed)
                players.pop(user.id)
                update_leaderboard()
                return

            elif players[user.id]['room'][i+1][players[user.id]['room'][i].index(stuff['enemy'])] == stuff['bullet']:
                pos = players[user.id]['room'][i].index(stuff['enemy'])
                (players[user.id]['room'][i]).pop(pos)
                (players[user.id]['room'][i]).insert(pos, stuff['empty'])
                (players[user.id]['room'][i+1]).pop(pos)
                (players[user.id]['room'][i+1]).insert(pos, stuff['empty'])
                increase_score(user)

            else:
                players[user.id]['enemy_poses'].append(
                    [i, players[user.id]['room'][i].index(stuff['enemy'])])

        if stuff['bullet'] in players[user.id]['room'][i]:

            if i == 1:
                pos = players[user.id]['room'][1].index(stuff['bullet'])
                (players[user.id]['room'][1]).pop(pos)
                (players[user.id]['room'][1]).insert(pos, stuff['empty'])

            elif players[user.id]['room'][i-1][players[user.id]['room'][i].index(stuff['bullet'])] == stuff['enemy']:
                pos = players[user.id]['room'][i].index(stuff['bullet'])
                (players[user.id]['room'][i]).pop(pos)
                (players[user.id]['room'][i]).insert(pos, stuff['empty'])
                (players[user.id]['room'][i-1]).pop(pos)
                (players[user.id]['room'][i-1]).insert(pos, stuff['empty'])
                increase_score(user)

            else:
                players[user.id]['bullet_poses'].append(
                    [i, players[user.id]['room'][i].index(stuff['bullet'])])

    for pos in players[user.id]['enemy_poses']:
        if randint(0, 10) > 3:
            await down(players[user.id]['room'], stuff['empty'], stuff['enemy'], pos)

    for pos in players[user.id]['bullet_poses']:
        await up(players[user.id]['room'], stuff['empty'], stuff['bullet'], pos)

    for i in range(1, len(players[user.id]['room'])+1):
        to_send += '\n' + "".join(players[user.id]['room'][i])

    embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:",
                          description=to_send, color=discord.Color.purple())
    message = await ctx.fetch_message(players[user.id]['game'])
    await message.edit(embed=embed)


def player_pos(user):
    """ Function to update player position """

    for i in range(1, len(players[user]['room'])+1):
        if stuff['player'] in players[user]['room'][i]:
            x_axis = i
            y_axis = players[user]['room'][i].index(stuff['player'])
            del players[user]['playerPos'][:]
            players[user]['playerPos'].append(x_axis)
            players[user]['playerPos'].append(y_axis)


async def updater(user, ctx):
    await gamemap(user, ctx)
    player_pos(user.id)

# Add the server owner's id in owner_ids list. To get the id, right click the owner in discord and click copy id. There can be more than 1 owner_id added to the list.
bot = commands.Bot(
    command_prefix="$",
    description="SPACE INVADERS bot",
    case_insensitive=True,
    intents=discord.Intents.all(),
    owner_ids=[])  # Make sure to enable all intents in the developer portal.


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name} ({bot.user.id})")


@bot.command()
async def hello(ctx):
    """ A friendly hello from the bot! """

    if 'space-invaders' not in ctx.message.channel.name:
        return

    return await ctx.reply("Hi! I'm the Retro Bot. Use **$help** for a list of my commands!", mention_author=True)


@bot.command()
@commands.is_owner()
async def refresh(ctx: commands.Context):
    """ To refresh the leaderboards (owner only) """

    with open('leaderboard.csv', 'r') as board:
        listcsv = list(reader(board))
        listcsv = list(map(lambda x: [listcsv.index(x)+1]+x[1:], listcsv))
        if len(listcsv) > 10:
            listcsv = listcsv[:10]
        embed = discord.Embed(title=":space_invader: __**OLD LEADERBOARDS**__ :space_invader:",
                              description=f"```{tabulate(listcsv, headers=['Rank','Username','Score'])}```",
                              colour=discord.Colour.gold())
        await ctx.message.author.send(embed=embed)

    leaderboards.clear()
    with open('leaderboard.csv', 'w') as board:
        board.truncate()
        board.close()


@bot.command(aliases=['leaderboard', 'leaderboards', 'lboards'])
async def lboard(ctx):
    """ Shows you the current leaderboard """

    with open('leaderboard.csv', 'r') as board:
        listcsv = list(reader(board))
        listcsv = list(map(lambda x: [listcsv.index(x)+1]+x[1:], listcsv))
        if len(listcsv) > 10:
            listcsv = listcsv[:10]
        embed = discord.Embed(title=":space_invader: __**LEADERBOARDS**__ :space_invader:",
                              description=f"```{tabulate(listcsv, headers=['Rank','Username','Score'])}```",
                              colour=discord.Colour.gold())
        return await ctx.reply(embed=embed, mention_author=True)


@bot.command()
async def jump(ctx):
    """ Shows you the current playing game """

    if 'space-invaders' not in ctx.message.channel.name:
        return

    if ctx.message.author.id not in players:
        return await ctx.reply(f"You are not playing! Use **$play** to start playing.", mention_author=True)

    message = await ctx.fetch_message(players[ctx.message.author.id]['game'])
    return await message.reply(f"<@{ctx.message.author.id}>, here is your game!", mention_author=True)


@bot.command()
async def play(ctx):
    """ Starts a new game """

    if 'space-invaders' not in ctx.message.channel.name:
        return

    if ctx.message.author.id in players:
        message = await ctx.fetch_message(players[ctx.message.author.id]['game'])
        return await message.reply(f"<@{ctx.message.author.id}>, you are already playing!\nHere is the running game! Use **$stop** to stop playing.", mention_author=True)

    return await updater(ctx.message.author, ctx)


@bot.command()
async def stop(ctx):
    """ Stops the current playing game """

    if 'space-invaders' not in ctx.message.channel.name:
        return

    # If the user is not playing, then send a message.
    if ctx.message.author.id not in players:
        return await ctx.reply(f"You are not playing! Use **$play** to start playing.", mention_author=True)

    embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:",
                          description=f"Game stopped!\nYour Score: {players[ctx.message.author.id]['tscore']}", color=discord.Color.red())
    sent = await ctx.fetch_message(players[ctx.message.author.id]['game'])
    players.pop(ctx.message.author.id)
    update_leaderboard()
    return await sent.edit(embed=embed)


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user):

    if 'space-invaders' not in reaction.message.channel.name:
        return
    if user.bot:
        return

    emoji = reaction.emoji
    await reaction.remove(user)

    if user.id not in players:
        return

    if reaction.message.id != players[user.id]['game']:
        return

    if emoji == "⬅️":
        if players[user.id]['playerPos'][1]-1 != -1:
            await left(players[user.id]['room'], stuff['empty'], stuff['player'], players[user.id]['playerPos'])
            return await updater(user, reaction.message.channel)

    if emoji == "➡️":
        if players[user.id]['playerPos'][1]+1 != 10:
            await right(players[user.id]['room'], stuff['empty'], stuff['player'], players[user.id]['playerPos'])
            return await updater(user, reaction.message.channel)

    if emoji == "◀️":
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).pop(
            players[user.id]['playerPos'][1])
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).insert(
            players[user.id]['playerPos'][1], stuff['empty'])
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).pop(0)
        (players[user.id]['room'][players[user.id]
         ['playerPos'][0]]).insert(0, stuff['player'])
        return await updater(user, reaction.message.channel)

    if emoji == "▶️":
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).pop(
            players[user.id]['playerPos'][1])
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).insert(
            players[user.id]['playerPos'][1], stuff['empty'])
        (players[user.id]['room'][players[user.id]['playerPos'][0]]).pop(9)
        (players[user.id]['room'][players[user.id]
         ['playerPos'][0]]).insert(9, stuff['player'])
        return await updater(user, reaction.message.channel)

    if emoji == "🔴":
        shoot(players[user.id]['room'], players[user.id]['playerPos'])
        return await updater(user, reaction.message.channel)


bot.run("TOKEN", reconnect=True)
