%{!?python_sitearch: %define python_sitearch %(%{python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           python-twisted
Version:        12.3.0
Release:        0
Group:          Development/Languages
Summary:        Asynchronous networking framework written in Python
License:        MIT
URL:            http://twistedmatrix.com/trac/
Source0:        %{name}-%{version}.tar.bz2
Source1:        twisted-dropin-cache
# Available here:
# https://apestaart.org/thomas/trac/browser/pkg/fedora.extras/python-twisted-core/twisted-dropin-cache?format=raw

BuildRequires:  python-devel
BuildRequires:  python-zope-interface >= 3.0.1
Requires:       python
Requires:       python-zope-interface

%description
An extensible framework for Python programming, with special focus
on event-based network programming and multiprotocol integration.

It is expected that one day the project will expanded to the point
that the framework will seamlessly integrate with mail, web, DNS,
netnews, IRC, RDBMSs, desktop environments, and your toaster.

Twisted Core is used by most of the servers, clients and protocols that are
part of other Twisted projects.

%package doc
Summary:        Documentation for Twisted Core
Requires:       python-twisted = %{version}-%{release}

%description doc
Documentation for Twisted.

%prep
%setup -q -n %{name}-%{version}/Twisted

# Turn off exec bits on docs to avoid spurious dependencies
find doc -type f | xargs chmod 644

# Fix line endings
sed -i -e 's,\r$,,' doc/core/howto/listings/udp/*

%build
CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# cfsupport is support for MacOSX Core Foundations, so we can delete it
rm -rf $RPM_BUILD_ROOT%{python_sitearch}/twisted/internet/cfsupport

# iocpreactor is a win32 reactor, so we can delete it
rm -rf $RPM_BUILD_ROOT%{python_sitearch}/twisted/internet/iocpreactor

# Man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/
cp -a doc/*/man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1/
rm -rf doc/man

# Some of the zsh completions are no longer appropriate
find $RPM_BUILD_ROOT%{python_sitearch}/twisted/python/zsh -size 0c -exec rm -f {} \;

# script to regenerate dropin.cache
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_libexecdir}

# Create an empty dropin.cache to be %%ghost-ed
touch $RPM_BUILD_ROOT%{python_sitearch}/twisted/plugins/dropin.cache

# C files don't need to be packaged
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/protocols/_c_urlarg.c
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/test/raiser.c
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/python/sendmsg.c
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/python/_initgroups.c
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/runner/portmap.c
rm -f $RPM_BUILD_ROOT%{python_sitearch}/twisted/python/_epoll.c

# Fix permissions of shared objects
chmod 755 $RPM_BUILD_ROOT%{python_sitearch}/twisted/test/raiser.so

# See if there's any egg-info
if [ -f $RPM_BUILD_ROOT%{python_sitearch}/Twisted*.egg-info ]; then
    echo $RPM_BUILD_ROOT%{python_sitearch}/Twisted*.egg-info |
        sed -e "s|^$RPM_BUILD_ROOT||"
fi > egg-info

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{_libexecdir}/twisted-dropin-cache || :

%preun
if [ $1 -eq 0 ]; then
    # Complete removal, not upgrade, so remove plugins cache file
    %{__rm} -f %{python_sitearch}/twisted/plugins/dropin.cache || :
fi

%files -f egg-info
%defattr(0644, root, root, 0755)
%doc LICENSE NEWS README
%attr(0755, root, root) %{_bindir}/*
%attr(0755, root, root) %{_libexecdir}/twisted-dropin-cache
%{_mandir}/man1/*
%ghost %{python_sitearch}/twisted/plugins/dropin.cache
%{python_sitearch}/twisted/*

%files doc
%doc doc/*

