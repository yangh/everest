# try something like

from applications.everule.modules.everest import *

def index(): return dict(message="hello from everulecron.py")

def wget_it (uri):
    import os
    
    sdir = evst_get_source_path()
    filename = uri.split("/")[-1]

    logpath = sdir + "/wget.log"
    cmd = "wget -b -c "
    cmd += " -a " + logpath
    cmd += " -O " + sdir + filename + " " + uri + " >/dev/null 2>&1"
    print cmd
    ret = os.system(cmd)

    return ret

def download_upstream():
    query = (db.upstreamse.status == 'pending')
    rows = db(query).select(db.upstreamse.ALL)
    
    uris = []
    log = open('/tmp/download.log', 'aw')
    log.write('Start download...\n')
    for row in rows:
        uri = row['uri']
        id = row['id']
        print "Start download:[%d] %s" % (id, uri)
        ret = wget_it (uri)
        if ret == 0:
            print "Update status..."
            db.upstreamse[id] = dict (status='downloading')
         
        log.write (uri + '\n')
        uris.append (uri)
    
    log.close()
    
    return dict (uris = uris)
