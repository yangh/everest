import os

try:
    from config import EverestHome
except:
    print "Cann't for define of 'EverestHome'"
    EverestHome = '/Everest'

def evst_get_modules ():
    mods = []
    mdir = EverestHome + '/modules'
    print mdir
    for f in os.listdir (mdir):
        dir = mdir + '/' + f
        if os.path.isdir (dir) and os.access (dir + '/' + f + '.spec', os.F_OK) :
            mods.append (f)
    
    return mods

def evst_get_module_path ():
    return EverestHome + "/modules/"

def evst_get_module_info (fsmod = None):
    info = ""
    if fsmod is None:
        return info
    
    spec = EverestHome + "/modules/" + fsmod + "/" + fsmod + ".spec"
    if os.access(spec, os.F_OK) == False:
        return info
    
    cmd = "rpm -q --qf '%{name},%{version},%{release}\n' --specfile " + "%s" % spec
    ret = os.popen (cmd)
    lines = ret.readlines()
    
    return lines[0]
