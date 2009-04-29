#!/usr/bin/python
# -*- coding: utf-8 -*-

db = SQLDB ('sqlite://everule.db')

# Authentication infomation
db.define_table ('rules',
                       SQLField ('name'),
                       SQLField ('permission')
                       )

db.define_table ('users',
                       SQLField ('name'),
                       SQLField ('fullname'),
                       SQLField ('email', 'string', length=128),
                       SQLField ('rule', db.rules)
                       )

# Modules/Packages infomation
db.define_table ('modules',
                       SQLField ('name', 'string', length=64),
                       SQLField ('version'),
                       SQLField ('release'),
                       SQLField ('owner_id', db.users)
                       )

db.define_table ('packages',
                       SQLField ('module_id', db.modules),
                       SQLField ('name')
                       )

db.define_table ('tarballs',
                       SQLField ('name'),
                       SQLField ('suffix')
                       )

# upstream_uri: http://, ftp://, gnome://, kde://, and so on
db.define_table ('upstream_uries',
                       SQLField ('name'),
                       SQLField ('prefix'),
                       SQLField ('uri', 'text'),
                       SQLField ('predefined', 'boolean'), # for custom uri, e.g. gnome://...
                       )

db.define_table ('sources',
                       SQLField ('name', 'string', length=128),    # Diff from module name, glib for glib2, gtk+ for gtk2
                       SQLField ('mversion'),   # A part of version, 2.18 for 2.18.3
                       SQLField ('uri_type', db.upstream_uries),
                       SQLField ('uri', 'text'), # Download source
                       SQLField ('tarball_type', db.tarballs), 
                       SQLField ('module_id', db.modules),
                       SQLField ('gfwed', 'boolean'), # If gfwed, we must use proxy to access
                       SQLField ('auto_check_upstream', 'boolean'),
                       SQLField ('last_check_time', 'datetime')
                       )

db.define_table ('upstreamse',
                       SQLField ('module_id', db.modules),
                       SQLField ('source_id', db.sources),
                       SQLField ('version'),
                       SQLField ('uri', 'text'),
                       SQLField ('timestamp', 'datetime'),
                       SQLField ('status', comment='pending, downloading, downloaded')
                       )

db.users.name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'users.name')]

db.modules.name.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'modules.name')]
db.modules.version.requires = IS_NOT_EMPTY()

db.packages.name.requires = IS_NOT_EMPTY()

db.users.email.requires = [IS_EMAIL(), IS_NOT_IN_DB(db,'users.email')]
db.users.rule.requires = IS_IN_DB(db,'rules.id','rules.name')

db.modules.owner_id.requires = IS_IN_DB(db,'users.id','users.name')

db.packages.module_id.requires = IS_IN_DB(db,'modules.id','modules.name')

db.sources.module_id.requires = IS_IN_DB(db,'modules.id','modules.name')
db.sources.tarball_type.requires = IS_IN_DB(db,'tarballs.id','tarballs.name')
db.sources.uri_type.requires = IS_IN_DB(db,'upstream_uries.id','upstream_uries.name')

db.upstreamse.module_id.requires = IS_IN_DB(db,'modules.id','modules.name')
db.upstreamse.source_id.requires = IS_IN_DB(db,'sources.id','sources.name')
