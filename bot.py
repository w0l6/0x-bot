import discord, requests, json
from discord.ext import commands
from config import *
from typing import Union
import os,  json
from json import *


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="=", intents=intents)
bot.remove_command('help')
snip_mess = {}
antibot_status = {}
BLACKLIST_FILE = "blacklist.json"


def build_embed(title, description, color=0x3b3bf3):
    return discord.Embed(title=title, description=description, color=color)





def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return []  
    return []


def save_blacklist():
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(blacklist, f)



blacklist = load_blacklist()

def warning(titre, message):
    data = {
        "content": "**Alert** @everyone",
        "username": "Logs"
    }
    data["embeds"] = [
    {
        "color": 0x3B3BF3,
        "description" : message,
        "title" : titre
    }
    ]
    response = requests.post(urlwarning, json=data)

def logs(message):
    data = {
        "content": message,
        "username": "Logs"
    }
    response = requests.post(url_webhook, json=data)
    if response.status_code != 204:
        print(f"Erreur lors de l'envoi des logs: {response.status_code} - {response.text}")

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")







@bot.command(name="help")
async def help_command(ctx):
    if any(role.id == IDCOMMANDEMENT for role in ctx.author.roles):
        embed = discord.Embed(title="Commandes pour le **Commandement 0x**", description=" ", color=0x3b3bf3)
        embed.add_field(name="+ban @membre/<id>", value="permet de bannir", inline=False)
        embed.add_field(name="+unban <id>", value="permet de débannir", inline=False)
        embed.add_field(name="+addrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        embed.add_field(name="+rrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        embed.add_field(name="+renew", value="besoin de détailler ?", inline=False)
        embed.add_field(name="+derank @membre/<id>", value="retire tout les rôles d'un membre", inline=False)
        await ctx.reply(embed=embed)
    elif any(role.id == IDCONSEIL for role in ctx.author.roles):
        embed = discord.Embed(title="Commandes pour le **Conseil 0x**", description=" ", color=0x3b3bf3)
        embed.add_field(name="+ban @membre/<id>", value="permet de bannir", inline=False)
        embed.add_field(name="+unban <id>", value="permet de débannir", inline=False)
        embed.add_field(name="+addrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        embed.add_field(name="+rrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        embed.add_field(name="+derank @membre/<id>", value="retire tout les rôles d'un membre", inline=False)
        await ctx.reply(embed=embed)
    elif any(role.id == IDRC for role in ctx.author.roles):
        embed = discord.Embed(title="Commandes pour le **Recruteur 0x**", description=" ", color=0x3b3bf3)
        embed.add_field(name="+addrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        embed.add_field(name="+rrole @membre/<id> role-id", value="permet d'ajouter un role a un membre", inline=False)
        await ctx.reply(embed=embed)











                                         #            EVENT



@bot.event
async def on_member_join(member):
    if member.id in blacklist:
        try:
            await member.ban(reason="bl")

        except:
            logs(f"⚠️ Impossible de bannir {member}.")
    else:
        guild = member.guild
        is_active = antibot_status.get(guild.id, False)
        if member.bot and is_active:
            try:
                inviter = None
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                    if entry.target.id == member.id:
                        inviter = entry.user
                        break
                if not inviter:
                    print("⚠️ Impossible d’identifier l’invitant.")
                    return
                await member.kick(reason="Antibot activé")
                await guild.ban(inviter, reason="Tentative d'invitation de bot interdite")
                warning("Antibot",f"🤖 Bot kick : {member.name}#{member.discriminator}\n👤 Invité par : {inviter.name}#{inviter.discriminator}")
            except discord.Forbidden:
                print("❌ Permissions insuffisantes pour kick/ban.")
            except Exception as e:
                print(f"❌ Erreur dans l'antibot : {e}")    
            return  
        try:
            role = guild.get_role(IDRANDOM)  
            if role:
                await member.add_roles(role)
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de rôle : {e}")
            logs(f"Erreur lors de l'ajout de rôle : {e}")


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    if message.author.bot not in {1369155425231962184}:
        return
    snip_mess[message.channel.id] = {
        "content": message.content,
        "author": str(message.author),
        "time": int(message.created_at.timestamp())
    }




                                             #   ALL

@bot.command()
async def snipe(ctx):
    data = snip_mess.get(ctx.channel.id)
    if not data:
        await ctx.reply(embed=build_embed("❌","Aucun message trouvé"))
        return
    print(data["time"])
    await ctx.reply(embed=build_embed(":eyes:",f"Message : ``{data["content"]}`` \nDate: <t:{data["time"]}:R>"))
                                            # RC 











@bot.command()
async def addrole(ctx, user: discord.Member = None, role_id: int = None):
    author: discord.Member = ctx.author
    member: discord.Member = user
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL, IDRC] for role in author.roles):
        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        return await ctx.reply(embed=embed)
    if user is None or role_id is None:
        embed = build_embed("🦧", "Sa s'utilise comme ça : +addrole @membre <role-id>")
        return await ctx.reply(embed=embed)
    role = ctx.guild.get_role(role_id)
    if role is None:
        embed = build_embed("❌", "Rôle introuvable")
        return await ctx.reply(embed=embed)
    print(f"Rôle position : {role.position}, {author.top_role.position}, ")
    if role.position >= author.top_role.position:
        embed = build_embed("❌", "Tu ne peux pas attribuer un rôle égal ou supérieur au tien")
        return await ctx.reply(embed=embed)
    if any(r.position >= author.top_role.position for r in member.roles) :
        embed = build_embed("❌", "Tu ne peux donner un rôle à quelqu'un qui a un rôle plus élevé que le tien")
        return await ctx.reply(embed=embed)
    if role.position >= ctx.guild.me.top_role.position:
        embed = build_embed("❌", "Je peut pas attribuer ce rôle car il est au-dessus de mon rôle")
        return await ctx.reply(embed=embed)
    try:
        await member.add_roles(role, reason=f"add par {ctx.author} via +addrole")
        embed = build_embed("✅", f"Le rôle **{role.name}** a été donné à {member.mention}")
        return await ctx.reply(embed=embed)
    except discord.Forbidden:
        embed = build_embed("❌", f"Discord a dit non")
        return await ctx.reply(embed=embed)
    except discord.HTTPException as e:
        logs(f"Erreur HTTP dans addrole : {str(e)}")
        embed = build_embed("❌", f"Discord a dit non")
        return await ctx.reply(embed=embed)


@addrole.error
async def addrole_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = build_embed("🦧", "Argument invalide Utilisation : +addrole @membre <role-id>")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = build_embed("🦧", "Utilisation : +addrole @membre <role-id>")
        await ctx.reply(embed=embed)
    else:
        embed = build_embed("❌", "Une erreur est survenue")
        await ctx.reply(embed=embed)


@bot.command()
async def rrole(ctx, user: discord.Member = None, role_id: int = None):
    author: discord.Member = ctx.author
    member: discord.Member = user
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL, IDRC] for role in author.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande"))
    if user is None or role_id is None:
        return await ctx.reply(embed=build_embed("🦧", "Sa s'utilise comme ça : +rrole @membre <role-id>"))
    role = ctx.guild.get_role(role_id)
    if role is None:
        return await ctx.reply(embed=build_embed("❌", "Rôle introuvable"))
    if role.position >= author.top_role.position:
        return await ctx.reply(embed=build_embed("❌", "Tu ne peux pas retirer un rôle égal ou supérieur au tien"))
    if any(r.position >= author.top_role.position for r in member.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu ne peux pas modifier les rôles de ce membre"))
        
    if role.position >= ctx.guild.me.top_role.position:
        return await ctx.reply(embed=build_embed("❌", "??"))

    if role not in member.roles:
        return await ctx.reply(embed=build_embed("⚠️", "Ce membre ne possède pas ce rôle"))
    try:
        await member.remove_roles(role, reason=f"Retiré par {ctx.author} via +rrole")
        return await ctx.reply(embed=build_embed("✅", f"**{role.name}** a été retiré de {member.mention}"))
    except discord.Forbidden:
        return await ctx.reply(embed=build_embed("❌", f"Permission refusée pour retirer ce rôle"))
    except discord.HTTPException as e:
        logs(f"Erreur HTTP dans rrole : {str(e)}")
        return await ctx.reply(embed=build_embed("❌", f"Une erreur est survenue"))


@rrole.error
async def rrole_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.reply(embed=build_embed("🦧", "Argument invalide Utilisation : +rrole @membre <role-id>"))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(embed=build_embed("🦧", "Utilisation : +rrole @membre <role-id>"))
    else:
        await ctx.reply(embed=build_embed("❌", "Une erreur est survenue."))

#   
                                        #   CONSEIL 



@bot.command()
async def derank(ctx, target: discord.Member):
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL] for role in ctx.author.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande"))
    role = ctx.guild.get_role(IDRANDOM)  
    try:
        await target.edit(roles=[role])
        await ctx.reply(embed=build_embed("✅", f"Tous les rôles de {target.mention} on été retirés"))
    except discord.Forbidden:
        await ctx.send(embed=build_embed("❌", "Je n’ai pas la permission"))
    except Exception as e:
        await ctx.send(embed=build_embed("❌", "Une erreur est survenue"))
        logs(f"Erreur lors du derank de {target.name}: {str(e)}")


