# royal_court.py — Royal Court Administration Bot
# Admin-only commands for medieval realm management
import os
import random
import sqlite3
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import timedelta, datetime as dt, timezone
from discord.utils import utcnow

# ---------- ENV ----------
load_dotenv()
TOKEN  = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
DB_NAME = "royal_court.db"

# ---------- MEDIEVAL FLAIR ----------
MEDIEVAL_COLORS = {
    "gold": discord.Colour.gold(),
    "dark_gold": discord.Colour.dark_gold(),
    "red": discord.Colour.dark_red(),
    "green": discord.Colour.dark_green(),
    "blue": discord.Colour.dark_blue(),
    "purple": discord.Colour.purple(),
    "orange": discord.Colour.dark_orange(),
    "grey": discord.Colour.dark_grey(),
}

MEDIEVAL_PREFIXES = [
    "Hark!",
    "Verily,",
    "By mine honour,",
    "Prithee,",
    "Forsooth,",
    "By the King's decree,",
    "Hear ye, hear ye!",
    "Lo and behold,",
    "By mine troth,",
    "Marry,",
    "Gadzooks!",
    "Zounds!",
    "By the saints,",
    "By my halidom,",
    "In faith,",
    "By my beard,",
    "By the rood,",
    "Alack,",
    "Alas,",
    "Fie upon it!",
]

ROYAL_TITLES = [
    "Royal Decree from the Throne",
    "Proclamation of the Crown",
    "Edict from the Royal Court",
    "Mandate of the Sovereign",
    "Declaration from the Monarch",
    "Announcement from the Castle",
    "Word from the Keep",
    "Message from the Palace",
    "Command from the Regent",
    "Bull from the Pontiff",
]

ROYAL_SIGNATURES = [
    "By order of the Crown",
    "Sealed with the Royal Seal",
    "Witnessed by the Royal Scribe",
    "Proclaimed throughout the realm",
    "Let all subjects take heed",
    "Inscribed by the Court Chronicler",
    "Signed with royal blood",
    "Marked with the King's signet",
    "Carried by royal messenger",
    "Announced with trumpet blast",
]

def get_medieval_prefix():
    return random.choice(MEDIEVAL_PREFIXES)

def medieval_embed(title="", description="", color_name="gold"):
    """Create an embed with medieval styling"""
    color = MEDIEVAL_COLORS.get(color_name, MEDIEVAL_COLORS["gold"])
    embed = discord.Embed(
        title=f"⚔️  {title}" if title else None,
        description=description,
        colour=color
    )
    return embed

def medieval_response(message, success=True):
    """Create a medieval-style response message"""
    prefix = get_medieval_prefix()
    color = "green" if success else "red"

    full_message = f"{prefix} {message}".strip()

    return medieval_embed(description=full_message, color_name=color)

# ---------- BOT ----------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, case_insensitive=True)

