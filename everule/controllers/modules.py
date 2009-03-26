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
    rpms = get_pkgs_list ('glib2')
    modules = SQLTABLE (db ().select (db.modules.ALL))
    users = SQLTABLE (db ().select (db.users.ALL))
    packages = SQLTABLE (db ().select (db.packages.ALL))
    sources = SQLTABLE (db ().select (db.sources.ALL))
    upstreames = SQLTABLE (db ().select (db.upstreames.ALL))
    
    return dict (rpms = rpms,
                    users = users, 
                    modules = modules, 
                    packages = packages,
                    sources = sources,
                    upstreames = upstreames)

def add_user():
    form = SQLFORM (db.users)
    if form.accepts (request.vars, session):
        response.flash = 'New user added!'
    users = SQLTABLE (db ().select (db.users.ALL))
    
    return dict (form = form, users = users)

def add_module():
    form = SQLFORM (db.modules)
    if form.accepts (request.vars, session):
        response.flash = 'New module added!'
    modules = SQLTABLE (db ().select (db.modules.ALL))
    
    return dict (form = form, modules = modules)

def check_upstream():
    uri=''
    
#    src = {}
#    src['name'] = 'glib'
#    src['version'] = '2.18.2'
#    src['mversion'] = '2.18'
#    src['tarball'] = 'tar.bz2'
#    src['uri'] =  'http://ftp.gnome.org/pub/GNOME/sources/%{name}/%{mversion}/%{name}-%{version}.%{tarball}'
    
    upstreams = []
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
            upstreams = suri.get_upstream ()
            for up in upstreams:
                query = (db.upstreames.source_id == up['source_id']) \
                            & (db.upstreames.version == up['version'])
                matches = db (query).select (db.upstreames.ALL)
                if (len (matches)) == 0:
                    db.upstreames.insert (module_id = up['module_id'],
                                                  source_id = up['source_id'],
                                                  version = up['version'],
                                                  uri = up['uri'],
                                                  timestamp = up['timestamp'])
    
    return dict (message=message, upstreames = upstreams)
