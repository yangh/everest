%define libdir /%{_lib}

Summary: A library of handy utility functions
Name: glib2
Version: 2.20.0
Release: 1 
License: LGPL
Group: System Environment/Libraries
Source: glib-%{version}.tar.bz2
Source2: glib2.sh
Source3: glib2.csh
Patch0: glib-2.11.1-libdir.patch
Patch1: get_type_G_GNUC_IDEMPOTENT.patch
Patch2: glib-2.16-improve-compatibility.patch
Conflicts: libgnomeui <= 2.2.0
BuildRoot: %{_tmppath}/glib-%{PACKAGE_VERSION}-root
BuildRequires: pkgconfig >= 0.8
BuildRequires: gettext
Obsoletes: glib-gtkbeta
URL: http://www.gtk.org

%description 
GLib is the low-level core library that forms the basis
for projects such as GTK+ and GNOME. It provides data structure
handling for C, portability wrappers, and interfaces for such runtime
functionality as an event loop, threads, dynamic loading, and an 
object system.

This package provides version 2 of GLib.

%package devel
Summary: The GIMP ToolKit (GTK+) and GIMP Drawing Kit (GDK) support library
Group: Development/Libraries
Obsoletes: glib-gtkbeta-devel
Requires: pkgconfig >= 1:0.8
Requires: %{name} = %{version}-%{release}
Conflicts: glib-devel <= 1:1.2.8

%description devel
The glib2-devel package includes the header files for 
version 2 of the GLib library. 

%prep
%setup -q -n glib-%{version}
#%patch0 -p1 -b .libdir
%patch1 -p0
%build

for i in config.guess config.sub ; do
	test -f /usr/share/libtool/$i && cp /usr/share/libtool/$i .
done
./configure --prefix=/usr --sysconfdir=/etc --mandir=/usr/share/man --disable-gtk-doc --enable-static
make
%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

## glib2.sh and glib2.csh
./mkinstalldirs $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
install -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
install -m 755 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/profile.d

rpmclean

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files 
%defattr(-, root, root)

%doc AUTHORS COPYING ChangeLog NEWS README
%{_libdir}/libglib-2.0.so.*
%{_libdir}/libgthread-2.0.so.*
%{_libdir}/libgmodule-2.0.so.*
%{_libdir}/libgobject-2.0.so.*
%{_libdir}/libgio-2.0.so.*
/usr/lib/gio/modules/*
%{_sysconfdir}/profile.d/*
/usr/share/locale
%files devel
%defattr(-, root, root)

%{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_libdir}/lib*.a
%{_libdir}/glib-2.0
%{_includedir}/*
%{_datadir}/aclocal/*
%{_datadir}/gtk-doc/
%{_libdir}/pkgconfig/*
%{_datadir}/glib-2.0
%{_bindir}/*
%{_mandir}/man1/*

%changelog
* Mon Sep 17 2007 Cjacker <cjacker@gmail.com>
- update to 2.14.1
* Mon Jul 30 2007 Cjacker <cjacker@gmail.com>
- prepare for 0.5