@bot.command()
async def renew(ctx):
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL] for role in ctx.author.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande"))
    old_channel = ctx.channel
    try:
        new_channel = await old_channel.clone(reason=f"Renew par {ctx.author}", name=old_channel.name)
        await new_channel.edit(category=old_channel.category, position=old_channel.position)
        await new_channel.send(embed=build_embed("🔄", f"Salon recréé par {ctx.author.mention}"))
        await old_channel.delete(reason=f"Renew par {ctx.author}")
    except discord.Forbidden:
        await ctx.send(embed=build_embed("❌", f"Je n'ai pas les permissions nécessaires"))
    except discord.HTTPException as e:
        await ctx.send(embed=build_embed("❌", f" Une erreur s'est produite"))
        logs(f"Erreur lors du renouvellement du salon : {str(e)}")




@bot.command()
async def ban(ctx, user: Union[discord.Member, int, str] = None, *, reason=None):
    is_commandement = any(role.id == IDCOMMANDEMENT for role in ctx.author.roles)
    is_conseil = any(role.id == IDCONSEIL for role in ctx.author.roles)
    if not is_commandement and not is_conseil:
        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        return await ctx.reply(embed=embed)
    if user is None:
        embed = build_embed("⚠️", "Merci de mentionner un membre **ou** de fournir son **ID**")
        return await ctx.reply(embed=embed)
    try:
        if isinstance(user, discord.Member):
            commandement_role = ctx.guild.get_role(IDCOMMANDEMENT)
            if not commandement_role:
                embed = build_embed("⚠️", "Rôle commandement introuvable")
                return await ctx.reply(embed=embed)
            if user.top_role.position >= commandement_role.position:
                embed = build_embed("🚫", f"{user.mention} a un rôle **égal ou supérieur** à celui du COMMANDEMENT.\nBannissement interdit")
                return await ctx.reply(embed=embed)
            if user.top_role >= ctx.author.top_role :
                embed = build_embed("⛔", f"Tu ne peux pas bannir {user.mention}")
                return await ctx.reply(embed=embed)
            if user.top_role >= ctx.guild.me.top_role:
                embed = build_embed("⛔", f"Je ne peux pas bannir {user.mention} car son rôle est plus élevé que le mien.")
                return await ctx.reply(embed=embed)
            await user.ban(reason=reason)
            embed = build_embed("✅", f"{user.mention} a été banni\nRaison : {reason or 'Non spécifiée'}")
            return await ctx.reply(embed=embed)
        else:
            user_id = int(user)
            target = discord.Object(id=user_id)
            await ctx.guild.ban(target, reason=reason)
            embed = build_embed("✅", f"L'utilisateur avec l'ID `{user_id}` a été banni\nRaison : {reason or 'Non spécifiée'}")
            return await ctx.reply(embed=embed)
    except discord.NotFound:
        embed = build_embed("❌", "L'utilisateur n'existe pas ou n'a pas pu être trouvé")
        return await ctx.reply(embed=embed)
    except discord.Forbidden:
        embed = build_embed("⛔", "Permission refusée. Le bot ne peut pas bannir cet utilisateur")
        return await ctx.reply(embed=embed)
    except Exception as e:
        logs(f"⚠️ Erreur lors du bannissement : {str(e)}")
        embed = build_embed("⚠️", "Une erreur est survenue. Voir les logs")
        return await ctx.reply(embed=embed)


