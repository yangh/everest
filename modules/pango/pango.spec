%define glib2_base_version 2.17.3
%define glib2_version %{glib2_base_version}-1
%define pkgconfig_version 0.12
%define freetype_version 2.1.3-3
%define fontconfig_version 2.0
%define cairo_version 1.7.6

Summary: System for layout and rendering of internationalized text
Name: pango
Version: 1.24.0
Release: 3
License: LGPL
Group: System Environment/Libraries
Source: http://ftp.gnome.org/pub/gnome/sources/pango/1.8/pango-%{version}.tar.bz2

URL: http://www.pango.org
BuildRoot: %{_tmppath}/pango-%{PACKAGE_VERSION}-root

# We need to prereq this so we can run pango-querymodules
Prereq: glib2 >= %{glib2_version}
Prereq: freetype >= %{freetype_version}
Requires(pre): libXrender, libX11, libXext, libXft
Requires: freetype >= %{freetype_version}
Requires: cairo >= %{cairo_version}
Requires: sed
BuildRequires: libtool >= 1.4.2-10
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: pkgconfig >= %{pkgconfig_version}
BuildRequires: freetype-devel >= %{freetype_version}
BuildRequires: fontconfig-devel >= %{fontconfig_version}
BuildRequires: libXrender-devel
BuildRequires: libX11-devel
BuildRequires: libXext-devel
BuildRequires: libXft-devel
BuildRequires: libXt-devel
BuildRequires: cairo-devel >= %{cairo_version}
Obsoletes: pango-gtkbeta, fribidi-gtkbeta

Patch1: pango-slighthint.patch
Patch2:	pango-mem-leak.patch
# Look for pango.modules in an arch-specific directory
#Patch5: pango-1.2.5-lib64.patch
Patch6: pango-1.10-simulate-bold-oblique-style.diff

%description
Pango is a system for layout and rendering of internationalized text.


%package devel
Summary: System for layout and rendering of internationalized text.
Group: Development/Libraries
Requires: pango = %{PACKAGE_VERSION}
Requires: libXrender-devel
Requires: libX11-devel
Requires: libXext-devel
Requires: libXft-devel
Requires: glib2-devel >= %{glib2_version}
Requires: freetype-devel >= %{freetype_version}
Requires: fontconfig-devel >= %{fontconfig_version}
Requires: cairo-devel >= %{cairo_version}
Obsoletes: fribidi-gtkbeta-devel, pango-gtkbeta-devel

%description devel
The pango-devel package includes the static libraries, header files,
and developer docs for the pango package.

Install pango-devel if you want to develop programs which will use
pango.

%prep
%setup -q -n pango-%{version}

#%patch1 -p1 -b .slighthint
#%patch2 -p1
#%patch5 -p1 -b .lib64
#%patch6 -p1
%build


%configure --disable-gtk-doc
make

%install
rm -rf $RPM_BUILD_ROOT

# Deriving /etc/pango/$host location
# NOTE: Duplicated below
#
# autoconf changes linux to linux-gnu
case "%{_host}" in
  *linux) host="%{_host}-gnu"
  ;;
  *) host="%{_host}"
  ;;
esac

# autoconf uses powerpc not ppc
host=`echo $host | sed "s/^ppc/powerpc/"`

# Make sure that the host value that is passed to the compile 
# is the same as the host that we're using in the spec file
#
compile_host=`grep 'host_triplet =' pango/Makefile | sed "s/.* = //"`

if test "x$compile_host" != "x$host" ; then
  echo 1>&2 "Host mismatch: compile='$compile_host', spec file='$host'" && exit 1
fi

%makeinstall

