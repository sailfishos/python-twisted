Name:           python3-twisted
Version:        22.10.0
Release:        0
Summary:        Asynchronous networking framework written in Python
License:        MIT
URL:            https://github.com/sailfishos/python-twisted
Source0:        %{name}-%{version}.tar.bz2
Source1:        twisted-dropin-cache

BuildRequires:  python3-devel
BuildRequires:  python3-zope-interface
BuildRequires:  python3-incremental
BuildRequires:  python3-setuptools
Requires:       python3-base
Requires:       python3-zope-interface

BuildArch:      noarch

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
Requires:       %{name} = %{version}-%{release}

%description doc
Documentation for Twisted.

%prep
%autosetup -n %{name}-%{version}/twisted

# Turn off exec bits on docs to avoid spurious dependencies
find docs -type f | xargs chmod 644

# Fix line endings
sed -i -e 's,\r$,,' docs/core/howto/listings/udp/*

%build
%py3_build

%install
%py3_install

# iocpreactor is a win32 reactor, so we can delete it
rm -rf $RPM_BUILD_ROOT%{python3_sitelib}/twisted/internet/iocpreactor

# Man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/
cp -a docs/*/man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1/
rm -rf docs/man

# script to regenerate dropin.cache
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_libexecdir}

# Create an empty dropin.cache to be %%ghost-ed
touch $RPM_BUILD_ROOT%{python3_sitelib}/twisted/plugins/dropin.cache

# See if there's any egg-info
if [ -f $RPM_BUILD_ROOT%{python3_sitelib}/Twisted*.egg-info ]; then
    echo $RPM_BUILD_ROOT%{python3_sitelib}/Twisted*.egg-info |
        sed -e "s|^$RPM_BUILD_ROOT||"
fi > egg-info

mkdir -p %{buildroot}/%{_docdir}/%{name}-%{version}
install -m 644 -t %{buildroot}/%{_docdir}/%{name}-%{version} NEWS.rst README.rst
cp -r docs/* %{buildroot}/%{_docdir}/%{name}-%{version}/

%post
%{_libexecdir}/twisted-dropin-cache || :

%preun
if [ $1 -eq 0 ]; then
    # Complete removal, not upgrade, so remove plugins cache file
    %{__rm} -f %{python3_sitelib}/twisted/plugins/dropin.cache || :
fi

%files -f egg-info
%license LICENSE
%attr(0755, root, root) %{_bindir}/*
%attr(0755, root, root) %{_libexecdir}/twisted-dropin-cache
%ghost %{python3_sitelib}/twisted/plugins/dropin.cache
%{python3_sitelib}/Twisted-*-py%{python3_version}.egg-info
%{python3_sitelib}/twisted

%files doc
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/man1/*
