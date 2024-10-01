from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import requests
import re

intents = discord.Intents.default()
intents.message_content = True
description = 'description'
bot = commands.Bot(command_prefix='!', description=description, intents=intents)

TOKEN = 'token'


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def card(ctx, *, key):
    noti = await ctx.send('Solgeがカードを検索しています。しばらくお待ちください。')

    URL = 'https://dm.takaratomy.co.jp/card/'
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = {
        'suggest': 'on',
        'keyword': key,
        'keyword_type[]': ['card_name', 'card_ruby', 'card_text'],
        'culture_cond[]': ['単色', '多色'],
        'pagenum': 1,
        'sort': 'release_new'
    }
    imagePattern = re.compile('src="(.*?)"')

    res = requests.post(URL, headers=headers, data=data)

    bsObject = BeautifulSoup(res.text, 'html.parser')
    bsObject = bsObject.find('div', {'id': 'cardlist'})

    getlink = imagePattern.findall(str(bsObject))
    if getlink:
        if len(getlink) == 1:
            embed = discord.Embed(title='『{}』のカード検索結果'.format(key))
            embed.set_image(url='https://dm.takaratomy.co.jp' + getlink[0])

        else:
            counter = 0

            urlPattern = re.compile('<a data-href="(.*?)"')
            titlePattern = re.compile('<title>(.*?)</title>')
            getUrl = urlPattern.findall(str(bsObject))

            for i in getUrl:
                counter = counter + 1
                each = 'https://dm.takaratomy.co.jp' + i

                res = requests.get(each)
                title = titlePattern.search(res.text).group(1)
                if counter == 1:
                    totalRes = '[%s](%s)' % (title.split(' | ')[0], each)

                elif counter == 10:
                    break

                else:
                    totalRes = totalRes + '\n[%s](%s)' % (title.split(' | ')[0], each)

            embed = discord.Embed(title='『{}』のカード検索結果'.format(key), description='{}'.format(totalRes))

    else:
        embed = discord.Embed(title='『{}』のカード検索結果'.format(key), description='カードが検索されませんでした')
    
    await noti.delete()
    await ctx.send(embed=embed)


bot.run(TOKEN)
