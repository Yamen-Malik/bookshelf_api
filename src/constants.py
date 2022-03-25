from os import getenv

ITEMS_PER_PAGE = 10

# Database
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST")
DB_NAME = "bookshelf_api"
DB_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Auth
CLIENT_ID = getenv("BOOKSHELF_API_CLINET_ID")
CLIENT_SECRET = getenv("BOOKSHELF_API_CLINET_SECRET")
AUTH0_DOMAIN = getenv("BOOKSHELF_API_DOMAIN")
ALGORITHMS = ['RS256']
API_AUDIENCE = "bookshelf_api"
CALLBACK_ENDPOINT = "callback"
REQUEST_TIMEOUT = 1
