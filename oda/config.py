from os import getenv

from dotenv import load_dotenv

load_dotenv()

que = {}
admins = {}
SESSION_NAME = getenv("SESSION_NAME", "AQBQOVJ7tZDKn6rnttdAr9VJbyofWn7frQOQ3h8jFB1L8184r6uHM4xtIsboWAEWeiQWyBEM22oxu6a2fdbWfkB9Xs356bmphmKm9ZpExpzw1le7jIC7NSh458pyXw1C1M6jEbbG8Be6RU1eEHTm5sbfr3sEBzEM2391VBRGBtRnZJL5WFxk5Uwwzj5wEQDryQ1s44ZrbBswO57tte1DVxAZNZtSopuKcuLmaKC5iY-Dz2noolDrKK263EiLRyWUJDn1d88w4nK3i0lC6vpCuRJ3BSymMmDjIrsObppqOZ8mauRYw-FWe0Bme9Oogh9ZkPhu50P5dqjb50-cjhomf7AOaef2EAA")
BOT_TOKEN = getenv("BOT_TOKEN", "2078085167:AAGv4wJHNXWO7wGioM4PZgg8kJIGZn9FAbk")
BOT_NAME = getenv("BOT_NAME", "IGRISX")
BOT_USERNAME = getenv("BOT_USERNAME", "IGRISX_ROBOT")
ASSID = 2078085167
ASSNAME = "IGRISXMUSIC"
ASSUSERNAME = getenv("ASSUSERNAME", "IGRISXMUSIC")
BOT_ID = 2078085167
UPSTREAM_REPO = getenv("UPSTREAM_REPO")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://godlike:godlike@cluster0.c9aeb.mongodb.net/cluster0?retryWrites=true&w=majority")
API_ID = 6185076
API_HASH = getenv("API_HASH", "3e00f0be9697fec9b99501a367b7ff29")
OWNER_ID = int(getenv("OWNER_ID"))
UPDATE = getenv("UPDATE", "IGRISXUPDATES")
SUPPORT = getenv("SUPPORT", "IGRISROBOTSUPPORT")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "10"))
CMD_MUSIC = list(getenv("CMD_MUSIC", "/ !").split())
BG_IMG = "https://telegra.ph/file/79861c65fd1b2b8d0c09c.jpg"
SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))
