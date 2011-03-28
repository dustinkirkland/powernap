# powernap.spec
%define version 2.4
%define release 1
%define _unpackaged_files_terminate_build 0

Summary:   Powernap
Name:      powernap
Version:   %{version}
Release:   %{release}
License:   GPL
Group:     Applications/System
Source0:   %{name}_%{version}.orig.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}
Requires:  %{name}_%{version}=upstart >= 0.6.5 

%description
PowerNap is a configurable daemon that will bring a running system to a lower power state according
to a set of configuration preferences. It acts as a sort of "screensaver" for servers, watching the
process table for activity rather than the keyboard or mouse. PowerNap will run $ACTION when none
of $PROCESSES have executed for some number of $ABSENCE seconds. For instance, PowerNap can
automatically "pm-suspend" a system if no instance of "kvm" runs for some contiguous block of "300"
seconds.

# Sub package section used to generate powernap-common rpms
%package -n powernap-common
Summary:   powernap-common
Version:   %{version}
Release:   %{release}
Group:     Applications/System
Requires:  powernap-common_%{version}=upstart >= 0.6.5

%description -n powernap-common
This package contains the common library files required as a runtime dependency of powernap.


# Sub package section used to generate powerwake rpms
%package -n powerwake
Summary:   powerwake
Version:   %{version}
Release:   %{release}
Group:     Applications/System
Requires:  powerwake_%{version}=upstart >= 0.6.5 

%description -n powerwake
PowerWake is a generic mechanism for remotely waking systems. It is intended to support wake-on-lan,
ipmi, and other remote waking mechanisms. Currently, wake-on-lan is the only supported mechanism. It
also includes some handy caching of MAC addresses, such that systems can be awakened by
hostname or ip address, in addition to MAC address.

# prep section is used to setup the build environment for the software is created and directing
# RPM through the process of preparing the software for building
%prep
%setup powernap-2.4

# Create the temporary build directory to build the rpms

%install
for x in $RPM_BUILD_ROOT $RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT/usr/sbin $RPM_BUILD_ROOT/usr/bin $RPM_BUILD_ROOT/usr/share $RPM_BUILD_ROOT/usr/share/man $RPM_BUILD_ROOT/usr/lib/python2.7 $RPM_BUILD_ROOT/usr/lib/python2.7/dist-packages $RPM_BUILD_ROOT/usr/lib/python2.7/dist-packages/powernap $RPM_BUILD_ROOT/usr/lib/python2.7/dist-packages/powernap/monitors $RPM_BUILD_ROOT/usr/share/man/man1 $RPM_BUILD_ROOT/usr/share/man/man8 $RPM_BUILD_ROOT/usr/share/pyshared $RPM_BUILD_ROOT/usr/share/pyshared/powernap $RPM_BUILD_ROOT/usr/share/pyshared/powernap/monitors $RPM_BUILD_ROO/usr/share/doc/powernap/ $RPM_BUILD_ROOT/etc $RPM_BUILD_ROOT/etc/init $RPM_BUILD_ROOT/etc/init.d $RPM_BUILD_ROOT/etc/logrotate.d $RPM_BUILD_ROOT/etc/bash_completion.d/ $RPM_BUILD_ROOT/etc/powernap $RPM_BUILD_ROOT/etc/pm $RPM_BUILD_ROOT/etc/pm/power.d ; do
install -d $x
done

# Install the necessary files to the build directory to generate rpms

# Installing all super user binaries in /usr/sbin
pushd $RPM_BUILD_ROOT/usr/sbin
for x in powernap powernapd powernap-now powernap-action powerwake-now ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/sbin/$x $RPM_BUILD_ROOT/usr/sbin
done
popd

# Installing all binaries in /usr/bin
pushd $RPM_BUILD_ROOT/usr/bin
for x in powernap_calculator powerwake ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/bin/$x $RPM_BUILD_ROOT/usr/sbin
done
popd

install -D /usr/src/redhat/BUILD/powernap-2.4/powerwake_completion $RPM_BUILD_ROOT/etc/bash_completion.d

# Installing configuration files in /etc/powernap
pushd $RPM_BUILD_ROOT/etc/powernap
for x in action config ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/$x $RPM_BUILD_ROOT/etc/powernap
done
popd

pushd $RPM_BUILD_ROOT/etc/pm/power.d
for x in 01cpu_online cpu_frequency eth_speed usb usb_autosuspend video ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/actions/$x $RPM_BUILD_ROOT/etc/pm/power.d
done
popd

# Installing all powernap specific python scripts
pushd $RPM_BUILD_ROOT/usr/share/pyshared
for x in __init__.py powernap.py ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/powernap/$x $RPM_BUILD_ROOT/usr/share/pyshared/powernap
done
popd

# Installing all powernap specific python scripts
pushd $RPM_BUILD_ROOT/usr/share/pyshared/powernap/monitors
for x in ProcessMonitor.py ConsoleMonitor.py IOMonitor.py InputMonitor.py LoadMonitor.py Monitor.py TCPMonitor.py UDPMonitor.py WoLMonitor.py __init__.py ; do
install -D /usr/src/redhat/BUILD/powernap-2.4/powernap/monitors/$x $RPM_BUILD_ROOT/usr/share/pyshared/powernap/monitors
done
popd