@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = build_embed("❌", "Argument invalide Utilisation : +ban @membre/<user-id> [raison]")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = build_embed("⚠️", "Utilisation correcte : +ban @membre | <user-id> [raison]")
        await ctx.reply(embed=embed)
    else:
        embed = build_embed("⚠️", "Une erreur est survenue lors de l'exécution de la commande")
        await ctx.reply(embed=embed)


@bot.command()
async def unban(ctx, user_id: int):
    if any(role.id == IDCOMMANDEMENT for role in ctx.author.roles) or any(role.id == IDCONSEIL for role in ctx.author.roles):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = build_embed("✅", f"{user} a été débanni")
            await ctx.reply(embed=embed)
        except discord.NotFound:
            embed = build_embed("❌", f"Aucun utilisateur avec cet ID n’est banni")
            await ctx.reply(embed=embed)
        except discord.Forbidden:
                    embed = build_embed("⛔", "permissions insuffisantes")
                    await ctx.send(embed=embed)
        except Exception as e:
            logs(f"❌ Une erreur est survenue : {e}")
            embed = build_embed("⚠️", "Erreur enreigstrée dans les logs")
            await ctx.send(embed=embed)
    else:
        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        await ctx.reply(embed=embed)

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = build_embed("❌", "L'argument fourni n'est pas un ID valide. Utilisation : +unban <user-id>")
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = build_embed("🦧", "Utilisation correcte : +unban <user-id>")
        await ctx.reply(embed=embed)
    else:
        embed = build_embed("⚠️", "Une erreur est survenue lors de l'exécution de la commande")
        await ctx.reply(embed=embed)



                                                        # COMMANDEMENT


