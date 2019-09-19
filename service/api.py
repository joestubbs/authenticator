from flask_migrate import Migrate

from service.models import db, app

# db and migrations ----
db.init_app(app)
migrate = Migrate(app, db)
