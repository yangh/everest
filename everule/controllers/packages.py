response.menu=[
                       ['Summary',False,URL(r=request,f='index')],
                       ['Add User',False,URL(r=request,f='add_user')],
                       ['Add Module',False,URL(r=request,f='add_module')]
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
    pkgs = get_pkgs_list ('glib2')
    modules = SQLTABLE (db ().select (db.modules.ALL))
    users = SQLTABLE (db ().select (db.users.ALL))
    
    return dict(users = users, modules = modules, packages = pkgs)

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