# Remove files that should not be packaged
rm $RPM_BUILD_ROOT%{_libdir}/pango/*/modules/*.la

PANGOXFT_SO=$RPM_BUILD_ROOT%{_libdir}/libpangoxft-1.0.so
if ! test -e $PANGOXFT_SO; then
        echo "$PANGOXFT_SO not found; did not build with Xft support?"
        ls $RPM_BUILD_ROOT%{_libdir}
        exit 1
fi      

# We need to have separate 32-bit and 64-bit pango-querymodules binaries
# for places where we have two copies of the Pango libraries installed.
# (we might have x86_64 and i686 packages on the same system, for example.)
case "$host" in
  alpha*|ia64*|powerpc64*|s390x*|x86_64*)
   mv $RPM_BUILD_ROOT%{_bindir}/pango-querymodules $RPM_BUILD_ROOT%{_bindir}/pango-querymodules-64
   ;;
  *)
   mv $RPM_BUILD_ROOT%{_bindir}/pango-querymodules $RPM_BUILD_ROOT%{_bindir}/pango-querymodules-32
   ;;
esac

rm $RPM_BUILD_ROOT%{_sysconfdir}/pango/pango.modules
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pango/$host
touch $RPM_BUILD_ROOT%{_sysconfdir}/pango/$host/pango.modules

#
# We need the substitution of $host so we use an external
# file list
#
echo %dir %{_sysconfdir}/pango/$host > modules.files
echo %ghost %{_sysconfdir}/pango/$host/pango.modules >> modules.files
rpmclean
%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig

# Deriving /etc/pango/$host location
#
# autoconf changes linux to linux-gnu
case "%{_host}" in
  *linux) host="%{_host}-gnu"
  ;;
  *) host="%{_host}"
  ;;
esac

# autoconf uses powerpc not ppc
host=`echo $host | sed "s/^ppc/powerpc/"`

case "$host" in
  alpha*|ia64*|powerpc64*|s390x*|x86_64*)
   %{_bindir}/pango-querymodules-64 > %{_sysconfdir}/pango/pango.modules
   ;;
  *)
   %{_bindir}/pango-querymodules-32 > %{_sysconfdir}/pango/pango.modules
   ;;
esac

%postun -p /sbin/ldconfig

%files -f modules.files
%defattr(-, root, root)
%doc README AUTHORS COPYING ChangeLog 
%doc examples/HELLO.utf8
%{_libdir}/libpango*-*.so.*
%{_bindir}/pango-querymodules*
%{_libdir}/pango
%{_mandir}/man1/*

%dir %{_sysconfdir}/pango
%config %{_sysconfdir}/pango/pangox.aliases


%files devel
%defattr(-, root, root)
%{_libdir}/libpango*.so
%{_libdir}/libpango*.la
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_bindir}/pango-view
/usr/share/gtk-doc/

%changelog
* Fri Mar 27 2008 Pengu1n
- New upstream 1.26.0

* Sun May 21 2006 Matthias Clasen <mclasen@redhat.com> - 1.13.1-3
- Add missing BuildRequires (#191958)

* Tue May 16 2006 Matthias Clasen <mclasen@redhat.com> - 1.13.1-2
- Update to 1.13.1

* Mon May  8 2006 Matthias Clasen <mclasen@redhat.com> - 1.13.0-1
- Update to 1.13.0

* Fri Apr  7 2006 Matthias Clasen <mclasen@redhat.com> - 1.12.1-2
- Update to 1.12.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 1.12.0-1
- Update to 1.12.0

* Sun Feb 26 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.99-1
- Update to 1.11.99

* Tue Feb 21 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.6-1
- Upate to 1.11.6
- Drop upstreamed patches

* Fri Feb 17 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.5-2
- Fix a crash in pango_split
- Hide some private API

* Mon Feb 11 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.5-1
- Update to 1.11.5

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.11.4-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.11.4-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb  6 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.4-1
- Update to 1.11.4

* Mon Jan 30 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.3-1
- Update to 1.11.3

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> - 1.11.2-1
- Update to 1.11.2

* Wed Dec 19 2005 Matthias Clasen <mclasen@redhat.com> - 1.11.1-2
- BuildRequire cairo-devel

* Wed Dec 14 2005 Matthias Clasen <mclasen@redhat.com> - 1.11.1-1
- Update to 1.11.1

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 30 2005 Matthias Clasen <mclasen@redhat.com> - 1.11.0-1
- Update to 1.11.0

* Tue Nov 29 2005 Matthias Clasen <mclasen@redhat.com> - 1.10.2-1
- Update to 1.10.2

* Sun Nov 13 2005 Jeremy Katz <katzj@redhat.com> - 1.10.1-6
- switch prereqs to modular X

* Fri Nov  4 2005 Matthias Clasen <mclasen@redhat.com> - 1.10.1-5
- Switch buildrequires to modular X.
- Don't install .la files for modules.

* Thu Oct 27 2005 Matthias Clasen <mclasen@redhat.com> - 1.10.1-2
- Bump the requirement for glib (#165928)

* Mon Oct  3 2005 Matthias Clasen <mclasen@redhat.com> - 1.10.1-1
- Newer upstream version
- Use the docs which are included in the tarball

* Wed Aug 17 2005 Owen Taylor <otaylor@redhat.com> - 1.10.0-1
- Upgrade to 1.10.0

* Mon Aug 15 2005 Kristian Høgsberg <krh@redhat.com> 1.9.1-2
- Patch out libpixman dependency.

* Thu Jul 28 2005 Owen Taylor <otaylor@redhat.com> 1.9.1-1
- Update to 1.9.1

* Tue Jun 21 2005 Matthias Clasen <mclasen@redhat.com> 
- Add a missing requires

* Tue Jun 21 2005 Matthias Clasen <mclasen@redhat.com> 1.9.0-1
- Update to 1.9.0
- Require cairo

* Fri Mar  4 2005 Owen Taylor <otaylor@redhat.com> - 1.8.1-1
- Update to 1.8.1

* Tue Dec 21 2004 Matthias Clasen <mclasen@redhat.com> - 1.8.0-1
- Version 1.8.0
- Drop unneeded patches and hacks

* Wed Oct 20 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-7
- Fix problem with pango_layout_get_attributes returning one too few items
  (Needed to fix problems mentioned in #135656, 
  http://bugzilla.gnome.org/show_bug.cgi?id=155912)

* Tue Oct 19 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-6
- Make Hangul and Kana not backspace-deletes-char (#135356)

* Tue Oct 19 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-5
- Fix problem in the last patch where we weren't getting the metrics from the 
  right font description (#136428, Steven Lawrance)

* Mon Oct 18 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-4
- Move place where we compute fontset metrics to fix problems with line 
  height in CJK locales (#131218)

* Mon Oct 11 2004 Colin Walters <walters@redhat.com> - 1.6.0-3
- BR xorg-x11-devel instead of XFree86-devel

* Mon Sep 20 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-2
- Add patch from CVS to fix display of U+3000 (#132203,  
  reported upstream by Suresh Chandrasekharan, Federic Zhang)

* Mon Sep 20 2004 Owen Taylor <otaylor@redhat.com> - 1.6.0-1
- Version 1.6.0
- Add patch from CVS to fix bitmap-fonts/no-hint problem (#129246)

* Wed Sep  8 2004 Jeremy Katz <katzj@redhat.com> - 1.5.2-3
- fix running of pango-query-modules to have necessary libraries available
  (#132052)

* Mon Aug 16 2004 Owen Taylor <otaylor@redhat.com> - 1.5.2-2
- Fix crashes with left-matra fixups (#129982, Jatin Nansi)

* Mon Aug  2 2004 Owen Taylor <otaylor@redhat.com> - 1.5.2-1
- Update to 1.5.2
- Fix ppc/powerpc confusion when creating query-modules binary (#128645)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Mar 17 2004 Owen Taylor <otaylor@redhat.com> 1.4.0-2
- Fix location for modules file on ppc/ppc64 (#114399)
- Make the spec file check to avoid further mismatches

* Wed Mar 17 2004 Alex Larsson <alexl@redhat.com> 1.4.0-1
- update to 1.4.0

* Wed Mar 10 2004 Mark McLoughlin <markmc@redhat.com> 1.3.6-1
- Update to 1.3.6
- Bump required glib2 to 2.3.1

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Mark McLoughlin <markmc@redhat.com> 1.3.5-1
- Update to 1.3.5

* Wed Feb 25 2004 Mark McLoughlin <markmc@redhat.com> 1.3.3-1
- Update to 1.3.3

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jan 23 2004 Jonathan Blandford <jrb@redhat.com> 1.3.2-1
- new version
- add man page

* Thu Dec 18 2003 Owen Taylor <otaylor@redhat.com> 1.2.5-4
- Deal with autoconf changing -linux to -linux-gnu (#112387)

* Mon Dec  8 2003 Owen Taylor <otaylor@redhat.com> 1.2.5-3.0
- Package pango-querymodules as pango-querymodules-{32,64}; look for 
  pango.modules in an architecture-specific directory.
  (Fixes #111511, Justin M. Forbes)

* Mon Sep  8 2003 Owen Taylor <otaylor@redhat.com> 1.2.5-2.0
- Fix problem with corrupt Thai shaper

* Wed Aug 27 2003 Owen Taylor <otaylor@redhat.com> 1.2.5-1.1
- Version 1.2.5

* Tue Aug 26 2003 Owen Taylor <otaylor@redhat.com> 1.2.4-1.1
- Version 1.2.4

* Tue Jul  8 2003 Owen Taylor <otaylor@redhat.com> 1.2.3-2.0
- Bump for rebuild

* Mon Jun  9 2003 Owen Taylor <otaylor@redhat.com>
- Version 1.2.3

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun  2 2003 Owen Taylor <otaylor@redhat.com>
- Use the right version-1.2.2 tarball

* Thu May 29 2003 Owen Taylor <otaylor@redhat.com>
- Version 1.2.2

* Thu Feb 13 2003 Tim Powers <timp@redhat.com> 1.2.1-3
- remove deps on Xft and Xft-devel since XFree86 no longer has the
  virtual prvodes. Instead, require XFree86-devel > 4.2.99

* Tue Feb 11 2003 Owen Taylor <otaylor@redhat.com>
- Fix problem where language tag wasn't causing relookup of font (#84034)

* Sun Feb  2 2003 Owen Taylor <otaylor@redhat.com>
- Version 1.2.1

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 14 2003 Owen Taylor <otaylor@redhat.com>
- Patch from CVS to synthesize GDEF tables for fonts
  without them, like the Kacst fonts in fonts-arabic

* Thu Jan  9 2003 Owen Taylor <otaylor@redhat.com>
- Make requires freetype, not freetype-devel (#81423)

* Tue Jan  7 2003 Owen Taylor <otaylor@redhat.com>
- Update slighthint patch for freetype-2.1.3 (#81125)

* Fri Dec 20 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.2.0

* Mon Dec 16 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.1.6

* Wed Dec 11 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.1.5

* Tue Dec  3 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.1.4

* Thu Nov 21 2002 Havoc Pennington <hp@redhat.com>
- change PKG_CONFIG_PATH hack to also search /usr/X11R6/lib64/pkgconfig

* Wed Nov 20 2002 Havoc Pennington <hp@redhat.com>
- explicitly require pangoxft to be built, so we catch situations such
  as xft.pc moving to /usr/X11R6
- also add /usr/X11R6/lib/pkgconfig to PKG_CONFIG_PATH as a temporary 
  hack

* Thu Nov  7 2002 Havoc Pennington <hp@redhat.com>
- 1.1.3

* Thu Oct 31 2002 Owen Taylor <otaylor@redhat.com> 1.1.1-5
- Require the necessary freetype version, don't just
  BuildRequires it (#74744)

* Thu Oct 31 2002 Owen Taylor <otaylor@redhat.com> 1.1.1-4
- Own /etc/pango (#73962, Enrico Scholz)
- Remove .la files from the build root

* Mon Oct  7 2002 Havoc Pennington <hp@redhat.com>
- require glib 2.0.6-3, try rebuild on more arches

* Wed Aug 21 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.1.1 (main change, fixes font selection for FT2 backend, 
  as in gdmgreeter)

* Thu Aug 15 2002 Owen Taylor <otaylor@redhat.com>
- Fix linked list manipulation problem that was causing hang for anaconda
- Fix warning from loading mini-fonts with context == NULL

* Wed Aug 14 2002 Owen Taylor <otaylor@redhat.com>
- Fix major memory leak in the last patch

* Tue Aug 13 2002 Owen Taylor <otaylor@redhat.com>
- Actually use language tags at the rendering layer (should fix #68211)

* Mon Jul 15 2002 Owen Taylor <otaylor@redhat.com>
- Remove fixed-ltmain.sh, relibtoolize; to fix relink problems without 
- Fix bug causing hex boxes to be misrendered
  leaving RPATH (#66005)
- For FT2 backend, supply FT_LOAD_NO_BITMAP to avoid problems with 
  fonts with embedded bitmaps (#67851)

* Mon Jul  8 2002 Owen Taylor <otaylor@redhat.com>
- Make basic-x shaper work with our big-5 fonts

* Wed Jul  3 2002 Owen Taylor <otaylor@redhat.com>
- New upstream tarball with hooks for change-on-the fly font rendering

* Tue Jun 25 2002 Owen Taylor <otaylor@redhat.com>
- Up FreeType version to deal with FreeType-2.0.x / 2.1.x \
  ABI changes for pango's OpenType code.

* Mon Jun 24 2002 Owen Taylor <otaylor@redhat.com>
- Add some Korean aliases that the installer wants

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sat Jun  8 2002 Havoc Pennington <hp@redhat.com>
- devel package requires fontconfig/Xft devel packages

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Thu Jun  6 2002 Owen Taylor <otaylor@redhat.com>
- Snapshot with Xft2/fontconfig support

* Wed May 29 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.0.2
- Patch for charmaps problem

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed May 22 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed May 22 2002 Havoc Pennington <hp@redhat.com>
- add patch to adjust to newer version of freetype

* Wed Apr  3 2002 Alex Larsson <alexl@redhat.com>
- Update to version 1.0.1, remove patch

* Tue Mar 19 2002 Owen Taylor <otaylor@redhat.com>
- Patch from CVS for big speedup with FreeType-2.0.9

* Mon Mar 11 2002 Owen Taylor <otaylor@redhat.com>
- Rebuild

* Fri Mar  8 2002 Owen Taylor <otaylor@redhat.com>
- Version 1.0.0

* Mon Feb 25 2002 Alex Larsson <alexl@redhat.com>
- Update to 0.26

* Thu Feb 21 2002 Alex Larsson <alexl@redhat.com>
- Bump for rebuild

* Mon Feb 18 2002 Alex Larsson <alexl@redhat.com>
- Update to 0.25

* Fri Feb 15 2002 Havoc Pennington <hp@redhat.com>
- add horrible buildrequires hack

* Thu Feb 14 2002 Havoc Pennington <hp@redhat.com>
- 0.24.90 cvs snap

* Tue Jan 29 2002 Owen Taylor <otaylor@redhat.com>
- Version 0.24

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jan  2 2002 Havoc Pennington <hp@redhat.com>
- new snap 0.23.90

* Sun Nov 25 2001 Havoc Pennington <hp@redhat.com>
- rebuild with 64-bit-fixed glib

* Sun Nov 25 2001 Havoc Pennington <hp@redhat.com>
- Version 0.22
- add explicit check for required glib2 version before we do the build,
  so we don't end up with bad RPMs on --nodeps builds
- PreReq the glib2_version version, instead of 1.3.8 hardcoded that 
  no one had updated recently

* Thu Oct 25 2001 Owen Taylor <otaylor@redhat.com>
- Version 0.21

* Thu Oct  4 2001 Havoc Pennington <hp@redhat.com>
- cvs snap
- new cvs snap with a bugfix

* Thu Sep 27 2001 Havoc Pennington <hp@redhat.com>
- sync with Owen's changes, fix up dependency versions

* Wed Sep 19 2001 Havoc Pennington <hp@redhat.com>
- 0.19

* Mon Sep 10 2001 Havoc Pennington <hp@redhat.com>
- build CVS snap

* Wed Sep 05 2001 Havoc Pennington <hp@redhat.com>
- no relinking junk

* Tue Sep  4 2001 root <root@dhcpd37.meridian.redhat.com>
- Version 0.18

* Fri Jul 20 2001 Owen Taylor <otaylor@redhat.com>
- Configure --disable-gtk-doc
- BuildRequires freetype-devel, XFree86-devel

* Tue Jun 12 2001 Havoc Pennington <hp@redhat.com>
- 0.17
- libtool hackarounds

* Fri May 04 2001 Owen Taylor <otaylor@redhat.com>
- 0.16, rename back to pango from pango-gtkbeta

* Fri Feb 16 2001 Owen Taylor <otaylor@redhat.com>
- Obsolete fribidi-gtkbeta

* Mon Dec 11 2000 Havoc Pennington <hp@redhat.com>
- Remove that patch I just put in

* Mon Dec 11 2000 Havoc Pennington <hp@redhat.com>
- Patch pangox.pc.in to include -Iincludedir

* Fri Nov 17 2000 Owen Taylor <otaylor@redhat.com>
- final 0.13

* Tue Nov 14 2000 Owen Taylor <otaylor@redhat.com>
- New 0.13 tarball

* Mon Nov 13 2000 Owen Taylor <otaylor@redhat.com>
- 0.13pre1

* Sun Aug 13 2000 Owen Taylor <otaylor@redhat.com>
- Rename to 0.12b to avoid versioning problems

* Thu Aug 10 2000 Havoc Pennington <hp@redhat.com>
- Move to a CVS snapshot

* Fri Jul 07 2000 Owen Taylor <otaylor@redhat.com>
- Move back to /usr
- Version 0.12

* Mon Jun 19 2000  Owen Taylor <otaylor@redhat.com>
- Add missing %%defattr

* Thu Jun 8 2000  Owen Taylor <otaylor@redhat.com>
- Rebuild with a prefix of /opt/gtk-beta

* Wed May 31 2000 Owen Taylor <otaylor@redhat.com>
- version 0.11
- add --without-qt

* Wed Apr 26 2000 Owen Taylor <otaylor@redhat.com>
- Make the devel package require *-gtkbeta-* not the normal packages.

* Tue Apr 25 2000 Owen Taylor <otaylor@redhat.com>
- GTK+ snapshot version installing in /opt/gtk-beta

* Fri Feb 11 2000 Owen Taylor <otaylor@redhat.com>
- Created spec file
