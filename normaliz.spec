%{?_javapackages_macros:%_javapackages_macros}
Name:           normaliz
Version:        2.10.1
Release:        2.3%{?dist}
Summary:        A tool for mathematical computations

License:        GPLv3+
URL:            https://www.mathematik.uni-osnabrueck.de/normaliz/
# Warning: This zip-ball contains .jar binaries, source only zip-ball not
# available
Source0:        http://www.mathematik.uni-osnabrueck.de/normaliz/Normaliz%{version}/Normaliz%{version}.zip
# Change the Makefiles to use our build flags, build libnormaliz as a shared
# library, and link the normaliz binary with the shared library
Patch0:         %{name}-shlib.patch

BuildRequires:  ant
BuildRequires:  apache-commons-exec
BuildRequires:  apache-commons-exec-javadoc
BuildRequires:  appframework
BuildRequires:  boost-devel
BuildRequires:  gmp-devel
%if 0%{?fedora}
%else
BuildRequires:  gmpxx-devel
BuildRequires:  gomp-devel
%endif
BuildRequires:  java-devel >= 1:1.6.0
BuildRequires:  javasysmon
BuildRequires:  jpackage-utils

Requires:       lib%{name}%{?_isa} = %{version}-%{release}

%global nopatchver %(cut -d. -f1-2 <<< %{version})

%description
Normaliz is a tool for computations in affine monoids, vector
configurations, lattice polytopes, and rational cones.

Documentation and examples can be found in %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}},
in particular you may find Normaliz%{version}Documentation.pdf useful.  

%package -n libnormaliz
Summary:        Normaliz internals as a library
%ifarch x86_64 aarch64
Provides:	libnormaliz.so.2.10()(64bit)
%else
Provides:	libnormaliz.so.2.10
%endif

%description -n libnormaliz
This package contains the normaliz internals as a library, often called
libnormaliz.

%package -n libnormaliz-devel
Summary:        Developer files for libnormaliz
Requires:       lib%{name}%{?_isa} = %{version}-%{release}

%description -n libnormaliz-devel
Header files and library links to develop applications that use the
Normaliz internals as a library (libnormaliz).

%package -n jnormaliz
Summary:        Graphical interface for Normaliz
Requires:       %{name} = %{version}-%{release}
Requires:       apache-commons-exec
Requires:       appframework
Requires:       java >= 1:1.6.0
Requires:       javasysmon
Requires:       jpackage-utils
BuildArch:      noarch

%description -n jnormaliz
JNormaliz is a graphic interface for Normaliz, written in Java.

%package -n jnormaliz-javadoc
Summary:        Javadoc documentation for jNormaliz
Requires:       jnormaliz = %{version}-%{release}
Requires:       apache-commons-exec-javadoc
Requires:       jpackage-utils
BuildArch:      noarch

%description -n jnormaliz-javadoc
Javadoc documentation for jNormaliz

%prep
%setup -q -n Normaliz%{nopatchver}
%patch0

# Remove prebuilt class files, jars, and javadocs, except for one netbeans jar
# used for building only (no runtime dependencies).
find . -name \*.jar -a \! -name \*copylibstask.jar | xargs rm -f
rm -fr source/jNormaliz/build

# Use system jars instead of bundled jars
ln -s %{_javadir}/appframework.jar lib/appframework-1.0.3.jar
ln -s %{_javadir}/commons-exec.jar lib/commons-exec-1.0.1.jar
ln -s %{_javadir}/javasysmon.jar lib/javasysmon.jar

cd source/jNormaliz/lib
ln -s %{_javadir}/commons-exec.jar commons-exec-1.0.1/commons-exec-1.0.1.jar
ln -s %{_javadocdir}/apache-commons-exec commons-exec-1.0.1/apidocs
ln -s %{_javadir}/javasysmon.jar javasysmon.jar
ln -s %{_javadir}/junit.jar junit_4/junit-4.5.jar
ln -s %{_javadir}/appframework.jar swing-app-framework/appframework-1.0.3.jar

