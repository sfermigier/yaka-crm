#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from config import Config
from yaka_crm import create_app, db


app = create_app(Config())
if len(sys.argv) > 1 and sys.argv[1] == 'debug':
  DEBUG = True
else:
  DEBUG = app.config.get('DEBUG', False)
PORT = app.config.get('PORT', 5000)

if DEBUG:
  from flask_debugtoolbar import DebugToolbarExtension
  toolbar = DebugToolbarExtension(app)

with app.app_context():
  db.create_all()
  # + load dummy data

print "starting with DEBUG =", DEBUG
for k, v in sorted(app.config.items()):
  print "%s: %s" % (k, v)

app.run(host="0.0.0.0", debug=DEBUG, port=PORT)
