#!/usr/bin/env python

from sh_utils import RPMModule
from RPMSpec import *

m = RPMModule ('glib2')
print m.get_packages_list()

src = {}
src['name']='glib'
src['version']='2.18.3'
src['mversion']='2.18'
src['tarball']='tar.bz2'

uri = 'http://ftp.gnome.org/pub/GNOME/sources/%{name}/%{mversion}/%{name}-%{version}.%{tarball}'

suri = SourceURI('', src)
uri = suri.parse_uri (uri)

print uri
