import discord as discord
import random as random

client = discord.Client()
playing = False
sent: discord.Message = discord.Message
player: discord.User = discord.User
enemyPoses = []
bulletPoses = []
score = 0

#    0    1    2    3    4    5    6    7    8    9
room = {1: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # ^
        2: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        3: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        4: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        5: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        6: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # x
        7: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        8: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ],  # |
        9: ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', ]}  # |
# <------------------------------y--------------------------------->

stuff = {'player':  ":railway_car:",
         'empty':  ":white_large_square:",
         'enemy':  ":space_invader:", 'bullet': ":exclamation:"}

for i in room:
    for ii in range(0, 10):
        room[i].pop(ii)
        room[i].insert(ii, stuff['empty'])
room[9].pop(5)
room[9].insert(5, stuff['player'])

playerPos = []  # 0 is Y,1 is X


async def left(ditcioary, inst_replace, inst_player, pos):
    (ditcioary[pos[0]]).pop(pos[1])
    (ditcioary[pos[0]]).insert(pos[1], inst_replace)
    (ditcioary[pos[0]]).pop(pos[1]-1)
    (ditcioary[pos[0]]).insert(pos[1]-1, inst_player)


async def right(ditcioary, inst_replace, inst_player, pos):
    (ditcioary[pos[0]]).pop(pos[1])
    (ditcioary[pos[0]]).insert(pos[1], inst_replace)
    (ditcioary[pos[0]]).pop(pos[1]+1)
    (ditcioary[pos[0]]).insert(pos[1]+1, inst_player)


async def up(ditcioary, inst_replace, inst_player, pos):
    (ditcioary[pos[0]]).pop(pos[1])
    (ditcioary[pos[0]]).insert(pos[1], inst_replace)
    (ditcioary[pos[0]-1]).pop(pos[1])
    (ditcioary[pos[0]-1]).insert(pos[1], inst_player)


async def down(ditcioary, inst_replace, inst_player, pos):
    (ditcioary[pos[0]]).pop(pos[1])
    (ditcioary[pos[0]]).insert(pos[1], inst_replace)
    (ditcioary[pos[0]+1]).pop(pos[1])
    (ditcioary[pos[0]+1]).insert(pos[1], inst_player)


def spawn_enemy(x):
    room[1].pop(x)
    room[1].insert(x, stuff['enemy'])


def shoot():
    (room[playerPos[0]-1]).pop(playerPos[1])
    (room[playerPos[0]-1]).insert(playerPos[1], stuff['bullet'])


async def gamemap(message: discord.Message):
    global toSend
    global playing
    global sent
    global enemyMove
    global player
    global enemyPoses
    global bulletPoses
    global score
    enemyMove = False
    toSend = 'Now Playing: SPACE INVADERS :space_invader:\nUse arrows in reaction section to move and 🔴 to shoot.\nYou can also use ◀️ ▶️ to go to corners.\nYour score: '+str(score)+'\n'

    if random.randint(0, 10) > 5:
        for i in range(random.randint(1, 3)):
            spawn_enemy(random.randint(0, 9))
    for i in range(1, len(room)+1):
        if stuff['enemy'] in room[i]:
            if i == 9:
                await message.channel.send('GAME OVER :space_invader:\nYour score: '+str(score)+'\nBetter luck next time :blush:! Use $play to retry.')
                await sent.delete()
                playing = False
                sent = discord.Message
                enemyPoses.clear()
                bulletPoses.clear()
                return
            elif room[i+1][room[i].index(stuff['enemy'])] == stuff['bullet']:
                pos = room[i].index(stuff['enemy'])
                (room[i]).pop(pos)
                (room[i]).insert(pos, stuff['empty'])
                (room[i+1]).pop(pos)
                (room[i+1]).insert(pos, stuff['empty'])
                score += 10
            else:
                enemyPoses.append([i, room[i].index(stuff['enemy'])])
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
                bulletPoses.append([i, room[i].index(stuff['bullet'])])

    for pos in enemyPoses:
        if random.randint(0, 10) > 3:
            await down(room, stuff['empty'], stuff['enemy'], pos)
    for pos in bulletPoses:
        await up(room, stuff['empty'], stuff['bullet'], pos)
    bulletPoses.clear()
    enemyPoses.clear()
    for i in range(1, len(room)+1):
        toSend += '\n' + "".join(room[i])
    if not playing:
        sent = await message.channel.send(toSend)
        await sent.add_reaction('◀️')
        await sent.add_reaction('⬅️')
        await sent.add_reaction('🔴')
        await sent.add_reaction('➡️')
        await sent.add_reaction('▶️')
        player = message.author
        playing = True
    else:
        await sent.edit(content=toSend)


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


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message: discord.Message):
    global playing
    global sent
    global playerPos
    global enemyPoses
    global bulletPoses
    if message.author == client.user:
        return
    else:
        if message.content.startswith('$hello'):
            await message.channel.send("Hello! I'm the Retro Bot. Use $help command to view my abilities")
        elif message.content.startswith('$help'):
            await message.channel.send("Sorry, I cannot help you :sweat: but if you want to play SPACE INVADERS, use $play")
        elif message.content.startswith('$stop'):
            if playing:
                if player == message.author:
                    await message.channel.send('Stopped playing SPACE INVADERS :space_invader:\nUse $play to play again.')
                    await sent.delete()
                    playing = False
                    sent = discord.Message
                    enemyPoses.clear()
                    bulletPoses.clear()
                else:
                    await message.channel.send('Only '+player.display_name+' can stop playing :space_invader: as he started!')
            else:
                await message.channel.send('Not playing!\nUse $play to start playing.')
        elif message.content.startswith('$play'):
            for i in room:
                for ii in range(0, 9):
                    room[i].pop(ii)
                    room[i].insert(ii, stuff['empty'])
            room[9].pop(5)
            room[9].insert(5, stuff['player'])
            playerPos = []
            if playing:
                await message.channel.send('Already playing!\nUse $stop to stop playing.')
            else:
                await updater(message)


@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    global playing
    if user == client.user:
        return
    elif reaction.message.id == sent.id:
        emoji = reaction.emoji
        message = reaction.message
        await reaction.remove(user)
        if playing:
            if emoji == '⬅️':
                if playerPos[1]-1 != -1:
                    await left(room, stuff['empty'], stuff['player'], playerPos)
                    await updater(message)
                else:
                    return
            elif emoji == '➡️':
                if playerPos[1]+1 != 10:
                    await right(room, stuff['empty'], stuff['player'], playerPos)
                    await updater(message)
                else:
                    return
            elif emoji == '◀️':
                (room[playerPos[0]]).pop(playerPos[1])
                (room[playerPos[0]]).insert(playerPos[1], stuff['empty'])
                (room[playerPos[0]]).pop(0)
                (room[playerPos[0]]).insert(0, stuff['player'])
                await updater(message)
            elif emoji == '▶️':
                (room[playerPos[0]]).pop(playerPos[1])
                (room[playerPos[0]]).insert(playerPos[1], stuff['empty'])
                (room[playerPos[0]]).pop(9)
                (room[playerPos[0]]).insert(9, stuff['player'])
                await updater(message)
            elif emoji == '🔴':
                shoot()
                await updater(message)


client.run('Your bot token here')
