import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import threading
from datetime import datetime

# ================= TOKENS =================
DISCORD_TOKEN = "PASTE_DISCORD_TOKEN"
TELEGRAM_TOKEN = "PASTE_TELEGRAM_TOKEN"

# ================= DATABASE =================
conn = sqlite3.connect("servers.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS joins (
    guild_id INTEGER,
    guild_name TEXT,
    joined_at TEXT
)
""")

conn.commit()

# ================= DISCORD BOT =================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_member_join(member):

    cursor.execute("""
    INSERT INTO joins (guild_id, guild_name, joined_at)
    VALUES (?, ?, ?)
    """, (
        member.guild.id,
        member.guild.name,
        datetime.utcnow().isoformat()
    ))

    conn.commit()

    print(f"📈 New join in {member.guild.name}")

# ================= TELEGRAM COMMAND =================
async def topservers(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("""
    SELECT guild_name, COUNT(*) as joins
    FROM joins
    GROUP BY guild_id
    ORDER BY joins DESC
    LIMIT 10
    """)

    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text("No join data yet.")
        return

    message = "🔥 Top Growing Servers\n\n"

    for i, row in enumerate(rows, start=1):
        message += f"{i}. {row[0]} — {row[1]} joins\n"

    await update.message.reply_text(message)

# ================= TELEGRAM START =================
def start_telegram():

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(
        CommandHandler("topservers", topservers)
    )

    print("✅ Telegram bot started")

    app.run_polling()

# ================= START BOTH BOTS =================
threading.Thread(target=start_telegram).start()

bot.run(DISCORD_TOKEN)