@bot.command()
async def bl(ctx, member: discord.Member = None):
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL] for role in ctx.author.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande"))

    if member is None:
        if not blacklist:
            await ctx.reply(embed=build_embed("⚠️", "La blacklist est vide"))
            return
        
        embed = discord.Embed(title="📌 Liste des membres blacklistés", color=discord.Color.red())
        for user_id in blacklist:
            try:
                user = await bot.fetch_user(user_id)
                embed.add_field(name=str(user), value=f"ID: {user_id}", inline=False)
            except:
                embed.add_field(name="Utilisateur inconnu", value=f"ID: {user_id}", inline=False)
        await ctx.reply(embed=embed)
        return

    #
    commandement_role = ctx.guild.get_role(IDCOMMANDEMENT) 
    
    if member.top_role >= ctx.author.top_role:
        return await ctx.reply(embed=build_embed("⛔", f"il a un rôle égal ou supérieur au tien"))
    
    if member.top_role >= commandement_role:
        return await ctx.reply(embed=build_embed("⛔", f"{member.mention}, bon🦧"))

    if member.id in blacklist:
        return await ctx.reply(embed=build_embed("⚠️", f"{member} est déjà dans la blacklist"))


    blacklist.append(member.id)
    save_blacklist()
    await ctx.guild.ban(member, reason="Blacklist")
    await ctx.reply(embed=build_embed("🚫", f"{member} a été ajouté à la blacklist"))

