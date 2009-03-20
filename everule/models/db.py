#!/usr/bin/python
# -*- coding: utf-8 -*-

db = SQLDB ('sqlite://everule.db')

# Authentication infomation
db.define_table ('rules',
                       SQLField ('name'),
                       SQLField ('permission'))

db.define_table ('users',
                       SQLField ('name'),
                       SQLField ('fullname'),
                       SQLField ('email'),
                       SQLField ('rule', db.rules))

# Modules/Packages infomation
db.define_table ('modules',
                       SQLField ('name'),
                       SQLField ('version'),
                       SQLField ('release'),
                       SQLField ('owner_id', db.users))

db.define_table ('packages',
                       SQLField ('module_id', db.modules),
                       SQLField ('name'))

db.users.name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'users.name')]
db.modules.name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'modules.name')]
db.modules.version.requires = IS_NOT_EMPTY()
db.packages.name.requires = IS_NOT_EMPTY()

db.users.email.requires = [IS_EMAIL(), IS_NOT_IN_DB(db,'users.email')]
db.users.rule.requires = IS_IN_DB(db,'rules.id','rules.name')
db.modules.owner_id.requires = IS_IN_DB(db,'users.id','users.name')
db.packages.module_id.requires = IS_IN_DB(db,'modules.id','modules.name')
