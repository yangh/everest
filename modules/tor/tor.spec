%define toruser tor
%define torgroup tor
%define native_version      0.2.0.33
%define version %(echo %{native_version} | sed -e 's/-/./g')
%define release 4 

Name: tor
Version: %{version}
Release: %{release}

Summary: Anonymizing overlay network for TCP (The onion router)
URL: http://tor.eff.org/
Group: System Environment/Daemons

License: BSD-like
Vendor: R. Dingledine <arma@seul.org>
Packager: Nick Mathewson <nickm@seul.org>

Requires: openssl >= 0.9.6, libevent >= 1.1a
BuildRequires: openssl-devel >= 0.9.6, libevent-devel >= 1.1a
Requires(pre): /usr/bin/id, /bin/date, /bin/sh
Requires(pre): %{_sbindir}/useradd, %{_sbindir}/groupadd
Requires: privoxy
Source0: http://tor.eff.org/dist/%{name}-%{native_version}.tar.gz
Source1: tor.init
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Tor is a connection-based low-latency anonymous communication system.

This package provides the "tor" program, which serves as both a client and
a relay node. Scripts will automatically create a "%{toruser}" user and
a "%{torgroup}" group, and set tor up to run as a daemon when the system
is rebooted.

Applications connect to the local Tor proxy using the SOCKS
protocol. The local proxy chooses a path through a set of relays, in
which each relay knows its predecessor and successor, but no
others. Traffic flowing down the circuit is unwrapped by a symmetric
key at each relay, which reveals the downstream relay.


%prep
%setup -q -n %{name}-%{native_version}

%build
%configure --with-tor-user=%{toruser} --with-tor-group=%{torgroup}
make

%install
%makeinstall

# Install init script and control script
%__mkdir_p ${RPM_BUILD_ROOT}%{_initrddir}
%__install -p -m 755 %{SOURCE1} ${RPM_BUILD_ROOT}%{_initrddir}/%{name}
%__install -p -m 755 contrib/torctl ${RPM_BUILD_ROOT}%{_bindir}

# Set up config file; "sample" file implements a basic user node.
%__install -p -m 644 ${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/torrc.sample ${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/torrc

# Install the logrotate control file.
%__mkdir_p -m 755 ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
%__install -p -m 644 contrib/tor.logrotate ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}

# Directories that don't have any preinstalled files
%__mkdir_p -m 700 ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{name}
%__mkdir_p -m 755 ${RPM_BUILD_ROOT}%{_localstatedir}/run/%{name}
%__mkdir_p -m 755 ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}

%clean
[ "${RPM_BUILD_ROOT}" != "/" ] && rm -rf ${RPM_BUILD_ROOT}

# These scripts are probably wrong for Mandrake or SuSE. They're certainly
# wrong for Debian, but what are you doing using RPM on Debian?

%pre

# If tor is already installed and running (whether installed by RPM
# or not), then kill it, but remember that it was running.
%__rm -f /tmp/${name}-was-running-%{version}-%{release}
if [ -f %{_initrddir}/%{name} ] && /sbin/service %{name} status &> /dev/null; then
    /sbin/service %{name} stop
    touch /tmp/${name}-was-running-%{version}-%{release}
fi

#
# Create a user and group if need be
#
if [ ! -n "`/usr/bin/id -g %{torgroup} 2>/dev/null`" ]; then
    # One would like to default the GID, but doing that properly would
    # require thought.
    %{_sbindir}/groupadd %{torgroup} 2> /dev/null
fi
if [ ! -n "`/usr/bin/id -u %{toruser} 2>/dev/null`" ]; then
    # One would also like to default the UID, but doing that properly would
    # also require thought.
    if [ -x %{_sbindir}/nologin ]; then
        %{_sbindir}/useradd -r -g %{torgroup} -d% {_localstatedir}/lib/%{name} -s %{_sbindir}/nologin %{toruser} 2> /dev/null
    else
        %{_sbindir}/useradd -r -g %{torgroup} -d %{_localstatedir}/lib/%{name}  -s /bin/false %{toruser} 2> /dev/null
    fi
fi
exit 0

%post

# If this is a new installation, use chkconfig to put tor in the
# default set of runlevels. If it's an upgrade, leave the existing
# configuration alone.
#if [ $1 -eq 1 ]; then
#    /sbin/chkconfig --add %{name}
#fi

# Older tor RPMS used a different username for the tor daemon.
# Make sure the runtime data have the right ownership.
%__chown -R %{toruser}.%{torgroup} %{_localstatedir}/{lib,log,run}/%{name}

#if [ -f /tmp/${name}-was-running-%{version}-%{release} ]; then
#    /sbin/service %{name} start
#    %__rm -f /tmp/${name}-was-running-%{version}-%{release}
#fi
exit 0

%preun

# If no instances of tor will be installed when we're done, make
# sure that it gets killed. We *don't* want to kill it or delete
# any of its data on uninstall if it's being upgraded to a new
# version, because the new version will actually already have
# been installed and started before the uninstall script for
# the old version is run, and we'd end up hosing it.
#if [ $1 -le 0 ]; then
#    if [ -f %{_initrddir}/%{name} ] && /sbin/service %{name} status ; then
#        /sbin/service %{name} stop
#    fi
#    %/sbin/chkconfig --del %{name}
#    %__rm -f ${_localstatedir}/lib/%{name}/cached-directory
#    %__rm -f ${_localstatedir}/lib/%{name}/bw_accounting
#    %__rm -f ${_localstatedir}/lib/%{name}/control_auth_cookie
#    %__rm -f ${_localstatedir}/lib/%{name}/router.desc
#    %__rm -f ${_localstatedir}/lib/%{name}/fingerprint
#fi
exit 0

%files
%defattr(-,root,root)
%doc AUTHORS INSTALL LICENSE README ChangeLog doc/HACKING doc/TODO
%{_mandir}/man*/*
%dir %{_datadir}/tor
%{_datadir}/tor/geoip
%{_bindir}/tor
%{_bindir}/torctl
%{_bindir}/torify
%{_bindir}/tor-resolve
%{_bindir}/tor-gencert

%config %{_initrddir}/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}
%dir %attr(0755,root,%{torgroup}) %{_sysconfdir}/%{name}/
%config(noreplace) %attr(0644,root,%{torgroup}) %{_sysconfdir}/%{name}/*
%attr(0700,%{toruser},%{torgroup}) %dir %{_localstatedir}/lib/%{name}
%attr(0750,%{toruser},%{torgroup}) %dir %{_localstatedir}/run/%{name}
%attr(0750,%{toruser},%{torgroup}) %dir %{_localstatedir}/log/%{name}

%changelog
* Mon Feb 01 2009 YangH - 0.2.0.33
- New upstream 0.2.0.33

* Mon Dec 29 2008 YangH - 0.2.0.32
- New upstream 0.2.0.32 for Everest

* Tue Mar 28 2006 Andrew Lewman <phobos@interloper.org>
- converted to build the specified target cpu and arch
- override related rpm macros to build correctly
- see OR-CVS for details

