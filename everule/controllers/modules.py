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

def detail():
    if (len (request.args) == 0):
        redirect(URL(r=request,f='index'))
    
    mod = request.args[0]
        
    query = (db.modules.name == mod)
    results = db (query).select (db.modules.ALL)
    
    if (len(results) == 0):
        redirect(URL(r=request,f='index'))
    
    mod = results[0]
    
    print "Module for detail %s" % mod
    
    module = mod
    query = (db.packages.module_id == mod['id'])
    packages = db (query).select (db.packages.ALL)

    query = (db.sources.module_id == mod['id'])
    sources = db (query).select (db.sources.ALL)

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
        #info = "vte,0.17.4,4"
        print info
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
        print "Check if %s in fsmods" % m['name']
        if m['name'] in fsmods:
            fsmods.remove(m['name'])
            print "Remove %s from fsmods" % m['name']
    
    return dict (form = form, modules = modules, fsmods = fsmods)

def check_upstream():
    uri=''
    
#    src = {}
#    src['name'] = 'glib'
#    src['version'] = '2.18.2'
#    src['mversion'] = '2.18'
#    src['tarball'] = 'tar.bz2'
#    src['uri'] =  'http://ftp.gnome.org/pub/GNOME/sources/%{name}/%{mversion}/%{name}-%{version}.%{tarball}'
    
    upstreamse = []
    message = "Check for upstream..."
    
    query = (db.sources.auto_check_upstream == True) \
                & (db.sources.gfwed == False)
    rows = db (query).select(db.sources.ALL)
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
            upstreamse = suri.get_upstream ()
            for up in upstreamse:
                query = (db.upstreamse.source_id == up['source_id']) \
                            & (db.upstreamse.version == up['version'])
                matches = db (query).select (db.upstreamse.ALL)
                if (len (matches)) == 0:
                    db.upstreamse.insert (module_id = up['module_id'],
                                                  source_id = up['source_id'],
                                                  version = up['version'],
                                                  uri = up['uri'],
                                                  timestamp = up['timestamp'])
    
    return dict (message=message, upstreamse = upstreamse)