# Installing man pages in man1 directory assuming that the source is present in
# /usr/src/redhat/BUILD/powernap-2.4 directory
pushd $RPM_BUILD_ROOT/usr/share/man/man1
for x in powernap_calculator.1 powerwake.1 ; do
gzip /usr/src/redhat/BUILD/powernap-2.4/man/$x
install -D /usr/src/redhat/BUILD/powernap-2.4/man/$x.gz $x.gz
done
popd

# Installing man pages in man8 directory assuming that the source is present in
# /usr/src/redhat/BUILD/powernap-2.4 directory
pushd $RPM_BUILD_ROOT/usr/share/man/man8
for x in powernap.8 powernapd.8 powernap-now.8 powerwake-now.8 powernap-action.8 ; do
gzip /usr/src/redhat/BUILD/powernap-2.4/man/$x
install -D /usr/src/redhat/BUILD/powernap-2.4/man/$x.gz $x.gz
done
popd

# Creating soft links for powernap python scripts
pushd $RPM_BUILD_ROOT/usr/lib/python2.7/dist-packages/powernap/
for x in __init__.py powernap.py ; do
rm -f $x; /bin/ln -sf ../../../../share/pyshared/powernap/$x $x
done
popd

# Creating soft links for powernap python scripts
pushd $RPM_BUILD_ROOT/usr/lib/python2.7/dist-packages/powernap/monitors
for x in ProcessMonitor.py ConsoleMonitor.py IOMonitor.py InputMonitor.py LoadMonitor.py Monitor.py TCPMonitor.py UDPMonitor.py WoLMonitor.py __init__.py ; do
rm -f $x; /bin/ln -sf ../../../../../share/pyshared/powernap/monitors/$x $x
done
popd

# To clean up any files that are not part of the application's normal build area
%clean
#rm -rf $RPM_BUILD_ROOT
#rm -rf /usr/src/redhat/BUILD/powernap-2.4

# Files section contains list of the files that are part of the rpm
%files -n powernap
%defattr(-, root, root, 0555)
/usr/sbin/powernap
/usr/sbin/powernapd
/usr/sbin/powernap-now
/usr/sbin/powernap-action
/usr/sbin/powerwake-now
/usr/bin/powernap_calculator
/etc/powernap/action
/etc/powernap/config
/usr/share/man/man8/powernapd.8.gz
/usr/share/man/man8/powernap-now.8.gz
/usr/share/man/man8/powernap.8.gz
/usr/share/man/man8/powerwake-now.8.gz
/usr/share/man/man8/powernap-action.8.gz
/usr/share/man/man1/powernap_calculator.1.gz

# Files to be added in powernap-common rpm
%files -n powernap-common
/etc/pm/power.d/01cpu_online
/etc/pm/power.d/cpu_frequency
/etc/pm/power.d/eth_speed
/etc/pm/power.d/usb
/etc/pm/power.d/usb_autosuspend
/etc/pm/power.d/video
/usr/share/pyshared/powernap/__init__.py
/usr/share/pyshared/powernap/monitors/ProcessMonitor.py
/usr/share/pyshared/powernap/monitors/ConsoleMonitor.py
/usr/share/pyshared/powernap/monitors/IOMonitor.py
/usr/share/pyshared/powernap/monitors/InputMonitor.py
/usr/share/pyshared/powernap/monitors/LoadMonitor.py
/usr/share/pyshared/powernap/monitors/Monitor.py
/usr/share/pyshared/powernap/monitors/TCPMonitor.py
/usr/share/pyshared/powernap/monitors/UDPMonitor.py
/usr/share/pyshared/powernap/monitors/WoLMonitor.py
/usr/share/pyshared/powernap/monitors/__init__.py
/usr/share/pyshared/powernap/powernap.py
/usr/lib/python2.7/dist-packages/powernap/__init__.py
/usr/lib/python2.7/dist-packages/powernap/monitors/ConsoleMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/IOMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/InputMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/LoadMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/Monitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/ProcessMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/TCPMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/UDPMonitor.py
/usr/lib/python2.7/dist-packages/powernap/monitors/WoLMonitor.py
/usr/lib/python2.7/dist-packages/powernap/powernap.py

# Files to be added in powerwake rpm
%files -n powerwake
/usr/bin/powerwake
/usr/share/man/man1/powerwake.1.gz
/etc/bash_completion.d/powerwake_completion


%changelog
* Mon Mar 21 2011 Nandakumar Raghavan <nandkumar.raghavan@gmail.com>
- Spec file to build and generate powernap rpms for RedHat based distros (Revision 3)

* Fri Mar 4 2011 Nandakumar Raghavan <nandkumar.raghavan@gmail.com>
- Spec file to build and generate powernap rpms for RedHat based distros (Revision 2)

* Tue Mar 3 2011 Nandakumar Raghavan <nandkumar.raghavan@gmail.com>
- Spec file to build and generate powernap rpms for RedHat based distros

