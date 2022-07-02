import os
import json
import asyncio
from asyncio.tasks import wait_for
import requests
import discord
#from discord_slash import SlashCommand
from discord.ext import commands
from discord import Button, ButtonStyle, SelectMenu, SelectOption, ActionRow
import datetime, time
import random
from pretty_help import DefaultMenu, PrettyHelp
from keep_alive import keep_alive
#my_secret = os.environ["Token"]

bot = commands.Bot(command_prefix="!", intents=discord.Intents().all(), help_command=PrettyHelp())
#bot = commands.Bot(command_prefix = "!", description = "Bot by")
#slash = SlashCommand(bot, sync_commands = True)
#bot.remove_command('help')

@bot.event
async def on_ready():
  print("{} est prêt".format(bot.user))
  global start
  start=datetime.datetime.now()
#======================================================
  with open("adventure.json", "r") as f:
    global adv
    adv=json.load(f)
  with open("guilds.json", "r") as f:
    global guilds
    guilds=json.load(f)
  with open("shop.json", "r") as f:
    global shop
    shop=json.load(f)
  with open("gem_shop.json", "r") as f:
    global gem_shop
    gem_shop=json.load(f)
  with open("levels.json","r") as f:
    global levels
    levels=json.load(f)

@bot.event
async def on_raw_bulk_message_delete(payload):
  salon=bot.get_channel(932297174606290957)
  guild=bot.get_guild(payload.guild_id)
  await salon.send(f"{len(payload.message_ids)} messages supprimés dans <#{payload.channel_id}>\n({guild})")
#======================================================
menu = DefaultMenu(page_left="◀️", page_right="▶️", remove="❌")#, active_time=15)
ending_note = f"Commande help de {bot.get_user(951899328828567612)}"#\nFor command {help.clean_prefix}{help.invoked_with}"
bot.help_command = PrettyHelp(menu=menu, ending_note=ending_note)
#nav = Navigation("◀️", "▶️", "❌")
#bot.help_command = PrettyHelp(navigation=nav,color=discord.Colour.green()
#======================================================
async def up():
  with open("adventure.json", "w") as f:
    json.dump(adv, f)
  with open("guilds.json", "w") as f:
    json.dump(guilds, f)
  with open("shop.json", "w") as f:
    json.dump(shop, f)
async def start_adv(user):
  adv[str(user.id)]={}
  adv[str(user.id)]["Niveau"]=1
  adv[str(user.id)]["Expérience"]=0
  adv[str(user.id)]["Niveau supérieur"]=100
  adv[str(user.id)]["Expérience totale"]=0
  adv[str(user.id)]["Vies"]=100
  adv[str(user.id)]["Vies max"]=100
  adv[str(user.id)]["Pièces"]=0
  adv[str(user.id)]["Gemmes"]=10
  adv[str(user.id)]["Points"]=0
  adv[str(user.id)]["Canne à pêche"]=False
  adv[str(user.id)]["Fusil"]=False
  adv[str(user.id)]["Arme"]=False
  adv[str(user.id)]["Niveau de l'arme"]=0
  adv[str(user.id)]["Inventaire"]=[]
  adv[str(user.id)]["Joignement"]=int(round(time.time(),0))
  await up()
async def niveau_sup(user, chan):
  if adv[str(user.id)]["Expérience"]>=adv[str(user.id)]["Niveau supérieur"]:
    adv[str(user.id)]["Expérience"]-=adv[str(user.id)]["Niveau supérieur"]
    adv[str(user.id)]["Niveau supérieur"]=int(adv[str(user.id)]["Niveau supérieur"]*1.025)+adv[str(user.id)]["Niveau"]*4
    adv[str(user.id)]["Niveau"]+=1
    adv[str(user.id)]["Vies max"]=int((adv[str(user.id)]["Vies max"]*1.01)+10)
    adv[str(user.id)]["Vies"]=adv[str(user.id)]["Vies max"]
    adv[str(user.id)]["Pièces"]+=adv[str(user.id)]["Niveau"]*5+100
    adv[str(user.id)]["Gemmes"]+=int(adv[str(user.id)]["Niveau"]/2)
    await up()
    nv=adv[str(user.id)]["Niveau"]
    await chan.send(f"{user.mention}, vous venez de passer au niveau {nv} !\nVous gagnez {nv*5+100} pièces et {int(nv/2)} gemmes !")
async def get_power(user):
  return int((adv[str(user.id)]["Vies"]+adv[str(user.id)]["Niveau"])*(adv[str(user.id)]["Niveau de l'arme"]+1))