@bot.command()
async def unbl(ctx, member: discord.User):
    if not any(role.id in [IDCOMMANDEMENT, IDCONSEIL] for role in ctx.author.roles):
        return await ctx.reply(embed=build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande"))
    if member.id not in blacklist:
        await ctx.reply(embed=build_embed("❌", f"{member} n'est pas dans la blacklist"))
        return
    blacklist.remove(member.id)
    save_blacklist()
    await ctx.send(embed=build_embed("✅", f"{member} a été retiré de la blacklist"))


@bot.command(name="massrole")
async def massrole(ctx, role_id: int):
    if ctx.author.id not in {1202243081076740246, 769344924000583721, 1369155425231962184}:

        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        await ctx.send(embed=embed)
        return

    role = ctx.guild.get_role(role_id)
    if not role:
        embed = build_embed("❌", "ID du rôle introuvable")
        await ctx.send(embed=embed)
        return
    
    if role_id is None or role_id <= 0:
        embed = build_embed("❌", "``+membrereload <id-role>``")
        await ctx.send(embed=embed)
        return

    count = 0
    for member in ctx.guild.members:

            try:
                await member.add_roles(role, reason="Rechargement des membres")
                count += 1
            except discord.Forbidden:
                embed = build_embed("⛔", "permissions insuffisantes")
                await ctx.send(embed=embed)
            except Exception as e:
                logs(f"⚠️ err  {member.display_name} : {str(e)}")
                embed = build_embed("⚠️", "Erreur")
                await ctx.send(embed=embed)

    await ctx.reply(embed=build_embed("✅", f"{count} membres ont reçu le rôle `{role.name}`"))
    count = None


@bot.command(name="membrereload")
async def membrereload(ctx, role_id: int):

    if ctx.author.id not in {1202243081076740246, 769344924000583721, 1369155425231962184}:

        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        await ctx.send(embed=embed)
        return

    role = ctx.guild.get_role(role_id)
    if not role:
        embed = build_embed("❌", "ID du rôle introuvable")
        await ctx.send(embed=embed)
        return
    
    if role_id is None or role_id <= 0:
        embed = build_embed("❌", "``+membrereload <id-role>``")
        await ctx.send(embed=embed)
        return

    count = 0
    for member in ctx.guild.members:
        if "0x" in member.display_name and role not in member.roles:
            try:
                await member.add_roles(role, reason="Rechargement des membres")
                count += 1
            except discord.Forbidden:
                embed = build_embed("⛔", "permissions insuffisantes")
                await ctx.send(embed=embed)
            except Exception as e:
                logs(f"⚠️ err  {member.display_name} : {str(e)}")
                embed = build_embed("⚠️", "Erreur")
                await ctx.send(embed=embed)

    await ctx.reply(embed=build_embed("✅", f"{count} membres ont reçu le rôle `{role.name}`"))
    count = None



@bot.command()
async def antibot(ctx, mode: str):
    if ctx.author.id not in {1202243081076740246, 769344924000583721, 1369155425231962184}:
        embed = build_embed("❌", "Tu n'as pas la permission d'utiliser cette commande")
        await ctx.reply(embed=embed)
        return
    
    if mode.lower() not in ["on", "off"]:
        return await ctx.reply(embed=build_embed("🦧", "Sa s'utilise comme ça : +antibot on ou +antibot off"))
        await ctx.send(embed=embed)
    
    antibot_status[ctx.guild.id] = mode.lower() == "on"
    await ctx.send(embed=build_embed("✅", f"Antibot est maintenant **{'activé' if mode == 'on' else 'désactivé'}**"))



bot.run(TOKEN)