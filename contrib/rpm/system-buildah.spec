Name:           system-buildah
Version:        0.1.0
Release:        1%{?dist}
Summary:        Simple toolbox for building system containers

License:        GPLv3+
URL:            https://github.com/projectatomic/system-buildah/
Source0:        https://github.com/projectatomic/system-buildah/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel, python3-setuptools
Requires:       python3-jinja2

%description
Simple toolbox for building system containers.


%prep
%autosetup -n %{name}-%{version}


%build
%{__python3} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
# Force python3
sed -i 's|/usr/bin/env python|/usr/bin/python3|' $RPM_BUILD_ROOT%{python3_sitelib}/system_buildah/cli.py


%files
%license LICENSE COPYING
%doc README.md
%{python3_sitelib}/*
%{_bindir}/%{name}


%changelog
* Fri Feb 23 2018 Steve Milner <smilner@redhat.com> - 0.1.0-1
- buildah tar update

* Mon Feb  5 2018 Steve Milner <smilner@redhat.com> - 0.0.9-1
- Code reorganization

* Tue Jul 11 2017 Steve Milner <smilner@redhat.com> - 0.0.8-1
- Dockerfile template bugfix

* Mon Jul 10 2017 Steve Milner <smilner@redhat.com> - 0.0.7-1
- Code clean up
- Basic logging
- init.sh added to file generation
- Functionality for different build backends
- More unittesting for cli
- Experimental buildah support

* Fri Jun 16 2017 Steve Milner <smilner@redhat.com> - 0.0.6-1
- Support for remote docker daemons
- More unittesting for cli
- Use the same json indent level

* Wed May 31 2017 Steve Milner <smilner@redhat.com> - 0.0.5-1
- Additional tests
- tar now outputs to $NAME-$LABEL.tar

* Wed May 24 2017 Steve Milner <smilner@redhat.com> - 0.0.4-1
- Update for release.
* Mon Apr 10 2017 Steve Milner <smilner@redhat.com> - 0.0.3-1
- Initial spec
