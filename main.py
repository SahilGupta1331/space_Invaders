import random
import discord

from discord.ext import commands


playing: bool = False
sent = None
player = None
enemy_poses = []
bullet_poses = []
playerPos = []
score = 0

room = {1: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        2: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        3: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        4: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        5: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        6: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        7: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        8: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],
        9: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ]}

stuff = {'player':  ":railway_car:",
         'empty':  ":white_large_square:",
         'enemy':  ":space_invader:", 'bullet': ":exclamation:"}

for i in room:
    for ii in range(0, 10):
        room[i].pop(ii)
        room[i].insert(ii, stuff['empty'])
        
room[9].pop(5)
room[9].insert(5, stuff['player'])

# Game functions

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
    """ Function to move player up """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]-1]).pop(pos[1])
    (dictionary[pos[0]-1]).insert(pos[1], inst_player)

async def down(dictionary, inst_replace, inst_player, pos):
    """ Function to move player down """

    (dictionary[pos[0]]).pop(pos[1])
    (dictionary[pos[0]]).insert(pos[1], inst_replace)
    (dictionary[pos[0]+1]).pop(pos[1])
    (dictionary[pos[0]+1]).insert(pos[1], inst_player)

def spawn_enemy(x):
    """ Function to spawn enemy """

    room[1].pop(x)
    room[1].insert(x, stuff['enemy'])

def shoot():
    """ Function to shoot a bullet """

    (room[playerPos[0]-1]).pop(playerPos[1])
    (room[playerPos[0]-1]).insert(playerPos[1], stuff['bullet'])

async def gamemap(message: discord.Message):
    global to_send
    global playing
    global sent
    global enemy_move
    global player
    global enemy_poses
    global bullet_poses
    global score
    enemy_move = False
    to_send = f"""
Use the arrows below to move around and :red_circle: to shoot.
You can also use ◀️ ▶️ to go left and right.
Score: **{score:,}**"""

    if random.randint(0, 10) > 5:
        for i in range(random.randint(1, 3)):
            spawn_enemy(random.randint(0, 9))

    for i in range(1, len(room)+1):
        if stuff['enemy'] in room[i]:
            if i == 9:
                embed = discord.Embed(title="__**GAME OVER**__ :space_invader:", description=f"Your score: {score:,}", color=discord.Color.orange())
                embed.set_footer(text=f"Better luck next time! Use $play to play again.")

                await sent.edit(content=None, embed=embed) # Edits the "Now playing" message to the "Game over" message
                playing = False

                sent = discord.Message
                enemy_poses.clear()
                bullet_poses.clear()
                return

            elif room[i+1][room[i].index(stuff['enemy'])] == stuff['bullet']:
                pos = room[i].index(stuff['enemy'])
                (room[i]).pop(pos)
                (room[i]).insert(pos, stuff['empty'])
                (room[i+1]).pop(pos)
                (room[i+1]).insert(pos, stuff['empty'])
                score += 10

            else:
                enemy_poses.append([i, room[i].index(stuff['enemy'])])

        if stuff['bullet'] in room[i]:
            if i == 1:
                pos = room[1].index(stuff['bullet'])
                (room[1]).pop(pos)
                (room[1]).insert(pos, stuff['empty'])

            elif room[i-1][room[i].index(stuff['bullet'])] == stuff['enemy']:
                pos = room[i].index(stuff['bullet'])
                (room[i]).pop(pos)
                (room[i]).insert(pos, stuff['empty'])
                (room[i-1]).pop(pos)
                (room[i-1]).insert(pos, stuff['empty'])
                score += 10

            else:
                bullet_poses.append([i, room[i].index(stuff['bullet'])])

    for pos in enemy_poses:
        if random.randint(0, 10) > 3:
            await down(room, stuff['empty'], stuff['enemy'], pos)

    for pos in bullet_poses:
        await up(room, stuff['empty'], stuff['bullet'], pos)

    bullet_poses.clear()
    enemy_poses.clear()

    for i in range(1, len(room)+1):
        to_send += '\n' + "".join(room[i])

    if not playing:
        embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:", description=to_send, color=discord.Color.purple())
        sent = await message.channel.send(embed=embed)

        await sent.add_reaction("◀️")
        await sent.add_reaction("⬅️")
        await sent.add_reaction("🔴")
        await sent.add_reaction("➡️")
        await sent.add_reaction("▶️")

        player = message.author
        playing = True

    else:
        embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:", description=to_send, color=discord.Color.purple())
        await sent.edit(embed=embed)

def player_pos():
    for i in range(1, len(room)+1):
        if stuff['player'] in room[i]:
            x_axis = i
            y_axis = room[i].index(stuff['player'])
            global playerPos
            del playerPos[:]
            playerPos.append(x_axis)
            playerPos.append(y_axis)

async def updater(message: discord.Message):
    await gamemap(message)
    player_pos()




bot = commands.Bot(
    command_prefix="$",
    description="SPACE INVADERS :space_invader bot",
    case_insensitive=True,
    intents=discord.Intents.all()) # Make sure to enable all intents in the developer portal.


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name} ({bot.user.id})")


@bot.command()
async def hello(ctx):
    """ A friendly hello from the bot! """
    
    return await ctx.reply("Hello! I'm the Retro Bot. Use **$help** for a list of my commands!", mention_author=False)
  
@bot.command()
async def play(ctx):
    for i in room:
        for ii in range(0, 9):
            room[i].pop(ii)
            room[i].insert(ii, stuff['empty'])

    room[9].pop(5)
    room[9].insert(5, stuff['player'])
    playerPos = []

    await updater(ctx.message)

@bot.command()
async def stop(ctx):
    """ Stops the current SPACE INVADERS game """

    global playing
    global sent

    if not playing: # If no one is playing, send a message
        return await ctx.reply("No one is playing! Use **$play** to start playing.", mention_author=False)

    if player.id != ctx.author.id: # If the player's ID isn't the same as the author's ID, then send a message.
        return await ctx.reply(f"Only {player.display_name} can stop this game, cause he started it!", mention_author=False)

    embed = discord.Embed(title=":space_invader: __**SPACE INVADERS**__ :space_invader:", description="Game stopped!", color=discord.Color.red())

    await sent.edit(embed=embed)

    playing = False
    sent = message
    enemy_poses.clear()
    bullet_poses.clear()
    return

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global playing

    if user.bot:
        return

    if reaction.message.id != sent.id:
        return

    if not playing:
        return

    emoji = reaction.emoji

    await reaction.remove(user)

    if reaction.emoji == "⬅️":
        if playerPos[1]-1 != -1:
            await left(room, stuff['empty'], stuff['player'], playerPos)
            return await updater(reaction.message)

    if reaction.emoji == "➡️":
        if playerPos[1]+1 != 10:
            await right(room, stuff['empty'], stuff['player'], playerPos)
            return await updater(reaction.message)

    if reaction.emoji == "◀️":
        (room[playerPos[0]]).pop(playerPos[1])
        (room[playerPos[0]]).insert(playerPos[1], stuff['empty'])
        (room[playerPos[0]]).pop(0)
        (room[playerPos[0]]).insert(0, stuff['player'])
        return await updater(reaction.message)

    if reaction.emoji == "▶️":
        (room[playerPos[0]]).pop(playerPos[1])
        (room[playerPos[0]]).insert(playerPos[1], stuff['empty'])
        (room[playerPos[0]]).pop(9)
        (room[playerPos[0]]).insert(9, stuff['player'])
        return await updater(reaction.message)

    if reaction.emoji == "🔴":
        shoot()
        return await updater(reaction.message)


bot.run("TOKEN", reconnect=True)
