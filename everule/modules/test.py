#!/usr/bin/env python

from sh_utils import RPMModule

m = RPMModule ('glib2')
print m.get_packages_list()

