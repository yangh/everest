#!/usr/bin/env python

from sh_utils import RPMModule

m = RPMModule ('glib2')
print m.get_packages_list()

from RPMSpec import *

src = {}
src['name']='glib'
src['version']='2.18.3'
src['mversion']='2.18'
src['tarball']='tar.bz2'

uri = 'http://ftp.gnome.org/pub/GNOME/sources/%{name}/%{mversion}/%{name}-%{version}.%{tarball}'

suri = SourceURI('', src)
uri = suri.parse_uri (uri)

print uri

from everest import *
mods = evst_get_modules()
print mods

info = evst_get_module_info ('vte')
print info

info = evst_get_module_packages('vte')
print info