%build
# Build the C library and the binaries
pushd source
export CXXFLAGS="%{optflags}"
export NORMFLAGS="-Wl,--as-needed $RPM_LD_FLAGS"
export VERSION="%{nopatchver}"
export MAJOR="%(cut -d. -f1 <<< %{version})"
make %{?_smp_mflags}

# Build the Java interface and documentation
cd jNormaliz
ant jar
ant javadoc
popd

mkdir -p docs/example

# Correct the end of line encodings for use on Linux
pushd example
for file in *.out *.in 
do
    sed 's/\r//' "$file" > "../docs/example/$file"
    touch -r "$file" "../docs/example/$file"
done
popd

mv doc/Normaliz%{nopatchver}Documentation.pdf docs
mv "doc/Computing the integral closure of an affine semigroup.pdf" \
    docs/Computing_the_integral_closure_of_an_affine_semigroup.pdf

%install
# Install the binary
install -D -m 755 source/normaliz %{buildroot}%{_bindir}/normaliz

# Install the library
mkdir -p %{buildroot}%{_libdir}
cp -a source/libnormaliz/libnormaliz.so* %{buildroot}%{_libdir}

# Install the headers
mkdir -p %{buildroot}%{_includedir}/libnormaliz
cp -p source/libnormaliz/*.h %{buildroot}%{_includedir}/libnormaliz

# Install the jar
mkdir -p %{buildroot}%{_javadir}
cp -p source/jNormaliz/dist/jNormaliz.jar %{buildroot}%{_javadir}

# Install the javadoc
mkdir -p %{buildroot}%{_javadocdir}
cp -a source/jNormaliz/dist/javadoc %{buildroot}%{_javadocdir}/jnormaliz

chmod a+r %{buildroot}%{_includedir}/libnormaliz/*.h

%files
%doc source/COPYING
%doc docs/*
%{_bindir}/normaliz

%files -n libnormaliz
%{_libdir}/libnormaliz.so.*

%files -n libnormaliz-devel
%doc source/libnormaliz/README
%{_libdir}/libnormaliz.so
%{_includedir}/libnormaliz/

%files -n jnormaliz
%{_javadir}/jNormaliz.jar

%files -n jnormaliz-javadoc
%{_javadocdir}/jnormaliz

%changelog
* Wed Jan 15 2014 Jerry James <loganjerry@gmail.com> - 2.10.1-2
- Fix thinko in -devel dependencies

* Tue Jan 14 2014 Jerry James <loganjerry@gmail.com> - 2.10.1-1
- New upstream release
- Package libnormaliz and jNormaliz separately

* Wed Aug 21 2013 Ville Skyttä <ville.skytta@iki.fi> - 2.7-8
- Adjust for unversioned %%{_docdir_fmt} (#994006).

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7-7.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 30 2013 Petr Machata <pmachata@redhat.com> - 2.7-6.2
- Rebuild for boost 1.54.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7-5.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7-4.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7-3.2
- Rebuilt for c++ ABI breakage

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7-2.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 26 2011 Marcela Mašláňová <mmaslano@redhat.com> - 2.7-1.2
- rebuild with new gmp without compat lib

* Wed Oct 12 2011 Peter Schiffer <pschiffe@redhat.com> - 2.7-1.1
- rebuild with new gmp

* Fri May 27 2011 Rex Dieter <rdieter@fedoraproject.org> 2.7-1
- 2.7

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Feb 25 2010 Mark Chappell <tremble@fedoraproject.org> - 2.2-3
- Preserve timestamps on examples
- Ensure that the first command in install is to wipe the buildroot
- Tweak to description

* Thu Feb 25 2010 Mark Chappell <tremble@fedoraproject.org> - 2.2-2
- Move examples into a subdirectory
- Correct inconsistant use of macros
- Provide a reference to the documentation in the description

* Wed Feb 24 2010 Mark Chappell <tremble@fedoraproject.org> - 2.2-1
- Initial build
