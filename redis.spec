# Check for status of man pages
# http://code.google.com/p/redis/issues/detail?id=202

Name:             redis
Version:          2.8.9
Release:          1%{?dist}
Summary:          A persistent key-value database

Group:            Applications/Databases
License:          BSD
URL:              http://redis.io
Source0:          http://redis.googlecode.com/files/%{name}-%{version}.tar.gz
Source1:          %{name}.logrotate
Source2:          %{name}.init
# Update configuration
Patch0:           %{name}-%{version}-redis.conf.patch
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:    tcl >= 8.5

ExcludeArch:      ppc64

Requires:         logrotate
Requires(post):   chkconfig
Requires(postun): initscripts
Requires(pre):    shadow-utils
Requires(preun):  chkconfig
Requires(preun):  initscripts

%package -n libae
Summary:          Redis asynchronous event library
Group:            System Environment/Libraries

%package -n libae-devel
Summary:          Header files and libraries for Redis asynchronous event library
Group:            Development/Libraries
Requires:         libae

%description
Redis is an advanced key-value store. It is similar to memcached but the data
set is not volatile, and values can be strings, exactly like in memcached, but
also lists, sets, and ordered sets. All this data types can be manipulated with
atomic operations to push/pop elements, add/remove elements, perform server side
union, intersection, difference between sets, and so forth. Redis supports
different kind of sorting abilities.

%description -n libae
Redis asynchronous event library. This library also includes the custom
allocator implementation zmalloc.

%description -n libae-devel
The libae-devel package contains the header files and libraries to develop
applications using Redis asynchronous event library.

%prep
%setup -q
%patch0 -p0

%build
make %{?_smp_mflags} \
  DEBUG='' \
  CFLAGS='%{optflags}' \
  V=1 \
  all

%check
make test

%install
rm -fr %{buildroot}
make install PREFIX=%{buildroot}%{_prefix}
# Install misc other
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
install -p -D -m 644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{name}

# Fix non-standard-executable-perm error
chmod 755 %{buildroot}%{_bindir}/%{name}-*

# Ensure redis-server location doesn't change
mkdir -p %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/%{name}-server %{buildroot}%{_sbindir}/%{name}-server

cd src
# install headers
install -p -D -m 644 ae.h %{buildroot}%{_includedir}
install -p -D -m 644 zmalloc.h %{buildroot}%{_includedir}
# build ae.o and zmalloc.o
for src in ae.c zmalloc.c; do
    cc -std=c99 -pedantic -Wall -O2 -g -ggdb -O2 -g
        -I../deps/hiredis -I../deps/linenoise -I../deps/lua/src \
        -DUSE_JEMALLOC -I../deps/jemalloc/include -c $src
done
# create static library libae.a
ar rcs libae.a ae.o config.o zmalloc.o
install -p -D -m 644 libae.a %{buildroot}%{_libdir}
# create shared library libae.so
gcc -shared -Wl,-soname,libae.so.2 -o libae.so.2.8.9 ae.o config.o zmalloc.o
install -p -D -m 644 libae.so.2.8.9 %{buildroot}%{_libdir}
cd %{buildroot}%{_libdir}
ln -sf libae.so.2.8.9 libae.so.2
ln -sf libae.so.2.8.9 libae.so

%clean
rm -fr %{buildroot}

%post
/sbin/chkconfig --add redis

%pre
getent group redis &> /dev/null || groupadd -r redis &> /dev/null
getent passwd redis &> /dev/null || \
useradd -r -g redis -d %{_sharedstatedir}/redis -s /sbin/nologin \
-c 'Redis Server' redis &> /dev/null
exit 0

%preun
if [ $1 = 0 ]; then
  /sbin/service redis stop &> /dev/null
  /sbin/chkconfig --del redis &> /dev/null
fi

%files
%defattr(-,root,root,-)
%doc 00-RELEASENOTES BUGS CONTRIBUTING COPYING README
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/run/%{name}
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_initrddir}/%{name}

%files -n libae
%defattr(-,root,root,-)
%{_libdir}/libae.so
%{_libdir}/libae.so.2
%{_libdir}/libae.so.2.8.9

%files -n libae-devel
%defattr(-,root,root,-)
%{_includedir}/ae.h
%{_includedir}/zmalloc.h
%{_libdir}/libae.a

%changelog
* Mon May 12 2014 Per Andersson <avtobiff@gmail.com> - 2.8.9-1
- Update to redis 2.8.9

* Tue Apr 16 2013 Karl Böhlmark <karl.bohlmark@gmail.com> - 2.6.12-1
- Update to redis 2.6.12

* Thu Feb 06 2013 Karl Böhlmark <karl.bohlmark@gmail.com> - 2.6.9-1
- Update to redis 2.6.9

* Sat Mar 31 2012 Silas Sewell <silas@sewell.org> - 2.4.10-1
- Update to redis 2.4.10

* Fri Feb 24 2012 Silas Sewell <silas@sewell.org> - 2.4.8-2
- Disable ppc64 for now
- Enable verbose builds

* Fri Feb 24 2012 Silas Sewell <silas@sewell.org> - 2.4.8-1
- Update to redis 2.4.8

* Sat Apr 23 2011 Silas Sewell <silas@sewell.ch> - 2.2.5-2
- Remove google-perftools-devel

* Sat Apr 23 2011 Silas Sewell <silas@sewell.ch> - 2.2.5-1
- Update to redis 2.2.5

* Tue Oct 19 2010 Silas Sewell <silas@sewell.ch> - 2.0.3-1
- Update to redis 2.0.3

* Fri Oct 08 2010 Silas Sewell <silas@sewell.ch> - 2.0.2-1
- Update to redis 2.0.2
- Disable checks section for el5

* Fri Sep 11 2010 Silas Sewell <silas@sewell.ch> - 2.0.1-1
- Update to redis 2.0.1

* Sat Sep 04 2010 Silas Sewell <silas@sewell.ch> - 2.0.0-1
- Update to redis 2.0.0

* Thu Sep 02 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-3
- Add Fedora build flags
- Send all scriplet output to /dev/null
- Remove debugging flags
- Add redis.conf check to init script

* Mon Aug 16 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-2
- Don't compress man pages
- Use patch to fix redis.conf

* Tue Jul 06 2010 Silas Sewell <silas@sewell.ch> - 1.2.6-1
- Initial package
