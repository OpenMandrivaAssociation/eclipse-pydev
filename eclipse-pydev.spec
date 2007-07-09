Epoch: 1

%define gcj_support         1
%define version_major       1
%define version_minor       3
%define version_majmin      %{version_major}.%{version_minor}
%define version_micro       1
%define eclipse_base        %{_datadir}/eclipse

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:          Eclipse Python development plug-in
Name:             eclipse-pydev
Version:          %{version_majmin}.%{version_micro}
Release:          %mkrel 5.1.1
License:          EPL
URL:              http://pydev.sourceforge.net/
Group:            Development/Java

# The upstream PyDev project does not distribute a source drop conveniently.
# Instead, you must build it by hand. Generate the source zip using the 
# enclosed script like so:
#  ./fetch-eclipse-pydev.sh pydev \
#    :pserver:anonymous@sourceware.org/cvs/eclipse pydev_1_3_1 \
#    pydev/org.python.pydev.releng 

Source0:          eclipse-pydev-fetched-src-pydev_%{version_major}_%{version_minor}_%{version_micro}.tar.bz2
Source1:          fetch-eclipse-pydev.sh
Patch0:           eclipse-pydev-stack.patch
# Remove references to the retroweaver jar, since we don't use it
Patch1:           %{name}-noretroweaver.patch
# Add a TestDependent class which makes the tests compile
Patch2:           %{name}-TestDependent.java.patch

%if %{gcj_support}
BuildRequires:    java-1.5.0-gcj-devel
Requires(post):   java-1.5.0-gcj
Requires(postun): java-1.5.0-gcj
%else
BuildRequires:    java-devel >= 0:1.5.0
%endif

Requires:         eclipse-jdt
Requires:         python
Requires:         commons-codec >= 0:1.3
Requires:         junit >= 0:3.8.1
Requires:         jython >= 0:2.2
BuildRequires:    eclipse-pde
BuildRequires:    jpackage-utils >= 0:1.5
BuildRequires:    junit >= 0:3.8.1
BuildRequires:    commons-codec >= 0:1.3
BuildRequires:    jython >= 0:2.2

%if %{gcj_support}
%else
BuildArch:        noarch
%endif
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%prep
%setup -q -c 
%patch0 -p1
pushd pydev/org.python.pydev.releng/results/
%patch1 -p0
%patch2 -p0

# Replace all references to 0.9.7.1 with the correct version number
for f in `grep -rl '0.9.7.1' *` ; do 
    if [ -f $f ]; then
        sed --in-place "s/0.9.7.1/%{version_majmin}.%{version_micro}/g" $f
    fi
done 

# Remove the unused retroweaver jar
find . -name retroweaver-rt.jar -exec rm {} \;

# Remove #!'s from the .py files enclosed in org.python.pydev.jython
for f in `find plugins -name '*.py'` ; do 
    if [ -f $f ]; then
        sed --in-place "s/^#!.*$//" $f
    fi
done 

# Link to system jars
rm -f plugins/org.python.pydev.core/commons-codec.jar
ln -sf %{_datadir}/java/jakarta-commons-codec.jar \
       plugins/org.python.pydev.core/commons-codec.jar

rm -f plugins/org.python.pydev.core/lib/junit.jar
ln -sf %{_datadir}/java/junit.jar \
       plugins/org.python.pydev.core/junit.jar

rm -f plugins/org.python.pydev.jython/jython.jar
ln -sf %{_datadir}/java/jython.jar \
       plugins/org.python.pydev.jython/jython.jar

popd

%build
# Copy the SDK for build
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
SDK=$(cd SDK > /dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home
homedir=$(cd home > /dev/null && pwd)

# build the main pydev feature
%{_bindir}/eclipse \
     -Duser.home=$homedir                              \
     -application org.eclipse.ant.core.antRunner       \
     -Dtype=feature                                    \
     -Did=org.python.pydev.feature                     \
     -DbaseLocation=$SDK                               \
     -DsourceDirectory=$(pwd)                          \
     -DjavacSource=1.5  -DjavacTarget=1.5              \
     -DbuildDirectory=$(pwd)/build                     \
     -Dbuilder=%{eclipse_base}/plugins/org.eclipse.pde.build/templates/package-build \
     -f %{eclipse_base}/plugins/org.eclipse.pde.build/scripts/build.xml

%install
rm -rf $RPM_BUILD_ROOT
install -d -m755 ${RPM_BUILD_ROOT}/%{eclipse_base}
unzip -q -d $RPM_BUILD_ROOT%{eclipse_base}/.. \
            build/rpmBuild/org.python.pydev.feature.zip

pushd $RPM_BUILD_ROOT%{_datadir}/eclipse/plugins
rm -rf \
  org.python.pydev.core_%{version_majmin}.%{version_micro}/commons-codec.jar
ln -sf %{_datadir}/java/jakarta-commons-codec.jar \
  org.python.pydev.core_%{version_majmin}.%{version_micro}/commons-codec.jar

mkdir org.python.pydev.core_%{version_majmin}.%{version_micro}/lib
ln -sf %{_datadir}/java/junit.jar \
  org.python.pydev.core_%{version_majmin}.%{version_micro}/lib/junit.jar

rm -rf \
  org.python.pydev.jython_%{version_majmin}.%{version_micro}/jython.jar
ln -sf %{_datadir}/java/jython.jar \
  org.python.pydev.jython_%{version_majmin}.%{version_micro}/jython.jar
popd

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean 
rm -rf ${RPM_BUILD_ROOT}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%{eclipse_base}/features/org.python.pydev*
%{eclipse_base}/plugins/org.python.pydev_*
%{eclipse_base}/plugins/org.python.pydev.ast*
%{eclipse_base}/plugins/org.python.pydev.core*
%{eclipse_base}/plugins/org.python.pydev.debug*
%{eclipse_base}/plugins/org.python.pydev.help*
%{eclipse_base}/plugins/org.python.pydev.parser*
%{eclipse_base}/plugins/org.python.pydev.templates*
%{eclipse_base}/plugins/org.python.pydev.jython*
%{eclipse_base}/plugins/org.python.pydev.refactoring*

%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif
