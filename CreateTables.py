from BeeServer import db, app
from sqlalchemy import text

with app.app_context():
    # 1. Drop everything in public, cascading dependencies
    db.session.execute(text('DROP SCHEMA public CASCADE;'))
    db.session.execute(text('CREATE SCHEMA public;'))
    db.session.commit()

    # 2. Recreate tables from your models
    db.create_all()
    print("✅ Schema reset and tables recreated")



# with app.app_context():
#     db.drop_all()
#     db.create_all()
#     print("Tables created successfully.")