#=====================================================
class Aventure(commands.Cog):
  """ Commandes d'aventure """
  
  @commands.command(name="profile", aliases=["p"], brief="Pour regarder son profil", help="Pour regarder son profil")
  async def profile(self, ctx, user:discord.Member=None):
    if not user:
      user=ctx.author
    if str(user.id) in adv:
      e=discord.Embed(timestamp=datetime.datetime.utcnow(),title=f"Voici le profil de {user.name}", color=discord.Color.gold())
      e.set_author(name=str(user), icon_url=user.avatar_url)
      guild=bot.get_guild(932297174606290954)
      e.set_thumbnail(url=guild.icon_url)
      #e.set_thumbnail(url=ctx.guild.icon_url)
      a=adv[str(user.id)]
      e.add_field(name="Niveau", value=a["Niveau"])
      exp=a["Expérience"];sup=a["Niveau supérieur"]
      p=exp/sup*100;value=""
      if p>=95:
        value="▣▣▣▣▣▣▣▣▣▣"
      elif p>=90:
        value="▣▣▣▣▣▣▣▣▣▢"
      elif p>=80:
        value="▣▣▣▣▣▣▣▣▢▢"
      elif p>=70:
        value="▣▣▣▣▣▣▣▢▢▢"
      elif p>=60:
        value="▣▣▣▣▣▣▢▢▢▢"
      elif p>=50:
        value="▣▣▣▣▣▢▢▢▢▢"
      elif p>=40:
        value="▣▣▣▣▢▢▢▢▢▢"
      elif p>=30:
        value="▣▣▣▢▢▢▢▢▢▢"
      elif p>=20:
        value="▣▣▢▢▢▢▢▢▢▢"
      elif p>=10:
        value="▣▢▢▢▢▢▢▢▢▢"
      elif p<10:
        value="▢▢▢▢▢▢▢▢▢▢"
      e.add_field(name="Expérience", value=f"```\n{exp} {value} {sup} xp```\nTotal : "+str(a["Expérience totale"])+" xp", inline=False)
      e.add_field(name="Vies", value=str(a["Vies"])+"/"+str(a["Vies max"]))
      e.add_field(name="Pièces", value=a["Pièces"], inline=False)
      e.add_field(name="Gemmes", value=a["Gemmes"])
      e.add_field(name="Points", value=a["Points"], inline=False)
      value=""
      for item in a["Inventaire"]:
        value+=str(item["name"])+" : "+str(item["amount"])+"\n"
      if a["Canne à pêche"] is True:
        value+="Canne à pêche"
        if a["Fusil"] is True:
          value+="\nFusil"
      elif a["Fusil"] is True:
        value+="Fusil"
      e.add_field(name="Inventaire", value=value, inline=False)
      if a["Arme"] is True:
        e.add_field(name="Arme", value="Niveau "+str(a["Niveau de l'arme"]))
      e.add_field(name="A rejoint l'aventure le", value="<t:"+str(a["Joignement"])+">", inline=False)
      AuthorPower=await get_power(user)
      e.set_footer(text="Puissance actuelle estimée : "+str(AuthorPower))
      await ctx.send(embed=e)
    else:
      await ctx.send(f"{user.name} n'a pas commencé son aventure !")
      
  #=====================================================

  @commands.command(name="test")
  async def test(self, ctx, msg:discord.Message):
    await ctx.send(int(round(msg.created_at.timestamp(),0)))
    #await ctx.send(f"<t:{int(round(time.time(),0))}>")
  
  @commands.command(name="adventure", aliases=["adv"], brief="Actions concernant l'aventure", help="Actions concernant l'aventure")
  async def adventure(self, ctx, *args):
    if args:
      if args[0]=="start":
        if str(ctx.author.id) in adv:
          await ctx.send(f"Vous avez déjà commencé votre aventure {ctx.author.mention} !")
        else:
          await start_adv(ctx.author)
          await ctx.send(f"Vous commencez votre aventure {ctx.author.mention} !")
      elif args[0]=="info":
        await ctx.send("Pour commencer il y a !regeneration qui permet de récupérer des vies\nIl y a ensuite !adventure pour tout ce qui concerne l'aventure elle-même\n!battle permet de lancer une bataille\n!fish est pour pêcher évidemment\n!hunt est complètement dédié à la chasse\net pour finir !profile sert à regarder son profil ! ")
      elif args[0]=="reset":
        del adv[str(ctx.author.id)]
        await start_adv(ctx.author)
        await ctx.send(f"Vous recommencez votre aventure {ctx.author.mention} :exploding_head:")
    else:
      await ctx.send("Vous désirez ? Voici vos choix :```\n- !adventure start\n- !adventure info\n- !adventure reset```")

  @commands.command(name="fish", brief="Pour pêcher", help="Pour pêcher")
  async def fish(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if adv[str(ctx.author.id)]["Canne à pêche"]==True:
      gain=random.randint(5,10)
      adv[str(ctx.author.id)]["Pièces"]+=gain
      adv[str(ctx.author.id)]["Expérience"]+=int(gain/1.5)
      adv[str(ctx.author.id)]["Expérience totale"]+=int(gain/1.5)
      l="";luck=random.randint(1,20)
      if luck==20:
        adv[str(ctx.author.id)]["Canne à pêche"]=False;l="\nVotre maladresse vous fait perdre votre canne à pêche lol"
      await ctx.send(f"{ctx.author.mention}, vous pêchez et gagnez {gain} pièces ainsi que {int(gain/1.5)} xp.{l}")
      await up()
    else:
      await ctx.send(f"Avec quoi avez-vous cru pouvoir pêcher ?! :rofl:\nAllez plutôt vous acheter une canne à pêche !")

  @commands.command(name="hunt", brief="Pour chasser", help="Pour chasser")
  async def hunt(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if adv[str(ctx.author.id)]["Fusil"]==True:
      gain=random.randint(15,30)
      adv[str(ctx.author.id)]["Pièces"]+=gain
      adv[str(ctx.author.id)]["Expérience"]+=int(gain/1.5)
      adv[str(ctx.author.id)]["Expérience totale"]+=int(gain/1.5)
      l="";luck=random.randint(1,20);unluck=random.randint(1,200)
      if luck==20:
        adv[str(ctx.author.id)]["Fusil"]=False;l="\nVotre venez de casser votre fusil lol"
      if unluck==200:
        adv[str(ctx.author.id)]["Fusil"]=False
        adv[str(ctx.author.id)]["Vies"]=0
        await ctx.send(f"{ctx.author.mention}, vous perdez toutes vos vies et votre fusil car un ours vous a mangé.")
        await up()
        return
      await ctx.send(f"{ctx.author.mention}, vous chassez et gagnez {gain} pièces ainsi que {int(gain/1.25)} xp.{l}")
      await up()
    else:
      await ctx.send(f"Avec quoi avez-vous cru pouvoir chasser ?! :rofl:\nAllez plutôt vous acheter un fusil !")

  @commands.command(name="battle", aliases=["btl"], brief="Lance une bataille", help="Lance une bataille")
  async def battle(self, ctx, user:discord.Member=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if user:
      if not str(user.id) in adv:
        return await ctx.send(f"{user.name} n'a pas commencé l'aventure !")
      await ctx.send(f"{user.mention}, {ctx.author.name} vous défie ! `A`ccepter ou `r`efuser ?")
      def check(author):
        def inner_check(message):
          return message.author == user
        return inner_check
      message = await bot.wait_for("message", check=check(user), timeout=60.0)
      mess=message.content.lower()
      while True:
        try:
          if mess=="r":
            return await ctx.send(f"{ctx.author.mention}, {user.name} decline votre défi.")
          elif mess=="a":
            msg=await ctx.send("Le combat est lancé !")
            AuthorPower=(adv[str(ctx.author.id)]["Vies"]+adv[str(ctx.author.id)]["Niveau"])*(adv[str(ctx.author.id)]["Niveau de l'arme"]+1)*(random.randint(100,200)/100)
            UserPower=(adv[str(user.id)]["Vies"]+adv[str(user.id)]["Niveau"])*(adv[str(user.id)]["Niveau de l'arme"]+1)*(random.randint(100,200)/100)
            time.sleep(1)
            if AuthorPower>UserPower:
              await msg.edit(content=f"{ctx.author.mention} gagne le combat face à {user.mention} !\nPuissance de {ctx.author.name} pendant ce combat : {round(AuthorPower,2)}\nPuissance de {user.name} pendant ce combat : {round(UserPower,2)}")
            elif AuthorPower<UserPower:
              await msg.edit(content=f"{user.mention} gagne le combat face à {ctx.author.mention} !\nPuissance de {ctx.author.name} pendant ce combat : {round(AuthorPower,2)}\nPuissance de {user.name} pendant ce combat : {round(UserPower,2)}")
            else:
              await msg.edit(content=f"Incroyable ! C'est une égalité entre {ctx.author.mention} et {user.mention} !\nPuissance de {ctx.author.name} pendant ce combat : {round(AuthorPower,2)}\nPuissance de {user.name} pendant ce combat : {round(UserPower,2)}")
          else:
            await ctx.send("Ce n'est pas une option valable !")
            break
          break
        except asyncio.TimeoutError:
          return await ctx.send(f"{ctx.author.mention}, {user.name} ne semble pas disposé pour une bataille.")
        await ctx.send("Une erreur est survenue.")
    else:
      event=random.randint(1,20)
      if event==20:
        BossPower=random.randint(adv[str(ctx.author.id)]["Niveau"]**2,adv[str(ctx.author.id)]["Niveau"]**2*2)
        embed=discord.Embed(title="Boss", description=f"Vous tombez sur un boss, sa puissance estimée est de {BossPower}.\nSouhaitez-vous l'affronter ou fuir ?", color=discord.Colour.lighter_gray())
        msg=await ctx.send(embed=embed)
        await msg.add_reaction("✅");await msg.add_reaction("❌");reacts=["✅","❌"]
        def check(reaction, user):
          return user == ctx.author and str(reaction.emoji) in reacts
        try:
          reaction, user = await bot.wait_for("reaction_add",timeout=60.0,check=check)
          if str(reaction.emoji)=="✅":
            await ctx.send("Le combat commence !")
            AuthorPower=await get_power(ctx.author)*(random.randint(100,200)/100)
            BossPower*=random.randint(75,200)/100
            if AuthorPower>BossPower:
              difference=AuthorPower-BossPower
              lost=int(1/difference*(1000*adv[str(ctx.author.id)]["Niveau"]))
              if lost>=adv[str(ctx.author.id)]["Vies"]:
                lost=adv[str(ctx.author.id)]["Vies"]-1
              bonus=int(difference/6)
              adv[str(ctx.author.id)]["Vies"]-=lost
              adv[str(ctx.author.id)]["Pièces"]+=bonus
              adv[str(ctx.author.id)]["Expérience"]+=int(bonus*1.25)
              adv[str(ctx.author.id)]["Expérience totale"]+=int(bonus*1.25)
              await up()
              e=discord.Embed(title="Victoire", description=f"Vous remportez la bataille !\nVous gagnez {bonus} pièces et {int(bonus*1.25)} xp\nVotre puissance au combat : {round(AuthorPower,2)}\nPuissance du boss au combat : {round(BossPower,2)}.\nVies restantes : "+str(adv[str(ctx.author.id)]["Vies"])+"/"+str(adv[str(ctx.author.id)]["Vies max"])+".", color=discord.Colour.green())
              await ctx.send(embed=e)
            else:
              adv[str(ctx.author.id)]["Vies"]=0
              await up()
              e=discord.Embed(title="Défaite", description=f"Vous mourrez au combat.\nVotre puissance au combat : {round(AuthorPower,2)}\nPuissance du boss au combat : {round(BossPower,2)}.\nVies restantes : "+str(adv[str(ctx.author.id)]["Vies"])+"/"+str(adv[str(ctx.author.id)]["Vies max"])+".", color=discord.Colour.red())
              await ctx.send(embed=e)
          else:
            lost=random.randint(adv[str(ctx.author.id)]["Niveau"]*2,(adv[str(ctx.author.id)]["Niveau"]**2+1))
            adv[str(ctx.author.id)]["Pièces"]-=lost
            await up()
            e=discord.Embed(title="Fuite", description=f"Vous fuyez et perdez {lost} pièces.", color=discord.Colour.dark_red())
            await ctx.send(embed=e)
        except asyncio.TimeoutError:
          lost=random.randint(adv[str(ctx.author.id)]["Niveau"]*2,(adv[str(ctx.author.id)]["Niveau"]**2+1))
          adv[str(ctx.author.id)]["Pièces"]-=lost
          await up()
          e=discord.Embed(title="Fuite", description=f"Vous fuyez et perdez {lost} pièces.", color=discord.Colour.dark_red())
          return await ctx.send(embed=e)
        else:
          return await reaction.remove(ctx.author)
      else:
        pass
      minus=int(random.randint(20,40)*(0.025*adv[str(ctx.author.id)]["Niveau"]))+10
      if adv[str(ctx.author.id)]["Niveau de l'arme"]>0:
        minus=int(minus/adv[str(ctx.author.id)]["Niveau de l'arme"])
      bonus=int(random.randint(15,30)*(0.0225*adv[str(ctx.author.id)]["Niveau"])*2)+5
      luck=random.randint(1,10)
      if adv[str(ctx.author.id)]["Vies"]-minus<0:
        adv[str(ctx.author.id)]["Vies"]=0
        await up()
        vies=adv[str(ctx.author.id)]["Vies"];max=adv[str(ctx.author.id)]["Vies max"]
        e=discord.Embed(title="Défaite", description=f"Vous perdez la bataille.\nVies restantes : {vies}/{max}", color=discord.Color.red())
        await ctx.send(embed=e)
      else:
        adv[str(ctx.author.id)]["Vies"]-=minus
        l=0
        if luck==10:
          l=random.randint(10,20)
        adv[str(ctx.author.id)]["Pièces"]+=bonus+l
        adv[str(ctx.author.id)]["Expérience"]+=bonus*2
        adv[str(ctx.author.id)]["Expérience totale"]+=bonus*2
        l2=0
        if adv[str(ctx.author.id)]["Fusil"] is False:
          l2=random.randint(1,50)
          if l2==50:
            adv[str(ctx.author.id)]["Fusil"]=True
            l2=100
        l3=0
        if adv[str(ctx.author.id)]["Canne à pêche"] is False:
          l3=random.randint(1,50)
          if l3==50:
            adv[str(ctx.author.id)]["Canne à pêche"]=True
            l3=100
        await up()
        vies=adv[str(ctx.author.id)]["Vies"];max=adv[str(ctx.author.id)]["Vies max"]
        e=discord.Embed(title="Victoire", description=f"Vous sortez vainqueur de cette bataille et gagnez {bonus} pièces ainsi que {bonus*2} xp.\nVies restantes : {vies}/{max}", color=discord.Color.green())
        if l>0:
          e.add_field(name="Bonus pièces", value=f"Vous avez trouvé {l} pièces sur votre chemin.", inline=False)
        if l2==100 and l3==100:
          e.add_field(name="Bonus items", value=f"Quelle chance ! Un brave homme vous ayant vu vous battre vous a offert sa canne à pêche et son fusil, émerveillé.")
        elif l2==100:
          e.add_field(name="Bonus item", value=f"Vous decouvrez un fusil dans une maison abandonnée.")
        elif l3==100:
          e.add_field(name="Bonus item", value=f"Une canne à pêche sauvage apparaît au détour d'un lac, les gens sont décidément tête en l'air !")
        await ctx.send(embed=e)
        
      
  @commands.command(name="regeneration", aliases=["reg", "regen"], brief="Pour récupérer des vies", help="Pour récupérer des vies")
  async def regen(self, ctx, number:int=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if number:
      if number<6 and number>0:
        vies=int((adv[str(ctx.author.id)]["Vies max"]*(number*10/100))*2)
        if adv[str(ctx.author.id)]["Vies"]==adv[str(ctx.author.id)]["Vies max"]:
          await ctx.send("Vos vies sont au maximum !")
          return
        if adv[str(ctx.author.id)]["Vies"]+vies<=adv[str(ctx.author.id)]["Vies max"]:
          pieces=int(vies*1.25)
          adv[str(ctx.author.id)]["Vies"]+=vies
          adv[str(ctx.author.id)]["Pièces"]-=pieces
          await ctx.send(f"Vous payez {pieces} pièces et gagnez {vies} vies.")
        else:
          vies=adv[str(ctx.author.id)]["Vies max"]-adv[str(ctx.author.id)]["Vies"]
          pieces=int(vies*1.25)
          adv[str(ctx.author.id)]["Vies"]+=vies
          adv[str(ctx.author.id)]["Pièces"]-=pieces
          await ctx.send(f"Vous payez {pieces} pièces et gagnez {vies} vies.")
        await up()
      else:
        await ctx.send(f"{ctx.author.mention}, veuillez mettre un nombre compris entre 1 et 5.")
    else:
      while True:
        e=discord.Embed(timestamp=datetime.datetime.utcnow(), title="Voici vos options, veuillez répondre avec le numéro de l'option.", description="Écrivez `0` pour fermer la page d'options.", color=discord.Color.blue())
        for i in range(2,12,2):
          p100=adv[str(ctx.author.id)]["Vies max"]
          e.add_field(name=int(i/2), value=f"{int(p100*(i*10/100))} vies | {int((p100*(i*10/100))*1.25)} pièces", inline=False)
        e.set_footer(text="Vous avez "+str(adv[str(ctx.author.id)]["Vies"])+" vie(s).")
        msg=await ctx.send(embed=e)
        def check(author):
          def inner_check(message):
            return message.author == author
          return inner_check
        message = await bot.wait_for("message", check=check(ctx.author), timeout=60)
        try:
          number=int(message.content.lower())
        except:
          await msg.edit(content=f"{ctx.author.mention}, veuillez entrer un nombre.", embed=None)
          return
        try:
          if number<6 and number>0:
            vies=int((adv[str(ctx.author.id)]["Vies max"]*(number*10/100))*2)
            if adv[str(ctx.author.id)]["Vies"]==adv[str(ctx.author.id)]["Vies max"]:
              await ctx.send("Vos vies sont au maximum !")
              return
            if adv[str(ctx.author.id)]["Vies"]+vies<=adv[str(ctx.author.id)]["Vies max"]:
              pieces=int(vies*1.25)
              adv[str(ctx.author.id)]["Vies"]+=vies
              adv[str(ctx.author.id)]["Pièces"]-=pieces
              await ctx.send(f"Vous payez {pieces} pièces et gagnez {vies} vies.")
            else:
              vies=adv[str(ctx.author.id)]["Vies max"]-adv[str(ctx.author.id)]["Vies"]
              pieces=int(vies*1.25)
              adv[str(ctx.author.id)]["Vies"]+=vies
              adv[str(ctx.author.id)]["Pièces"]-=pieces
              await ctx.send(f"Vous payez {pieces} pièces et gagnez {vies} vies.")
            await up()
          elif number==0:
            await msg.edit(content="Vous ne souhaitez pas acheter de vies.", embed=None)
            break
          else:
            await msg.edit(content=f"{ctx.author.mention}, choisissez un nombre compris entre 1 et 5.", embed=None)
            break
          break
        except asyncio.TimeoutError:
          await ctx.send("Vous avez attendu trop longtemps avant de répondre !")
        else:
          await ctx.send("Une erreur est survenue.")

  @commands.command(name="create-guild", aliases=["cg"], brief="Pour créer une guilde", help="Pour créer une guilde")
  async def create_guild(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    for guild in guilds:
      if guilds[guild]["Owner"]==str(ctx.author.id):
        return await ctx.send("Vous avez déjà une guilde !")
    guild_questions = ["Quel est le nom de la guilde ?", "Quelle est la description de la guilde ?"]
    guild_answers = []
    def check(m):
      return m.author == ctx.author and m.channel == ctx.channel
    for question in guild_questions:
      await ctx.send(question)
      try:
        message = await bot.wait_for("message", timeout= 30.0, check=check)
      except asyncio.TimeoutError:
        await ctx.send("Vous n'avez pas répondu à temps. Vous avez 30 secondes par question pour répondre.")
        return
      else:
        guild_answers.append(message.content)
    guild = str(guild_answers[0])
    for g in guilds:
      if guild==g:
        e=discord.Embed(title="Erreur lors de la création de la guilde", description=f"Une guild porte déjà le nom de `{g}` !", color=discord.Colour.red())
        return await ctx.send(embed=e)
    desc = str(guild_answers[1])
    guilds[str(guild)]={}
    guilds[str(guild)]["Description"]=str(desc)
    guilds[str(guild)]["Owner"]=str(ctx.author.id)
    guilds[str(guild)]["Membres"]=[]
    guilds[str(guild)]["Membres"].append(str(ctx.author.id))
    await up()
    await ctx.send(f"Vous avez bien créé la guilde {guild}.\nsa description est {desc}.")

  @commands.command(name="join-guild", aliases=["jg"], brief="Pour rejoindre une guilde", help="Pour rejoindre une guilde")
  async def join_guild(self, ctx, *, guild:str=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if not guild:
      return await ctx.send("Précisez le nom de la guilde !")
    if len(guilds[guild]["Membres"])==10:
      return await ctx.send("La guilde est au complet !")
    if str(guild) in guilds:
      for g in guilds:
        if str(ctx.author.id) in guilds[str(g)]["Membres"]:
          await ctx.send(f"Vous êtes déjà dans la guilde {g} !")
          return
      guilds[str(guild)]["Membres"].append(str(ctx.author.id))
      await up()
      await ctx.send(f"Vous avez rejoint la guilde `{guild}` !")
    else:
      await ctx.send("Cette guilde n'existe pas !")

  @commands.command(name="leave-guild", aliases=["lg"], brief="Pour quitter une guilde", help="Pour quitter une guilde")
  async def leave_guild(self, ctx, *, guild:str=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if not guild:
      return await ctx.send("Précisez le nom de la guilde !")
    if str(guild) in guilds:
      if str(ctx.author.id) in guilds[str(guild)]["Membres"]:
        if guilds[str(guild)]["Owner"]==str(ctx.author.id):
          return await ctx.send("Vous ne pouvez pas quitter une guilde que vous avez créé !")
        guilds[str(guild)]["Membres"].remove(str(ctx.author.id))
        await up()
        await ctx.send(f"Vous quitté la guilde `{guild}`.")
      else:
        await ctx.send(f"Vous n'êtes pas dans cette guilde.")
    else:
      await ctx.send("Cette guilde n'existe pas !")

  @commands.command(name="guild", brief="Pour regarder une guilde", help="Pour regarder une guilde")
  async def guild(self, ctx, *, guild=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if guild:
      for g in guilds:
        if g==guild:
          desc=guilds[g]["Description"]
          owner=guilds[g]["Owner"]
          membres=""
          members=len(guilds[g]["Membres"])
          for m in guilds[g]["Membres"]:
            membre=bot.get_user(int(m))
            if m==guilds[g]["Owner"]:
              membres+="👑 "+str(membre.name)+"\n"
            else:
              membres+=str(membre.name)+"\n"
          e=discord.Embed(title=f"Guilde de {bot.get_user(int(owner))}", color=discord.Colour.gold())
          e.add_field(name=f"`{g}`\nDescription : {desc}", value=f"**Nombre de membres : {members}**\n{membres}", inline=False)
          return await ctx.send(embed=e)
    else:
      for g in guilds:
        if guilds[g]["Owner"]==str(ctx.author.id):
          desc=guilds[g]["Description"]
          membres=""
          members=len(guilds[g]["Membres"])
          for m in guilds[g]["Membres"]:
            membre=bot.get_user(int(m))
            if m==guilds[g]["Owner"]:
              membres+="👑 "+str(membre.name)+"\n"
            else:
              membres+=str(membre.name)+"\n"
          e=discord.Embed(title=f"Voici votre guilde", color=discord.Colour.gold())
          e.add_field(name=f"`{g}`\nDescription : {desc}", value=f"**Nombre de membres : {members}**\n{membres}", inline=False)
          return await ctx.send(embed=e)
      await ctx.send("Vous n'avez pas de guilde !")
  
  @commands.command(name="guilds", brief="Pour consulter les guildes", help="Pour consulter les guildes")
  async def guilds(self, ctx):
    e=discord.Embed(title="Guildes", color=discord.Colour.gold())
    for guild in guilds:
      e.add_field(name=guild, value=str(guilds[guild]["Description"])+"\nMembres : "+str(len(guilds[guild]["Membres"])))
    await ctx.send(embed=e)
    #e=discord.Embed(title="Guildes", color=discord.Colour.gold())
    #for guild in guilds:
    #  desc=guilds[guild]["Description"]
      #membres=""
      #for m in guilds[guild]["Membres"]:
      #  membre=bot.get_user(int(m))
      #  if str(membre.id)==guilds[guild]["Owner"]:
      #    membres+="👑 "+str(membre.name)+"\n"
      #  else:
      #    membres+=str(membre.name)+"\n"
      #e.add_field(name=f"`{guild}`\nDescription : {desc}", value=str(membres)+"\n** **", inline=False)
      #e.set_footer(text=" ")
    #await ctx.send(embed=e)

  @commands.command(name="edit-guild", aliases=["eg"], brief="Pour modifier le nom où la description d'une guilde", help="Pour modifier le nom ou la description d'une guilde")
  async def edit_guild(self, ctx, mode=None, *, new=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if mode:
      if not new:
        return await ctx.send("Vous devez mettre le nouveau nom ou la nouvelle description !")
      for g in guilds:
        if guilds[g]["Owner"]==str(ctx.author.id):
          if mode=="desc":
            guilds[g]["Description"]=new
            await up()
            return await ctx.send(f"Vous avez bien changé la description de votre guilde en `{new}`.")
          elif mode=="name":
            guild=guilds[g]
            del guilds[g]
            guilds[new]={}
            guilds[new]=guild
            await up()
            return await ctx.send(f"Vous avez bien changé le nom de votre guilde en `{new}`.")
          else:
            await ctx.send(f"{new} n'est pas un paramètre changeable.")
    else:
      await ctx.send("Veuillez préciser ce que vous voulez changer entre la description et le nom de votre guilde. (`desc` | `name`)")

  @commands.command(name="delete-guild", aliases=["dg"], brief="Pour supprimer une guilde", help="Pour supprimer une guilde")
  async def delete_guild(self, ctx, *, guild:str=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if guild:
      if guild in guilds:
        if guilds[guild]["Owner"]==str(ctx.author.id):
          del guilds[guild]
          await up()
          return await ctx.send(f"Vous avez bien supprimé la guilde `{guild}`.")
        await ctx.send("Vous n'êtes pas le créateur de cette guilde !")
      else:
        await ctx.send("Cette guilde n'existe pas !")
    else:
      await ctx.send("Veuillez préciser le nom de la guilde à supprimer.")

  @commands.command(name="guild-expulse", aliases=["ge"], help="Pour expulser un membre d'une guilde", brief="Pour expulser un membre d'une guilde")
  async def guild_expulse(self, ctx, member:discord.Member=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if member:
      for guild in guilds:
        if guilds[guild]["Owner"]==str(ctx.author.id):
          if str(member.id) in guilds[guild]["Membres"]:
            if guilds[guild]["Owner"]!=str(member.id):
              guilds[guild]["Membres"].remove(str(member.id))
              await up()
              return await ctx.send(f"Vous avez expulsé {member.name} de {guild}.")
            else:
              return await ctx.send("Vous ne pouvez pas vous expulser !")
          else:
            return await ctx.send("Ce membre n'est pas dans votre guilde !")
      await ctx.send("Vous devez avoir une guilde pour pouvoir expulser quelqu'un !")
    else:
      await ctx.send("Veuillez spécifier le membre à expulser !")
    
  @commands.command(name="top", brief="Pour regarder le classement des joueurs ou des guilds", help="Pour regarder le classement des joueurs ou des guildes")
  async def top(self, ctx, *args):
    if args:
      if args[0]=="g" or args[0]=="guilds":
        x=5
        top = {}
        total=[]
        for guild in guilds:
          levels=0
          for member in guilds[guild]["Membres"]:
            levels+=adv[member]["Niveau"]
          top[levels] = guild
          total.append(levels)
        total = sorted(total,reverse=True)
        em=discord.Embed(title=f"Top {x} du classement des guildes", color=discord.Colour.blue())
        place = 1
        tt=[]
        for amt in total:
          guild = top[amt]
          if not guild in tt:
            tt.append(guild)
            lvls=amt
            em.add_field(name = f"\t{place}. {guild}" , value = f"Niveaux : {lvls}",  inline = False)
            if place==x:
              break
            else:
              place+=1
        return await ctx.send(embed=em)
      players=["players", "p", "joueurs", "j"]
      if any(i in args[0].lower() for i in players):
        x=5
        top = {}
        total = []
        for user in adv:
          name = int(user)
          if bot.get_user(name):
            tt_xp = adv[user]["Expérience totale"]
            top[tt_xp] = name
            total.append(tt_xp)
        total = sorted(total,reverse=True)
        em = discord.Embed(title = f"Top {x} du classement", color = discord.Color.blue())
        place = 1
        tt=[]
        for amt in total:
          id_ = top[amt]
          user = bot.get_user(id_)
          if not user in tt:
            tt.append(user)
            lvl=adv[str(user.id)]["Niveau"]
            em.add_field(name = f"\t{place}. {user.name}" , value = f"Niveau {lvl}",  inline = False)
            if place==x:
              break
            else:
              place+=1
        await ctx.send(embed=em)
      else:
        await ctx.send("Ce classement n'existe pas !")
    else:
      await ctx.send("Veuillez préciser le type de classement que vous voulez consulter. (`players` | `guilds`)")

  @commands.command(name="upgrade", brief="Pour améliorer un item", help="Pour améliorer un item")
  async def upgrade(self, ctx, *args):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if not args:
      return await ctx.send("Précisez ce que vous voulez améliorer !")
    if args[0].lower()=="weapon" or args[0].lower()=="w" or args[0].lower()=="arme":
      if adv[str(ctx.author.id)]["Niveau de l'arme"]==0:
        return await ctx.send("Vous devez acheter une arme pour l'améliorer !")
      price=int((adv[str(ctx.author.id)]["Niveau de l'arme"]*500)*2*(0.5*(adv[str(ctx.author.id)]["Niveau de l'arme"]+1)))
      if adv[str(ctx.author.id)]["Pièces"]<price:
        return await ctx.send(f"Vous n'avez pas assez de pièces !\nIl vous en faut `{price}`.")
      adv[str(ctx.author.id)]["Niveau de l'arme"]+=1
      adv[str(ctx.author.id)]["Pièces"]-=price
      await up()
      await ctx.send("Vous améliorez votre arme.")
    else:
      await ctx.send(f"Vous ne pouvez pas améliorer `{args[0]}`.")

  @commands.command(name="gain", brief="Pour gagner des pièces et des vies", help="Pour gagner des pièces et des vies")
  @commands.cooldown(1,72000, commands.BucketType.user)
  async def gain(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    gain=random.randint(100,200)
    vies=adv[str(ctx.author.id)]["Vies"];viesmax=adv[str(ctx.author.id)]["Vies max"]
    addlife=int(viesmax*(1/random.randint(1,50)))
    if vies+addlife>viesmax:
      addlife=viesmax-vies
    adv[str(ctx.author.id)]["Vies"]+=addlife
    adv[str(ctx.author.id)]["Expérience"]+=int(gain/1.5)
    adv[str(ctx.author.id)]["Expérience totale"]+=int(gain*1.5)
    adv[str(ctx.author.id)]["Pièces"]+=gain
    await up()
    await ctx.send(f"Vous gagnez {gain} pièces, {int(gain/1.5)} xp et {addlife} vies !")
  @commands.command(name="shop", brief="Pour voir la boutique", help="Pour voir la boutique")
  async def shop(self, ctx, item=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous n'avez pas encore commencé votre aventure !")
    if item:
      if item in shop:
        await ctx.send("a")
      else:
        await ctx.send("Cet item n'existe pas !")
    else:
      e=discord.Embed(title="Boutique", description="Voici la boutique", color=discord.Colour.teal())
      for item in shop:
        e.add_field(name=item,value=str(shop[item]["description"])+"\nCoût : "+str(shop[item]["price"]))
      await ctx.send(embed=e)

  @commands.command(name="buy", brief="Actions concernant un achat", help="Actions concernant un achat")
  async def buy(self, ctx, *, item=None):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    if item:
      if not item in shop:
        return await ctx.send("Cet item n'existe pas !")
      if adv[str(ctx.author.id)]["Pièces"]<shop[item]["price"]:
        return await ctx.send("Vous n'avez pas assez de pièces !")
      adv[str(ctx.author.id)]["Pièces"]-=shop[item]["price"]
      adv[str(ctx.author.id)][item]=True
      await up()
      await ctx.send("Vous avez acheté l'item `"+str(shop[item]["name"])+"` pour "+str(shop[item]["price"])+" pièces.")
    else:
      e=discord.Embed(description="Veuillez préciser ce que vous voulez acheter !", color=discord.Color.greyple())
      await ctx.send(embed=e)

  @commands.command(name="gem-shop", help="Le shop des gemmes")
  async def gem_shop(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    embed=discord.Embed(title="Boutique des gemmes", description="Cliquez sur la réaction associée à l'article pour l'acheter.", color=discord.Colour.orange());reacts=["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"];i=0
    for item in gem_shop:
      embed.add_field(name=str(reacts[i])+" "+str(gem_shop[item]["name"]), value=str(gem_shop[item]["description"])+"\nPrix : "+str(gem_shop[item]["price"]));i+=1
    msg=await ctx.send(embed=embed);i=0
    for r in reacts:
      i+=1
      if i>len(gem_shop):
        break
      else:
        await msg.add_reaction(r)
    def check(reaction, user):
      return user == ctx.author and str(reaction.emoji) in reacts
    try:
      reaction, user = await bot.wait_for("reaction_add",timeout=60.0,check=check)
      if str(reaction.emoji)=="1️⃣":
        await ctx.send("Première option")
      if str(reaction.emoji)=="2️⃣":
        await ctx.send("Deuxième option")
      if str(reaction.emoji)=="3️⃣":
        await ctx.send("Troisième option")
    except asyncio.TimeoutError:
      await ctx.send("Vous avez attendu trop longtemps avant de réagir !")
    else:
      await reaction.remove(ctx.author)

  @commands.command(name="inspect", help="Pour inspecter")
  @commands.cooldown(1, 3600, commands.BucketType.user)
  async def inspect(self, ctx):
    if not str(ctx.author.id) in adv:
      return await ctx.send("Vous devez avoir commencé l'aventure pour effectuer cette action !")
    a=random.randint(1,100)
    if a<=50:
      await ctx.send("Vous avez trouvé... de l'air !")
    if a>=51 and a<=70:
      await ctx.send(f"Vous avez trouvé un onyx et gagnez {a} pièces.")
      adv[str(ctx.author.id)]["Inventaire"][0]["amount"]+=1
    if a>=71 and a<=85:
      await ctx.send(f"Vous avez trouvé un saphir et gagnez {a} pièces.")
      adv[str(ctx.author.id)]["Inventaire"][1]["amount"]+=1
    if a>=86 and a<=95:
      await ctx.send(f"Vous avez trouvé un rubis et gagnez {a} pièces.")
      adv[str(ctx.author.id)]["Inventaire"][2]["amount"]+=1
    if a>95:
      await ctx.send(f"Vous avez trouvé un diamant et gagnez {a} pièces.")
      adv[str(ctx.author.id)]["Inventaire"][3]["amount"]+=1
    adv[str(ctx.author.id)]["Pièces"]+=a
    await up()

  @commands.command(name="check-list", aliases=["cl", "checklist"], help="Pour savoir ses cooldowns")
  async def cl(self, ctx):
    inspect=bot.get_command("inspect").get_cooldown_retry_after(ctx)
    gain=bot.get_command("gain").get_cooldown_retry_after(ctx)
    e=discord.Embed(title="Check list", description=f"`!inspect` : {round(inspect/60,2)} min. (Le <t:{round(time.time()+inspect)}>)\n`!gain` : {round(gain/60,2)} min. (Le <t:{round(time.time()+gain)}>)", color=discord.Colour.random(), timestamp=datetime.datetime.utcnow())
    await ctx.send(embed=e)

  @commands.command(name="set")
  @commands.is_owner()
  async def set(self, ctx):
    await ctx.send("Initialisation en cours, veuillez patienter...\nMise en place : items.")
    for user in adv:
      adv[user]["Inventaire"]=[{'name': 'onyx', 'amount': 0}, {'name': 'saphir', 'amount': 0}, {'name': 'rubis', 'amount': 0}, {'name': 'diamant', 'amount': 0}]
    await up()
    time.sleep(1)
    await ctx.send("Initialisation terminée !")

#=======================================================================
from googletrans import Translator
translator=Translator()
def trans_func(text):
  text=translator.translate(text, dest="fr") #es/en/ge
  return text.text

import typing
class Owner(commands.Cog):
  """ Bah c'est dans le nom """
  @commands.command(name="translate", aliases=["trad"])
  async def translate(self, ctx,*,text):
    trad=trans_func(text)
    await ctx.send(trad)
  @commands.command(aliases=["additem"])
  async def add_item(self, ctx, i=None, d=None, p: int=None):
    if not i:
      return await ctx.send("Nom d'item ?")
    if not d:
      return await ctx.send("Description ?")
    if not p:
      return await ctx.send("Prix ?")
    shop[i]={}
    shop[i]["name"]=i
    shop[i]["description"]=d
    shop[i]["price"]=p
    with open("shop.json", "w") as f:
      json.dump(shop, f)

  @commands.command()
  @commands.has_permissions(manage_channels=True)
  @commands.bot_has_permissions(manage_channels=True)
  async def channel_count(self, ctx, category:int=None):
    guild=ctx.guild
    category=discord.utils.get(guild.categories, id=category)
    count=0
    for m in guild.members:
      if m.bot==False:
        count+=1
    if count!=0:
      try:
        chan=await guild.create_voice_channel(f"Membres : {count}", category=category, position=0)
        overwrite=chan.overwrites_for(guild.default_role)
        overwrite.connect=False
        await ctx.send(f"Le salon {chan.mention} a été créé !")
      except:
        await ctx.send(f"Je ne peux pas créer le salon.\nNombre de membres sur ce serveur : {count}.")
  
  @commands.command()
  async def slap(self, ctx, members: commands.Greedy[discord.Member], *, reason='no reason'):
    slapped = ", ".join(x.name for x in members)
    await ctx.send('{} just got slapped for {}'.format(slapped, reason))

  @commands.command()
  async def ban(self, ctx, members: commands.Greedy[discord.Member],delete_days: typing.Optional[int] = 0, *,reason: str):
    banned=""
    for member in members:
      await member.ban(delete_message_days=delete_days, reason=reason)
      banned+=f"{member.mention} (`{member}`) : {member.id}\n"
    await ctx.send(f"Done :\n{banned}")
  
  @commands.command(brief=" ", help=" ", name="give")
  @commands.is_owner()
  async def give(self, ctx, mode=None, amount=None, user:discord.Member=None):
    if not user:
      user=ctx.author
    if not amount:
      amount=100
    if not mode:
      mode="Pièces"
    if mode=="Expérience":
      adv[str(user.id)]["Expérience totale"]+=int(amount)
    adv[str(user.id)][mode]+=int(amount)
    await up()
    await ctx.message.add_reaction("✅")

  @commands.command(name="eval", help=" ", brief=" ")
  @commands.is_owner()
  async def eval(self, ctx, *, code:str):
    terminal=eval(code);a="￣"
    await ctx.send(f"```py\n{code}```\n{a*33}```py\n{terminal}```")

  @commands.command(name="uptime", help="Pour savoir depuis combien de temps je suis en ligne")
  async def uptime(self,ctx):
    t=datetime.datetime.now()
    diff=t-start
    heures,reste=divmod(int(diff.total_seconds()), 3600)
    minutes,secondes=divmod(reste, 60)
    jours,heures=divmod(heures, 24)
    if jours:
      fmt=f"{jours}j {heures}h {minutes}m {secondes}s"
    else:
      fmt=f"{heures}h {minutes}m {secondes}s"
    uptime=fmt.format(j=jours, h=heures, m=minutes, s=secondes)
    embed=discord.Embed(title="En ligne depuis", description=f"{uptime}", color=discord.Colour.random()).add_field(name="Date du dernier lancement", value=f"<t:{round(start.timestamp())}>").add_field(name="Date actuelle", value=f"<t:{round(t.timestamp())}>")
    await ctx.send(embed=embed)
  
  @commands.command()
  async def loupacte(self, ctx):
    if ctx.author.id!=888422346354995210:
      return await ctx.send("C'est pas pour toi :)")
    lundi="1 consommation de coc\n2 joins\n1 petit sachet de pillules\n3 bières\n20 shots de whisky"
    mardi="0.5 g coc\n1 join\n2 petits sachets de pillules\n5 bière\n10 shots de wisky"
    mercredi="50 g de coc\n7 joins\n20 bieres\n30 shots de whisky\n4 petits sachets de pillules\n7g d'heroine\n4 verres de lean"
    e=discord.Embed(title="Semaine", color=discord.Colour.blue()).add_field(name="Lundi", value=lundi).add_field(name="Mardi", value=mardi).add_field(name="Mercredi", value=mercredi)
    await ctx.send(embed=e)
  
  @commands.command()
  async def buttons(self, ctx):
    msg_with_buttons = await ctx.send("Boutons", components=[[Button(label="Bouton rouge",custom_id="rouge",style=ButtonStyle.red),Button(label="Bouton vert",custom_id="vert",style=ButtonStyle.green),Button(label="Bouton bleu",custom_id="bleu",style=ButtonStyle.blurple),Button(label="Bouton gris",custom_id="gris",style=ButtonStyle.grey)]])
    def check_button(i: discord.Interaction, button):
      return i.author == ctx.author and i.message == msg_with_buttons
    interaction, button = await bot.wait_for("button_click", check=check_button)
    embed = discord.Embed(title="Bouton cliqué",
    description=f"Vous avez cliqué sur le bouton {button.custom_id}.",
    color=discord.Color.random())
    await interaction.respond(embed=embed)

  @commands.command()
  async def select(ctx):
    msg_with_selects = await ctx.send("Menu des options", components=[[SelectMenu(custom_id='_select_it', options=[SelectOption(emoji='1️⃣', label='Option N° 1', value='1', description="Option 1"),SelectOption(emoji='2️⃣', label='Option N° 2', value='2', description='Option 2'),SelectOption(emoji='3️⃣', label='Option N° 3', value='3', description="Option 3"),SelectOption(emoji='4️⃣', label='Option N° 4', value='4', description="Option 4")],placeholder='Choisissez une option', max_values=3)]])
    def check_selection(i: discord.Interaction, select_menu):
      return i.author == ctx.author and i.message == msg_with_selects
    interaction, select_menu = await bot.wait_for("selection_select", check=check_selection)
    embed = discord.Embed(title="Choix :",description=f"Vous avez choisi "+"\n".join([f"l'option N° {o}" for o in select_menu.values]),color=discord.Color.random())
    await interaction.respond(embed=embed)
  
  @commands.command(name="t", help=" ", brief=" ")
  async def t(self, ctx):
    await ctx.send(len(bot.cached_messages))

  @commands.command(name="tt", help=" ", brief=" ")
  async def tt(self, ctx):
    await ctx.send(bot.ws)

  @commands.command(name="pingpong", help=" ", brief=" ")
  async def pingpong(self, ctx):
    await ctx.send(f"{round(bot.ws.latency)*1000} ms")

  @commands.command(name="latency", help=" ", brief=" ")
  async def latency(self, ctx):  
    try:
      t1 = time.perf_counter()
      async with ctx.typing():
        ta = t1
        t2 = time.perf_counter()
      async with ctx.typing():
        tb = t2
        ra = round((tb - ta) * 1000)
    finally:
      pass
    try:
      t1a = time.perf_counter()
      async with ctx.typing():
        ta1 = t1a
        t2a = time.perf_counter()
      async with ctx.typing():
        tb1 = t2a
        ra1 = round((tb1 - ta1) * 1000)
    finally:
      pass
    try:
      t1b = time.perf_counter()
      async with ctx.typing():
        ta2 = t1b
        t2b = time.perf_counter()
      async with ctx.typing():
        tb2 = t2b
        ra2 = round((tb2 - ta2) * 1000)
    finally:
      pass
    try:
      t1c = time.perf_counter()
      async with ctx.typing():
        ta3 = t1c
        t2c = time.perf_counter()
      async with ctx.typing():
        tb3 = t2c
        ra3 = round((tb3 - ta3) * 1000)
    finally:
      pass
    try:
      t1d = time.perf_counter()
      async with ctx.typing():
        ta4 = t1d
        t2d = time.perf_counter()
      async with ctx.typing():
        tb4 = t2d
        ra4 = round((tb4 - ta4) * 1000)
    finally:
      pass
    e = discord.Embed(title="Connection", colour = 909999)
    e.add_field(name='Ping 1', value=str(ra), inline=False)
    e.add_field(name='Ping 2', value=str(ra2), inline=False)
    e.add_field(name='Ping 3', value=str(ra3), inline=False)
    e.add_field(name='Ping 4', value=str(ra4), inline=False)
    e.add_field(name="Moyenne", value=str((ra+ra2+ra3+ra4)/4), inline=False)
    await ctx.send(embed=e)

  @commands.command(name="ping", brief=" ", help=" ")
  async def ping(self, ctx):
    ping = round(bot.latency * 1000)
    await ctx.send(f"{ping} ms")

  @commands.command(name="a", help=" ", brief=" ")
  async def a(self, ctx):
    a=discord.Embed(timestamp=datetime.datetime.utcnow(), title="a", description="a").add_field(name="a", value="a").set_author(name="a", icon_url=ctx.author.avatar_url).set_footer(text="a", icon_url=ctx.author.avatar_url).set_thumbnail(url=ctx.author.avatar_url).set_image(url=ctx.author.avatar_url)
    await ctx.reply(embed=a)
#=======================================================================
class Warns(commands.Cog):
  """ Commandes relatives aux warns """
  @commands.command(brief="Pour warn un membre", help="Pour warn un membre")
  @commands.has_permissions(administrator=True)
  async def warn(self, ctx, membre:discord.Member, raison=None):
    if membre is None:
      await ctx.send("Veuillez spécifier un membre !")
      return
    if not raison:
      raison="Aucune raison fournie."
    with open("warns.json", "r") as f:
      warns=json.load(f)
    await update_warns(warns, membre, ctx.guild)
    try:
      time = datetime.datetime.now()
      date=f"Le {time.day}/{time.month}/{time.year} à {time.hour+2}:{time.minute}:{time.second}"
      warn={"date":date, "raison":raison}
      warns[str(ctx.guild.id)][str(membre.id)]["warns"].append(warn)
    except:
      time = datetime.datetime.now()
      date=f"Le {time.day}/{time.month}/{time.year} à {time.hour+2}:{time.minute}:{time.second}"
      warn={"date":date, "raison":raison}
      warns[str(ctx.guild.id)][str(membre.id)]["warns"] = [warn]
    with open("warns.json", "w") as f:
      json.dump(warns, f)
    await ctx.send(f"{membre.mention} a été warn par {ctx.author.mention}\nRaison : `{raison}`")

  #@slash.slash(name="Warn", description="Pour warn un utilisateur.")
  @commands.has_permissions(administrator=True)
  async def warn_slash(ctx, membre:discord.Member, raison=None):
    if not raison:
      raison="Aucune raison fournie."
    with open("warns.json", "r") as f:
      warns=json.load(f)
    await update_warns(warns, membre, ctx.guild)
    try:
      time = datetime.datetime.now()
      date=f"Le {time.day}/{time.month}/{time.year} à {time.hour+2}:{time.minute}:{time.second}"
      warn={"date":date, "raison":raison}
      warns[str(ctx.guild.id)][str(membre.id)]["warns"]+=[warn]
      await ctx.send("try")
    except:
      time = datetime.datetime.now()
      date=f"Le {time.day}/{time.month}/{time.year} à {time.hour+2}:{time.minute}:{time.second}"
      warn={"date":date, "raison":raison}
      warns[str(ctx.guild.id)][str(membre.id)]["warns"]=[warn]
      await ctx.send("except")
    with open("warns.json", "w") as f:
      json.dump(warns, f)
    await ctx.send(f"{membre.name} a été warn par {ctx.author.mention}\nRaison : `{raison}`")

  @commands.command(brief="Pour consulter les warns d'un membre", help="Pour consulter les warns d'un membre")
  @commands.has_permissions(administrator=True)
  async def warns(self, ctx, membre:discord.Member=None):
    if membre is None:
      membre=ctx.author
    with open("warns.json", "r") as f:
      warns=json.load(f)
    if not str(membre.id) in warns[str(ctx.guild.id)]:
      await ctx.send(f"{membre.name} n'a pas de warns.")
      return
    try:
      warnings=warns[str(ctx.guild.id)][str(membre.id)]["warns"]
      embed=discord.Embed(title=f"Voici la liste des warns de {membre.name} :")
      index=0
      for warn in warnings:
        index+=1
        embed.add_field(name=str(index)+". "+str(warn["date"]), value=warn["raison"], inline=False)
      await ctx.send(embed=embed)
    except:
      await ctx.send(f"{membre.name} n'a pas de warns.")

  #@slash.slash(name="Warns", description="Pour connaître les warns d'un utilisateur")
  @commands.has_permissions(administrator=True)
  async def warns_slash(ctx, membre:discord.Member):
    with open("warns.json", "r") as f:
      warns=json.load(f)
    if not str(membre.id) in warns[str(ctx.guild.id)]:
      await ctx.send(f"{membre.name} n'a pas de warns.")
      return
    try:
      warnings=warns[str(ctx.guild.id)][str(membre.id)]["warns"]
      embed=discord.Embed(title=f"Voici la liste des warns de {membre.name} :")
      index=0
      for warn in warnings:
        index+=1
        embed.add_field(name=str(index)+". "+str(warn["date"]), value=warn["raison"], inline=False)
      await ctx.send(embed=embed)
    except:
      await ctx.send(f"{membre.name} n'a pas de warns.")

  @commands.command(aliases=["reset"], brief="Pour reset les warns d'un membre", help="Pour reset les warns d'un membre")
  @commands.has_permissions(administrator=True)
  async def reset_warns(self, ctx, membre:discord.Member=None):
    if membre is None:
      await ctx.send("Veuillez spécifier un membre !")
      return
    with open("warns.json", "r") as f:
      warns=json.load(f)
    await update_warns(warns, membre, ctx.guild)
    del warns[str(ctx.guild.id)][str(membre.id)]["warns"]
    with open("warns.json", "w") as f:
      json.dump(warns, f)
    await ctx.send(f"Vous avez bien réinitialisé les warns de {membre.name}.")

  #@slash.slash(name="Reset-warns", description="Pour reset les warns d'un utilisateur.")
  @commands.has_permissions(administrator=True)
  async def reset_warns_slash(ctx, membre:discord.Member):
    with open("warns.json", "r") as f:
      warns=json.load(f)
    await update_warns(warns, membre, ctx.guild)
    del warns[str(ctx.guild.id)][str(membre.id)]["warns"]
    with open("warns.json", "w") as f:
      json.dump(warns, f)
    await ctx.send(f"Vous avez bien réinitialisé les warns de {membre.name}.")

async def update_warns(warns, user, guild):
  if not str(guild.id) in warns:
    warns[str(guild.id)]={}
  if not str(user.id) in warns:
    warns[str(guild.id)][str(user.id)]={}
    warns[str(guild.id)][str(user.id)]["warns"]=[]
    #warns[str(guild.id)][str(user.id)]["warns"]={}
  with open("warns.json", "w") as f:
    json.dump(warns, f)

#=======================================================================
import re
cd = commands.CooldownMapping.from_cooldown(360, 60, commands.BucketType.user)
@bot.listen()
async def on_message(message):
  if message.guild.id!=932297174606290954:
    return
  if message.author.bot == True:
    return
  msg=message.content.lower()
  chan=message.channel
  bucket = cd.get_bucket(message)
  retry_after = bucket.update_rate_limit()
  if retry_after:
    pass
  else:
    with open("levels.json", "r") as f:
      users=json.load(f)
    xp=random.randint(15,25)
    await update_level(users, message.author, message.guild)
    await add_xp(users, message.author, message.guild, xp)
    await level_up(users, message.author, message.guild, message.channel)
  if str(message.author.id) in adv:
    await niveau_sup(message.author, message.channel)
  mess=re.sub('\W+','', msg)
  if mess.endswith("quoi"):
    await chan.send("feur")
  #if msg.endswith("quoi"):
    #await chan.send("feur")
  if msg.startswith("salut"):
    await message.add_reaction("👋")
  if msg=="bonjour":
    await chan.send("Bonjour")
  if "muscle" in msg:
    await chan.send("💪")


async def add_xp(users, user, guild, amount):
  xp=users[str(guild.id)][str(user.id)]["experience"]
  xp+=amount
  users[str(guild.id)][str(user.id)]["experience"]=xp
  with open("levels.json", "w") as f:
    json.dump(users, f)

async def level_up(users, user, guild, chan):
  if users[str(guild.id)][str(user.id)]["experience"]>=users[str(guild.id)][str(user.id)]["level_up"]:
    lvl=users[str(guild.id)][str(user.id)]["level"]
    xp=users[str(guild.id)][str(user.id)]["experience"]
    lvl_up=users[str(guild.id)][str(user.id)]["level_up"]
    xp-=lvl_up
    lvl+=1
    lvl_up=45+10*(lvl)+lvl_up
    users[str(guild.id)][str(user.id)]["level"]=lvl
    await chan.send(f"{user.mention}, vous venez de passer au niveau {lvl}.")
    users[str(guild.id)][str(user.id)]["experience"]=xp
    users[str(guild.id)][str(user.id)]["level_up"]=lvl_up
    with open("levels.json", "w") as f:
      json.dump(users,f)

async def update_level(users, user, guild):
  if not str(guild.id) in users:
    users[guild.id]={}
    with open("levels.json", "w") as f:
      json.dump(users, f)
  if not str(user.id) in users[str(guild.id)]:
    users[str(guild.id)][user.id]={}
    users[str(guild.id)][user.id]["experience"]=0
    users[str(guild.id)][user.id]["level"]=0
    users[str(guild.id)][user.id]["level_up"]=100
    with open("levels.json", "w") as f:
      json.dump(users, f)

async def get_rank(user, guild):
  with open("levels.json", "r") as f:
    users=json.load(f)
  xp=users[str(guild.id)][str(user.id)]["experience"]
  lvl=users[str(guild.id)][str(user.id)]["level"]
  lvl_up=users[str(guild.id)][str(user.id)]["level_up"]
  return xp, lvl, lvl_up

class Niveaux(commands.Cog):
  """ Relatif au système de niveaux """

  @commands.command(brief="Pour consulter votre rank", help="Pour consulter votre rank")
  @commands.cooldown(1,5, commands.BucketType.user)
  async def rank(self, ctx):
    rank=await get_rank(ctx.author, ctx.guild)
    await ctx.send(f"Carte d'xp de {ctx.author.name} :\nNiveau {rank[1]}\n{rank[0]} xp / {rank[2]}")

  #@slash.slash(name="Remove_xp")
  async def remove_xp_slash(ctx,amount=0):
    with open("levels.json", "r") as f:
      users=json.load(f)
    xp=users[str(ctx.guild.id)][str(ctx.author.id)]["experience"]
    xp-=amount
    users[str(ctx.guild.id)][str(ctx.author.id)]["experience"]=xp
    with open("levels.json", "w") as f:
      json.dump(users,f)
    await ctx.send(f"-{amount} xp")

  #@slash.slash(name="Rank",description="Pour voir votre rank.")
  async def rank_slash(ctx, user:discord.Member=None):
    if user is None:
      user=ctx.author
    with open("levels.json","r") as f:
      users=json.load(f)
    xp=users[str(ctx.guild.id)][str(user.id)]["experience"]
    lvl=users[str(ctx.guild.id)][str(user.id)]["level"]
    lvl_up=users[str(ctx.guild.id)][str(user.id)]["level_up"]
    await ctx.send(f"Niveau {lvl} | {xp} xp\n({xp}/{lvl_up})")

@bot.command(name='boutons', description='sends you some nice Buttons')
async def boutons(ctx: commands.Context):
  components = [ActionRow(Button(label='Option N°1', custom_id='option1', emoji="🆒", style=ButtonStyle.green), Button(label='Option N°2', custom_id='option2', emoji="🆗", style=ButtonStyle.blurple)), ActionRow(Button(label='Waa un autre bouton', custom_id='sec_row_1st option', style=ButtonStyle.red, emoji='😀'), Button(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', label="Clique sur ce lien pour aider mon owner à me développer plus vite !", style=ButtonStyle.url, emoji='🎬')) ]
  an_embed = discord.Embed(title='Waa des boutons', description='Clique sur le tien :wink:', color=discord.Color.random())
  msg = await ctx.send(embed=an_embed, components=components)

  def _check(i: discord.Interaction, b):
      return i.message == msg and i.member == ctx.author

  interaction, button = await bot.wait_for('button_click', check=_check)
  button_id = button.custom_id

  # This sends the Discord-API that the interaction has been received and is being "processed"
  await interaction.defer()
  # if this is not used and you also do not edit the message within 3 seconds as described below,
  # Discord will indicate that the interaction has failed.

  # If you use interaction.edit instead of interaction.message.edit, you do not have to defer the interaction,
  # if your response does not last longer than 3 seconds.
  await interaction.edit(embed=an_embed.add_field(name='Choose', value=f'Your Choose was `{button_id}`'), components=[components[0].disable_all_buttons(), components[1].disable_all_buttons()])
  # The Discord API doesn't send an event when you press a link button so we can't "receive" that.




pointers = []


class Pointer:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self._possition_x = 0
        self._possition_y = 0

    @property
    def possition_x(self):
        return self._possition_x

    def set_x(self, x: int):
        self._possition_x += x
        return self._possition_x

    @property
    def possition_y(self):
        return self._possition_y

    def set_y(self, y: int):
        self._possition_y += y
        return self._possition_y


def get_pointer(obj: typing.Union[discord.Guild, int]):
    if isinstance(obj, discord.Guild):
        for p in pointers:
            if p.guild.id == obj.id:
                return p
        pointers.append(Pointer(obj))
        return get_pointer(obj)

    elif isinstance(obj, int):
        for p in pointers:
            if p.guild.id == obj:
                return p
        guild = bot.get_guild(obj)
        if guild:
            pointers.append(Pointer(guild))
            return get_pointer(guild)
        return None


def display(x: int, y: int):
    base = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    base[y][x] = 1
    base.reverse()
    return ''.join(f"\n{''.join([str(base[i][w]) for w in range(len(base[i]))]).replace('0', '⬛').replace('1', '⬜')}" for i in range(len(base)))


empty_button = discord.Button(style=discord.ButtonStyle.Secondary, label=" ", custom_id="empty", disabled=True)


def arrow_button():
    return discord.Button(style=discord.ButtonStyle.Primary)


@bot.command(name="start_game")
async def start_game(ctx: commands.Context):
    pointer: Pointer = get_pointer(ctx.guild)
    await ctx.send(embed=discord.Embed(title="Little Game",
                                       description=display(x=0, y=0)),
                   components=[discord.ActionRow(empty_button, arrow_button().set_label('↑').set_custom_id('up'), empty_button),
                               discord.ActionRow(arrow_button().update(disabled=True).set_label('←').set_custom_id('left').disable_if(pointer.possition_x <= 0),
                                                 arrow_button().set_label('↓').set_custom_id('down').disable_if(pointer.possition_y <= 0),
                                                 arrow_button().set_label('→').set_custom_id('right'))
                               ]
                   )


@bot.on_click()
#async def up(i: discord.Interaction, button):
async def something(i: discord.Interaction, button):
    pointer: Pointer = get_pointer(i.guild)
    pointer.set_y(1)
    await i.edit(embed=discord.Embed(title="Little Game",
                                     description=display(x=pointer.possition_x, y=pointer.possition_y)),
                           components=[discord.ActionRow(empty_button, arrow_button().set_label('↑').set_custom_id('up').disable_if(pointer.possition_y >= 9), empty_button),
                                       discord.ActionRow(arrow_button().set_label('←').set_custom_id('left').disable_if(pointer.possition_x <= 0),
                                                         arrow_button().set_label('↓').set_custom_id('down'),
                                                         arrow_button().set_label('→').set_custom_id('right').disable_if(pointer.possition_x >= 9))]
                           )

@bot.on_click()
async def down(i: discord.Interaction, button):
    pointer: Pointer = get_pointer(i.guild)
    pointer.set_y(-1)
    await i.edit(embed=discord.Embed(title="Little Game",
                                          description=display(x=pointer.possition_x, y=pointer.possition_y)),
                           components=[discord.ActionRow(empty_button, arrow_button().set_label('↑').set_custom_id('up'), empty_button),
                                       discord.ActionRow(arrow_button().set_label('←').set_custom_id('left').disable_if(pointer.possition_x <= 0),
                                                         arrow_button().set_label('↓').set_custom_id('down').disable_if(pointer.possition_y <= 0),
                                                         arrow_button().set_label('→').set_custom_id('right').disable_if(pointer.possition_x >= 9))]
                           )

@bot.on_click()
async def right(i: discord.Interaction, button):
    pointer: Pointer = get_pointer(i.guild)
    pointer.set_x(1)
    await i.edit(embed=discord.Embed(title="Little Game",
                                           description=display(x=pointer.possition_x, y=pointer.possition_y)),
                           components=[discord.ActionRow(empty_button, arrow_button().set_label('↑').set_custom_id('up'), empty_button),
                                       discord.ActionRow(arrow_button().set_label('←').set_custom_id('left'),
                                                         arrow_button().set_label('↓').set_custom_id('down'),
                                                         arrow_button().set_label('→').set_custom_id('right').disable_if(pointer.possition_x >= 9))]
                           )

@bot.on_click()
async def left(i: discord.Interaction, button):
    pointer: Pointer = get_pointer(i.guild)
    pointer.set_x(-1)
    await i.edit(embed=discord.Embed(title="Little Game",
                                           description=display(x=pointer.possition_x, y=pointer.possition_y)),
                           components=[discord.ActionRow(empty_button, arrow_button().set_label('↑').set_custom_id('up'), empty_button),
                                       discord.ActionRow(arrow_button().set_label('←').set_custom_id('left').disable_if(pointer.possition_x <= 0),
                                                         arrow_button().set_label('↓').set_custom_id('down'),
                                                         arrow_button().set_label('→').set_custom_id('right'))]
                           )






  
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    tps=error.retry_after
    if tps//3600>=1:
      tps_h=round(tps/3600,2)
      tp=f"({tps_h}h)"
    elif tps//60>=1:
      tps_min=round(tps/60,2)
      tp=f"({tps_min}m)"
    else:
      tp=""
    try:
      error=discord.Embed(title=f"Cooldown",description=f"Veuillez réessayer dans {error.retry_after:.2f}s. {tp}", color=discord.Colour.red())
      await ctx.send(embed=error)
      return
    except:
      await ctx.send(f"Veuillez réessayer dans {error.retry_after:.2f}s.")

keep_alive()

def run():
  bot.add_cog(Aventure(bot))
  bot.add_cog(Niveaux(bot))
  bot.add_cog(Warns(bot))
  bot.add_cog(Owner(bot))
  Token=""
  bot.run(Token)

if __name__ == "__main__":
  run()
