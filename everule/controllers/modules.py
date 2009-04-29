response.menu=[
                       ['Summary',False,URL(r=request,f='index')],
                       ['Add User',False,URL(r=request,f='add_user')],
                       ['Add Module',False,URL(r=request,f='add_module')],
                       ['Check Upstream',False,URL(r=request,f='check_upstream')]
                      ]

def get_pkgs_list (module):
    pkgs = []
    try:
        from applications.everule.modules.sh_utils import RPMModule
    except:
        pkgs.append ("Cann't import RPMModule")
    else:
        m = RPMModule (module)
        pkgs = m.get_packages_list () 
    
    return pkgs

def index():
    #rpms = get_pkgs_list ('glib2')
    #modules = SQLTABLE (db ().select (db.modules.ALL))
    #users = SQLTABLE (db ().select (db.users.ALL))
    #packages = SQLTABLE (db ().select (db.packages.ALL))
    #sources = SQLTABLE (db ().select (db.sources.ALL))
    #upstreamse = SQLTABLE (db ().select (db.upstreamse.ALL))
    
    query = (db.modules.owner_id == db.users.id)
    modules = db(query).select (db.modules.ALL,
                                          db.users.ALL)
    
    return dict (#rpms = rpms,
                    #users = users, 
                    modules = modules, 
                    #packages = packages,
                    #sources = sources,
                    #upstreamse = upstreamse
                    )

def add_source():
    if (len (request.args) == 0):
        redirect(URL(r=request,f='index'))
    
    mod = request.args[0]

    form = SQLFORM (db.sources)
    if form.accepts (request.vars, session):
        response.flash = 'New sources added!'
    sources = SQLTABLE (db ().select (db.sources.ALL))
    
    return dict (form = form, sources = sources)

def detail():
    if (len (request.args) == 0):
        redirect(URL(r=request,f='index'))
    
    mod = request.args[0]
        
    query = (db.modules.name == mod)
    results = db (query).select (db.modules.ALL)
    
    if (len(results) == 0):
        redirect(URL(r=request,f='index'))
    
    mod = results[0]
    
    #print "Module for detail %s" % mod
    
    module = mod
    query = (db.packages.module_id == mod['id'])
    packages = db (query).select (db.packages.ALL)

    query = (db.sources.module_id == mod['id'])
    sources = db (query).select (db.sources.ALL)

    # Mark modules for check upstream
    can_check_upstream = False
    for src in sources:
        if src['auto_check_upstream']:
            can_check_upstream = True
            break
    module['can_check_upstream'] = can_check_upstream

    query = (db.upstreamse.module_id == mod['id'])
    upstreamse = db (query).select (db.upstreamse.ALL)
    
    return dict (module = module,
                    packages = packages,
                    sources = sources,
                    upstreamse = upstreamse
                    )

def add_user():
    form = SQLFORM (db.users)
    if form.accepts (request.vars, session):
        response.flash = 'New user added!'
    users = SQLTABLE (db ().select (db.users.ALL))
    
    return dict (form = form, users = users)

def get_fsmodule_info():
    info = ""
    if len (request.args) == 0:
        return info
    
    mod = request.args[0]
    try:
        from applications.everule.modules.everest import evst_get_module_info
        info = evst_get_module_info (mod)
        #print info
    except:
        print "Cann't get fsmodule info for %s" % mod
    
    return info

def add_module():
    fsmods = []
    try:
        from applications.everule.modules.everest import evst_get_modules
        fsmods = evst_get_modules ()
    except:
        fsmods.append ("Cann't import RPMModule")

    form = SQLFORM (db.modules)
    if form.accepts (request.vars, session):
        response.flash = 'New module added!'
    modules = SQLTABLE (db ().select (db.modules.ALL))
    
    dbmods = db().select (db.modules.name)
    for m in dbmods:
        if m['name'] in fsmods:
            fsmods.remove(m['name'])
            #print "Remove %s from fsmods" % m['name']
    
    return dict (form = form, modules = modules, fsmods = fsmods)

def reload_module_packages():
    mid = -1
    mname = ""
    if len (request.args) > 0:
        rows = db(db.modules.name == request.args[0]).select() 
        if len (rows) > 0:
            mname = request.args[0]
            mid = rows[0]['id']
            print "Reload pkgs for %s, %s" % (mname, mid)
    else:
        redirect(URL(r=request, f='index'))
    
    pkgs = []
    try:
        from applications.everule.modules.everest import evst_get_module_packages
        pkgs = evst_get_module_packages (mname)
        print pkgs
    except:
        print "Cann't get packages for %s" % mname  
    rows = db(db.packages.module_id == mid).select()
    opkgs = []
    for r in rows:
        opkgs.append (r['name'])
    
    for p in pkgs:
        if p not in opkgs:
            db.packages.insert (module_id = mid, name = p)
    
    redirect(URL(r=request, f='detail', args=[mname]))

def check_upstream():
    uri=''
    upstreamse = []
    message = "Check for upstream..."
    
    query = (db.sources.auto_check_upstream == True) \
                & (db.sources.gfwed == False)
    check_for_module = False
    if len (request.args) > 0:
        rows = db(db.modules.name == request.args[0]).select() 
        if len (rows) > 0:
            mname = request.args[0]
            mid = rows[0]['id']
            print "Checking upstream for module: %s, id: %s" % (mname, mid)
            check_for_module = True
            query = query & (db.sources.module_id == mid)
    
    rows = db (query).select(db.sources.ALL)
    
    if len (rows) == 0 and check_for_module:
        redirect (URL(r=request, f='detail', args=[mname,]))
    
    for row in rows:
        mid = row ['module_id']
        query = (db.modules.id == row ['module_id']) \
                    & (db.tarballs.id == row['tarball_type'])
        mods = db(query).select(db.modules.version, db.tarballs.suffix)
        #print row
        #print mods[0]
        mod = mods[0]
        src = {}
        src['id'] = row['id']
        src['module_id'] = row['module_id']
        src['name'] = row['name']
        src['version'] = mod.modules.version
        src['mversion'] = row['mversion']
        src['tarball'] = mod.tarballs.suffix
        src['uri'] =  row['uri']
        
        # Check if is predefined URI
        query = (db.upstream_uries.id == row['uri_type'])
        uris = db (query).select (db.upstream_uries.ALL)
        uuri = uris[0]
        if (uuri.predefined == True):
            src['uri'] = uuri.uri
        #print src
        
        suri = None
        try:
            from applications.everule.modules.RPMSpec import SourceURI
            suri = SourceURI (src['uri'], src)
        except:
            message = T("Cann't import SourceURI")

        if suri:
            query = (db.upstreamse.source_id == src['id'])
            rows = db(query).select (db.upstreamse.version)
            exists_ups = []
            for row in rows:
                exists_ups.append (row['version'])
            upstreamse = suri.get_upstream (exists_ups)
            for up in upstreamse:
                db.upstreamse.insert (module_id = up['module_id'],
                                              source_id = up['source_id'],
                                              version = up['version'],
                                              uri = up['uri'],
                                              timestamp = up['timestamp'])
    if check_for_module:
        redirect (URL(r=request, f='detail', args=[mname,]))
    
    return dict (message=message, upstreamse = upstreamse)