# ---------- DB ----------
def init_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS punishments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            moderator_id INTEGER,
            action TEXT,
            reason TEXT,
            timestamp TEXT
        )""")
        db.execute("""
        CREATE TABLE IF NOT EXISTS guild_config (
            guild_id INTEGER PRIMARY KEY,
            pillory_channel INTEGER,
            decree_channel INTEGER
        )""")
        db.commit()

# ---------- PUNISHMENT LOG ----------
def log_action(user_id, moderator_id, action, reason):
    with sqlite3.connect(DB_NAME) as db:
        db.execute(
            "INSERT INTO punishments (user_id, moderator_id, action, reason, timestamp) VALUES (?,?,?,?,?)",
            (user_id, moderator_id, action, reason, utcnow().isoformat()))
        db.commit()

def fetch_history(user_id):
    with sqlite3.connect(DB_NAME) as db:
        cur = db.execute(
            "SELECT action, reason, timestamp FROM punishments WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
        return cur.fetchall()

def set_pillory_channel(guild_id, channel_id):
    with sqlite3.connect(DB_NAME) as db:
        db.execute("INSERT OR REPLACE INTO guild_config (guild_id, pillory_channel) VALUES (?,?)", (guild_id, channel_id))
        db.commit()

def get_pillory_channel(guild_id):
    with sqlite3.connect(DB_NAME) as db:
        row = db.execute("SELECT pillory_channel FROM guild_config WHERE guild_id=?", (guild_id,)).fetchone()
        return row[0] if row else None

def set_decree_channel(guild_id, channel_id):
    with sqlite3.connect(DB_NAME) as db:
        db.execute("INSERT OR REPLACE INTO guild_config (guild_id, decree_channel) VALUES (?,?)", (guild_id, channel_id))
        db.commit()

def get_decree_channel(guild_id):
    with sqlite3.connect(DB_NAME) as db:
        row = db.execute("SELECT decree_channel FROM guild_config WHERE guild_id=?", (guild_id,)).fetchone()
        return row[0] if row else None

def can_act_on(target: discord.Member, ctx):
    if target == ctx.guild.owner:
        return False, "The sovereign monarch may not be judged, noble sir."
    if target == ctx.guild.me:
        return False, "One may not pass sentence upon oneself, good sirrah."
    if ctx.guild.me.top_role <= target.top_role:
        return False, "The target beareth greater station than the Crown's agent, m'lord."
    return True, ""

# ---------- ROYAL COMMANDS ----------
@bot.command(name="help")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def _help(ctx):
    """Display royal commands"""
    cmds = {
        "purge": "Cleanse the hall of messages (1-100)",
        "banish": "Exile a soul forever from the realm",
        "castout": "Cast a peasant from the castle gates",
        "pillory": "Bind a wretch in public stocks",
        "stocks": "Mute a tongue with royal locks",
        "pardon": "Grant royal mercy to a soul",
        "summon": "Issue a royal summons to court",
        "chronicle": "Read the criminal records of a soul",
        "decree": "Proclaim a royal decree to a channel",
        "setpillory": "Set the pillory announcement hall",
        "setdecree": "Set the royal decree proclamation hall",
        "courtlog": "View all recent judgments in the realm"
    }

    embed = medieval_embed(
        title="📜 Royal Charter of Commands",
        description="**Hark!** Here be the royal commands for administering the realm:\n",
        color_name="gold"
    )

    for name, desc in cmds.items():
        embed.add_field(name=f"**{PREFIX}{name}**", value=f"*{desc}*", inline=False)

    embed.add_field(
        name="⚖️  Remember, noble lord:",
        value="These commands require the royal seal. Justice must be tempered with mercy.",
        inline=False
    )

    embed.set_footer(text=f"Royal Court of {ctx.guild.name}")

    await ctx.send(embed=embed)

# ---------- PURGE COMMAND ----------
@bot.command(aliases=['cleanse', 'sweep'])
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
async def purge(ctx, amount: int = 10):
    """Cleanse the hall of messages"""
    if amount < 1 or amount > 100:
        embed = medieval_response(
            "Thou mayest cleanse between 1 and 100 messages only, m'lord!",
            success=False
        )
        return await ctx.send(embed=embed)

    if not ctx.guild.me.guild_permissions.manage_messages:
        embed = medieval_response(
            "The Crown lacketh power to cleanse messages in this hall!",
            success=False
        )
        return await ctx.send(embed=embed)

    try:
        # Delete command message
        try:
            await ctx.message.delete()
        except:
            pass

        # Purge messages
        deleted = await ctx.channel.purge(limit=amount)

        if len(deleted) == 0:
            embed = medieval_response(
                "No messages could be cleansed! They may be older than a fortnight.",
                success=False
            )
            return await ctx.send(embed=embed, delete_after=5)

        log_action(ctx.author.id, ctx.author.id, "purge", f"Cleansed {len(deleted)} messages")

        purge_messages = [
            f"**{len(deleted)}** messages swept away like autumn leaves!",
            f"**{len(deleted)}** scrolls consigned to the flames!",
            f"**{len(deleted)}** whispers silenced by royal decree!",
            f"**{len(deleted)}** parchments torn and discarded!",
            f"The royal broom hath swept clean! **{len(deleted)}** messages removed!",
        ]

        embed = medieval_embed(
            description=f"🧹  {random.choice(purge_messages)}\n\n*By order of {ctx.author.mention}*",
            color_name="grey"
        )
        msg = await ctx.send(embed=embed, delete_after=5)

    except discord.Forbidden:
        embed = medieval_response(
            "The royal seal hath no power to cleanse here!",
            success=False
        )
        await ctx.send(embed=embed, delete_after=5)
    except discord.HTTPException:
        embed = medieval_response(
            "Messages older than a fortnight cannot be cleansed!",
            success=False
        )
        await ctx.send(embed=embed, delete_after=5)

# ---------- BANISH COMMAND ----------
@bot.command(aliases=['exile', 'ostracize'])
@commands.has_permissions(ban_members=True)
@commands.guild_only()
async def banish(ctx, member: discord.Member, *, reason: str = "By royal decree"):
    """Exile a soul forever from the realm"""
    if not ctx.guild.me.guild_permissions.ban_members:
        embed = medieval_response(
            "The Crown's herald lacketh the seal to banish souls from the realm!",
            success=False
        )
        return await ctx.send(embed=embed)

    ok, msg = can_act_on(member, ctx)
    if not ok:
        embed = medieval_response(msg, success=False)
        return await ctx.send(embed=embed)

    try:
        await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=0)
        log_action(member.id, ctx.author.id, "banish", reason)

        banish_messages = [
            f"**{member.display_name}** hath been banished beyond the realm's borders forever!",
            f"**{member.display_name}** is cast out, never to darken our gates again!",
            f"**{member.display_name}** is exiled from these lands for all eternity!",
            f"**{member.display_name}** is sent beyond the pale, banished by royal command!",
        ]

        embed = medieval_embed(
            title="🏴  ROYAL BANISHMENT",
            description=f"{random.choice(banish_messages)}\n\n**Crime:** {reason}\n**Judge:** {ctx.author.mention}",
            color_name="red"
        )
        embed.set_footer(text="Let this be a warning to all who would defy the Crown")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = medieval_response(
            "The gate guards refuse the writ of banishment!",
            success=False
        )
        await ctx.send(embed=embed)

# ---------- CASTOUT COMMAND ----------
@bot.command(aliases=['expel', 'eject'])
@commands.has_permissions(kick_members=True)
@commands.guild_only()
async def castout(ctx, member: discord.Member, *, reason: str = "Unfit for the court"):
    """Cast a peasant from the castle gates"""
    if not ctx.guild.me.guild_permissions.kick_members:
        embed = medieval_response(
            "The Crown lacketh the authority to cast out subjects!",
            success=False
        )
        return await ctx.send(embed=embed)

    ok, msg = can_act_on(member, ctx)
    if not ok:
        embed = medieval_response(msg, success=False)
        return await ctx.send(embed=embed)

    try:
        await member.kick(reason=f"{ctx.author}: {reason}")
        log_action(member.id, ctx.author.id, "castout", reason)

        kick_messages = [
            f"**{member.display_name}** hath been cast out beyond the castle gates!",
            f"**{member.display_name}** is shown the door of the keep!",
            f"**{member.display_name}** is expelled from the royal court!",
            f"**{member.display_name}** is tossed from the great hall!",
        ]

        embed = medieval_embed(
            title="🚪  CAST FROM COURT",
            description=f"{random.choice(kick_messages)}\n\n**Crime:** {reason}\n**Judge:** {ctx.author.mention}",
            color_name="orange"
        )
        embed.set_footer(text="May they learn humility beyond our walls")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = medieval_response(
            "The guards at the gate refuse to open them!",
            success=False
        )
        await ctx.send(embed=embed)

# ---------- PILLORY COMMAND ----------
@bot.command(aliases=['shame', 'humiliate'])
@commands.has_permissions(moderate_members=True)
@commands.guild_only()
async def pillory(ctx, member: discord.Member, minutes: int, *, reason: str = "Crimes against the Crown"):
    """Bind a wretch in public stocks"""
    if minutes <= 0 or minutes > 40320:
        embed = medieval_response(
            "Sentence must be between 1 minute and 4 weeks (40320 minutes), m'lord!",
            success=False
        )
        return await ctx.send(embed=embed)

    if not ctx.guild.me.guild_permissions.moderate_members:
        embed = medieval_response(
            "The Crown lacketh the chains to bind offenders!",
            success=False
        )
        return await ctx.send(embed=embed)

    ok, msg = can_act_on(member, ctx)
    if not ok:
        embed = medieval_response(msg, success=False)
        return await ctx.send(embed=embed)

    until = utcnow() + timedelta(minutes=minutes)

    # Medieval time descriptions
    if minutes < 60:
        time_desc = f"**{minutes}** minute{'s' if minutes != 1 else ''}"
    elif minutes < 1440:
        hours = minutes // 60
        time_desc = f"**{hours}** hour{'s' if hours != 1 else ''}"
    else:
        days = minutes // 1440
        time_desc = f"**{days}** day{'s' if days != 1 else ''}"

    try:
        await member.timeout(until, reason=f"{ctx.author}: {reason}")
    except discord.Forbidden:
        embed = medieval_response(
            "The sheriff refuseth to apply the stocks!",
            success=False
        )
        return await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = medieval_response(
            "The stocks' lock did break! Try anon, good sir!",
            success=False
        )
        return await ctx.send(embed=embed)

    log_action(member.id, ctx.author.id, "pillory", f"{minutes} minutes: {reason}")

    # Public shaming in pillory channel
    chan_id = get_pillory_channel(ctx.guild.id)
    if chan_id:
        chan = ctx.guild.get_channel(chan_id)
        if chan and chan.permissions_for(ctx.guild.me).send_messages:
            shame_messages = [
                f"**Hear ye!** {member.display_name} standeth in the pillory for {time_desc}!\n**Crime:** *{reason}*\nLet mockery rain upon them like arrows!",
                f"**Gather round!** {member.display_name} is bound for {time_desc}!\n**Offense:** *{reason}*\nPelt them with rotten vegetables!",
                f"**Attention all!** {member.display_name} faces public shame for {time_desc}!\n**Transgression:** *{reason}*\nLet laughter be their punishment!",
            ]
            await chan.send(random.choice(shame_messages))

    pillory_messages = [
        f"**{member.display_name}** hath been bound in the pillory for {time_desc}!",
        f"**{member.display_name}** is secured in the stocks for {time_desc}!",
        f"**{member.display_name}** faces public humiliation for {time_desc}!",
    ]

    embed = medieval_embed(
        title="🪓  PUBLIC PILLORY",
        description=f"{random.choice(pillory_messages)}\n\n**Crime:** {reason}\n**Judge:** {ctx.author.mention}\n**Until:** <t:{int(until.timestamp())}:R>",
        color_name="dark_gold"
    )
    embed.set_footer(text="Public shame is a powerful teacher")
    await ctx.send(embed=embed)

# ---------- STOCKS COMMAND ----------
@bot.command(aliases=['silence', 'mute'])
@commands.has_permissions(moderate_members=True)
@commands.guild_only()
async def stocks(ctx, member: discord.Member, minutes: int, *, reason: str = "Bound by royal order"):
    """Mute a tongue with royal locks"""
    if minutes <= 0 or minutes > 40320:
        embed = medieval_response(
            "Sentence must be 1-40320 minutes, noble sir!",
            success=False
        )
        return await ctx.send(embed=embed)

    if not ctx.guild.me.guild_permissions.moderate_members:
        embed = medieval_response(
            "The Crown lacketh the manacles to silence tongues!",
            success=False
        )
        return await ctx.send(embed=embed)

    ok, msg = can_act_on(member, ctx)
    if not ok:
        embed = medieval_response(msg, success=False)
        return await ctx.send(embed=embed)

    until = utcnow() + timedelta(minutes=minutes)

    # Time description
    if minutes < 60:
        time_desc = f"**{minutes}** minute{'s' if minutes != 1 else ''}"
    elif minutes < 1440:
        hours = minutes // 60
        time_desc = f"**{hours}** hour{'s' if hours != 1 else ''}"
    else:
        days = minutes // 1440
        time_desc = f"**{days}** day{'s' if days != 1 else ''}"

    try:
        await member.timeout(until, reason=f"{ctx.author}: {reason}")
        log_action(member.id, ctx.author.id, "stocks", f"{minutes} minutes: {reason}")

        stocks_messages = [
            f"**{member.display_name}** is locked in the stocks for {time_desc}!",
            f"**{member.display_name}** is silenced for {time_desc}!",
            f"**{member.display_name}**'s tongue is stilled for {time_desc}!",
        ]

        embed = medieval_embed(
            title="🔒  ROYAL SILENCE",
            description=f"{random.choice(stocks_messages)}\n\n**Reason:** {reason}\n**Judge:** {ctx.author.mention}\n**Until:** <t:{int(until.timestamp())}:R>",
            color_name="orange"
        )
        embed.set_footer(text="Silence breeds contemplation")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = medieval_response(
            "The sheriff refuseth to apply the lock!",
            success=False
        )
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = medieval_response(
            "The stocks did splinter! Try anon, m'lord!",
            success=False
        )
        await ctx.send(embed=embed)

# ---------- PARDON COMMAND ----------
@bot.command(aliases=['forgive', 'mercy'])
@commands.has_permissions(moderate_members=True)
@commands.guild_only()
async def pardon(ctx, member: discord.Member):
    """Grant royal mercy to a soul"""
    if not ctx.guild.me.guild_permissions.moderate_members:
        embed = medieval_response(
            "The Crown lacketh the key to grant pardons!",
            success=False
        )
        return await ctx.send(embed=embed)

    ok, msg = can_act_on(member, ctx)
    if not ok:
        embed = medieval_response(msg, success=False)
        return await ctx.send(embed=embed)

    try:
        await member.timeout(None, reason=f"Pardoned by {ctx.author}")
        log_action(member.id, ctx.author.id, "pardon", "Royal mercy granted")

        pardon_messages = [
            f"**{member.display_name}** hath been pardoned by the Crown!",
            f"**{member.display_name}** receives royal mercy!",
            f"**{member.display_name}** is granted clemency!",
            f"**{member.display_name}**'s sentence is lifted by royal grace!",
        ]

        embed = medieval_embed(
            title="🕊️  ROYAL PARDON",
            description=f"{random.choice(pardon_messages)}\n\n**Granted by:** {ctx.author.mention}",
            color_name="green"
        )
        embed.set_footer(text="Mercy is the mark of a true monarch")
        await ctx.send(embed=embed)
    except discord.Forbidden:
        embed = medieval_response(
            "The sheriff refuseth to turn the key!",
            success=False
        )
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = medieval_response(
            "The pardon scroll did tear! Try anon, good sir!",
            success=False
        )
        await ctx.send(embed=embed)

# ---------- SUMMON COMMAND ----------
@bot.command(aliases=['call', 'subpoena'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def summon(ctx, member: discord.Member, *, reason: str = "Summoned before the Crown"):
    """Issue a royal summons to court"""
    log_action(member.id, ctx.author.id, "summon", reason)

    summon_messages = [
        f"**{member.mention}** hath been summoned before the Crown!",
        f"**{member.mention}** is called to the royal court!",
        f"**{member.mention}** must answer the royal summons!",
        f"**{member.mention}** is commanded to appear before the throne!",
    ]

    embed = medieval_embed(
        title="📯  ROYAL SUMMONS",
        description=f"{random.choice(summon_messages)}\n\n**Reason:** {reason}\n**Issued by:** {ctx.author.mention}",
        color_name="gold"
    )
    embed.set_footer(text="Heed the call or face the consequences")
    await ctx.send(embed=embed)

# ---------- CHRONICLE COMMAND ----------
@bot.command(aliases=['record', 'dossier'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def chronicle(ctx, member: discord.Member):
    """Read the criminal records of a soul"""
    rows = fetch_history(member.id)
    if not rows:
        embed = medieval_response(
            f"{member.display_name} beareth no recorded misdeeds. A soul of pure virtue!",
            success=True
        )
        return await ctx.send(embed=embed)

    embed = medieval_embed(
        title=f"📜  Chronicle of {member.display_name}",
        description=f"**Recorded Transgressions:** {len(rows)}\n*Most recent judgments first:*",
        color_name="dark_gold"
    )

    for action, reason, ts in rows[:10]:  # Show 10 most recent
        # Format timestamp
        dt_obj = dt.fromisoformat(ts).replace(tzinfo=timezone.utc)
        time_ago = utcnow() - dt_obj

        if time_ago.days > 0:
            time_str = f"{time_ago.days} day{'s' if time_ago.days != 1 else ''} ago"
        elif time_ago.seconds > 3600:
            hours = time_ago.seconds // 3600
            time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            minutes = time_ago.seconds // 60
            time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        action_icons = {
            "banish": "🏴",
            "castout": "🚪",
            "pillory": "🪓",
            "stocks": "🔒",
            "pardon": "🕊️",
            "summon": "📯",
            "purge": "🧹",
            "decree": "📜"
        }

        icon = action_icons.get(action, "⚖️")

        # Medieval action descriptions
        action_descriptions = {
            "banish": "Banished from realm",
            "castout": "Cast from gates",
            "pillory": "Public pillory",
            "stocks": "Silenced in stocks",
            "pardon": "Royal pardon",
            "summon": "Royal summons",
            "purge": "Hall cleansed",
            "decree": "Royal decree"
        }

        action_desc = action_descriptions.get(action, action)

        embed.add_field(
            name=f"{icon} {action_desc} • {time_str}",
            value=f"**Judgment:** {reason}",
            inline=False
        )

    if len(rows) > 10:
        embed.set_footer(text=f"And {len(rows) - 10} more judgment{'s' if len(rows) - 10 != 1 else ''}...")
    else:
        severity = "A troublesome soul indeed!" if len(rows) > 5 else "Minor infractions only."
        embed.set_footer(text=severity)

    await ctx.send(embed=embed)

# ---------- COURTLOG COMMAND ----------
@bot.command(aliases=['judgments', 'recent'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def courtlog(ctx, limit: int = 10):
    """View all recent judgments in the realm"""
    if limit < 1 or limit > 25:
        embed = medieval_response(
            "Thou mayest view between 1 and 25 recent judgments!",
            success=False
        )
        return await ctx.send(embed=embed)

    with sqlite3.connect(DB_NAME) as db:
        rows = db.execute(
            "SELECT user_id, moderator_id, action, reason, timestamp FROM punishments ORDER BY timestamp DESC LIMIT ?",
            (limit,)).fetchall()

    if not rows:
        embed = medieval_response(
            "No judgments have been recorded in the royal chronicles!",
            success=True
        )
        return await ctx.send(embed=embed)

    embed = medieval_embed(
        title="⚖️  Recent Royal Judgments",
        description=f"**Last {len(rows)} judgments in the realm:**",
        color_name="blue"
    )

    for user_id, mod_id, action, reason, ts in rows:
        # Get member names
        member = ctx.guild.get_member(user_id)
        moderator = ctx.guild.get_member(mod_id)

        member_name = member.display_name if member else f"Unknown ({user_id})"
        mod_name = moderator.display_name if moderator else f"Unknown ({mod_id})"

        # Format time
        dt_obj = dt.fromisoformat(ts).replace(tzinfo=timezone.utc)
        time_str = f"<t:{int(dt_obj.timestamp())}:R>"

        action_icons = {
            "banish": "🏴",
            "castout": "🚪",
            "pillory": "🪓",
            "stocks": "🔒",
            "pardon": "🕊️",
            "summon": "📯",
            "purge": "🧹",
            "decree": "📜"
        }

        icon = action_icons.get(action, "⚖️")

        embed.add_field(
            name=f"{icon} {member_name}",
            value=f"**Action:** {action.title()}\n**By:** {mod_name}\n**Reason:** {reason[:100]}{'...' if len(reason) > 100 else ''}\n**When:** {time_str}",
            inline=False
        )

    embed.set_footer(text=f"Royal Court of {ctx.guild.name}")

    await ctx.send(embed=embed)

# ---------- DECREE COMMAND ----------
@bot.command(aliases=['proclaim', 'announce'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def decree(ctx, channel: discord.TextChannel = None, *, message: str = ""):
    """Proclaim a royal decree to a channel"""
    # If no channel specified, check for default decree channel
    if channel is None:
        decree_chan_id = get_decree_channel(ctx.guild.id)
        if decree_chan_id:
            channel = ctx.guild.get_channel(decree_chan_id)

        # If still no channel, use current channel
        if channel is None:
            channel = ctx.channel

        # If there's still no message, show usage
        if not message:
            embed = medieval_embed(
                title="📜  Royal Decree Command",
                description=f"**Usage:** `{PREFIX}decree [channel] <message>`\n\n**Examples:**\n`{PREFIX}decree Hear ye, the feast begins at sundown!`\n`{PREFIX}decree #announcements All subjects must attend court tomorrow!`\n`{PREFIX}decree The market square shall be closed for the royal procession!`",
                color_name="orange"
            )
            embed.set_footer(text="Use !setdecree to set a default decree hall")
            return await ctx.send(embed=embed)

    # Check if bot can send messages to the channel
    if not channel.permissions_for(ctx.guild.me).send_messages:
        embed = medieval_response(
            f"I cannot herald thy decree in {channel.mention}! The heralds are barred!",
            success=False
        )
        return await ctx.send(embed=embed)

    # Create the decree with maximum medieval flair
    title = random.choice(ROYAL_TITLES)
    signature = random.choice(ROYAL_SIGNATURES)

    # Medieval decree openings
    openings = [
        "**Hear ye, hear ye!**",
        "**Let it be known throughout the land that**",
        "**By royal command and sovereign will,**",
        "**Unto all loyal subjects of the realm,**",
        "**Thus spake the Crown from the highest tower:**",
        "**Be it proclaimed from castle to cottage that**",
        "**The word of the monarch rings clear:**",
        "**Let the trumpets sound and banners fly, for**",
    ]

    # Medieval decree closings
    closings = [
        "**So says the Crown!**",
        "**Let none dare oppose this decree!**",
        "**May all heed these words!**",
        "**By my royal authority!**",
        "**So shall it be, now and forever!**",
        "**Let this be law in all the land!**",
        "**He who obeys shall prosper!**",
        "**Signed and sealed!**",
    ]

    opening = random.choice(openings)
    closing = random.choice(closings)

    # Format the full decree
    full_message = f"{opening}\n\n{message}\n\n{closing}"

    # Create the royal embed
    embed = discord.Embed(
        title=f"📜  {title}",
        description=full_message,
        colour=discord.Colour.gold(),
        timestamp=utcnow()
    )

    # Add royal author field
    embed.set_author(
        name=f"Proclaimed by {ctx.author.display_name}, Herald of the Crown",
        icon_url=ctx.author.display_avatar.url
    )

    # Add royal footer with seal
    embed.set_footer(
        text=f"✨ {signature} • Royal Court of {ctx.guild.name}"
    )

    # Add a royal seal/thumbnail if possible
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    # Send the decree
    try:
        await channel.send(embed=embed)

        # Send confirmation to command user
        confirm_messages = [
            f"Thy decree hath been proclaimed in {channel.mention}!",
            f"The royal word echoes through {channel.mention}!",
            f"All in {channel.mention} shall hear thy decree!",
            f"Thy proclamation rings in {channel.mention}!",
        ]

        confirmation = medieval_response(
            random.choice(confirm_messages),
            success=True
        )
        await ctx.send(embed=confirmation, delete_after=5)

        # Log the action
        log_action(ctx.author.id, ctx.author.id, "decree", f"Proclaimed in {channel.name}: {message[:50]}...")

    except discord.Forbidden:
        embed = medieval_response(
            f"Could not send decree to {channel.mention}. The gates are barred!",
            success=False
        )
        await ctx.send(embed=embed)
    except discord.HTTPException:
        embed = medieval_response(
            "Failed to send the decree. The royal scribe's quill broke!",
            success=False
        )
        await ctx.send(embed=embed)

# ---------- SETPILLORY COMMAND ----------
@bot.command(aliases=['setshamehall'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setpillory(ctx, channel: discord.TextChannel):
    """Set the pillory announcement hall"""
    set_pillory_channel(ctx.guild.id, channel.id)
    embed = medieval_response(
        f"The pillory yard hath been raised in {channel.mention}. Let all who trespass beware!",
        success=True
    )
    await ctx.send(embed=embed)

# ---------- SETDECREE COMMAND ----------
@bot.command(aliases=['setannouncehall'])
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setdecree(ctx, channel: discord.TextChannel):
    """Set the royal decree proclamation hall"""
    set_decree_channel(ctx.guild.id, channel.id)
    embed = medieval_response(
        f"The royal decree hall hath been established in {channel.mention}. All proclamations shall echo there!",
        success=True
    )
    await ctx.send(embed=embed)

# ---------- ON READY ----------
@bot.event
async def on_ready():
    print(f'🏰  Royal Court Bot hath awakened as {bot.user} (ID: {bot.user.id})')
    print('⚖️  Ready to administer royal justice!')
    print('📜  Royal seals prepared and chronicles open!')
    print('------')

# ---------- ERROR HANDLER ----------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    # Medieval error messages
    error_messages = {
        commands.BadArgument: {
            "Member": "I know not of that soul in our realm. Use @mention or exact name, m'lord.",
            "TextChannel": "I know not of that hall. Use #channel or exact name.",
            "default": "Thy argument is flawed, noble sir. Check thy command usage."
        },
        commands.MissingPermissions: "🚫  Thou lacketh the royal seal for this command! Only the Crown's appointed may wield such power.",
        commands.NoPrivateMessage: "⚠️  Royal commands may not be issued in private chambers! The court must witness justice.",
        commands.MissingRequiredArgument: {
            "member": "Thou must name a subject for judgment, m'lord!",
            "minutes": "Thou must specify the duration of sentence!",
            "amount": "Thou must declare how many messages to cleanse!",
            "channel": "Thou must name a hall for the decree!",
            "default": "Thou hast forgotten a required argument in thy command!"
        }
    }

    # Find appropriate error message
    error_msg = None
    error_type = type(error)

    if error_type in error_messages:
        if error_type == commands.BadArgument:
            err_str = str(error)
            for key in error_messages[commands.BadArgument]:
                if key in err_str:
                    error_msg = error_messages[commands.BadArgument][key]
                    break
            if not error_msg:
                error_msg = error_messages[commands.BadArgument]["default"]

        elif error_type == commands.MissingRequiredArgument:
            param = str(error.param)
            for key in error_messages[commands.MissingRequiredArgument]:
                if key in param.lower():
                    error_msg = error_messages[commands.MissingRequiredArgument][key]
                    break
            if not error_msg:
                error_msg = error_messages[commands.MissingRequiredArgument]["default"]

        else:
            error_msg = error_messages[error_type]

    if error_msg:
        embed = medieval_response(error_msg, success=False)
        await ctx.send(embed=embed)
    else:
        embed = medieval_response(
            "An ill omen befell the royal scribes! The chronicles shall record this mishap.",
            success=False
        )
        await ctx.send(embed=embed)
        print("🏰  Unhandled error:", type(error).__name__, error)

# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    print("🏰  Initializing Royal Court Administration Bot...")
    print("⚖️  Preparing judgment systems...")
    print("📜  Loading royal chronicles...")
    print("🎭  All commands require the royal seal...")
    bot.run(TOKEN)
