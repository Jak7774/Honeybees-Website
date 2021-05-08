import os

db = os.system('heroku config:get DATABASE_URL -a bridgewaterbees')
print(db)