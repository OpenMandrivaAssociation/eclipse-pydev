Epoch: 1

%define gcj_support         1

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Summary:          Eclipse Python development plug-in
Name:             eclipse-pydev
Version:          1.3.8
Release:          %mkrel 0.1.3
License:          Eclipse Public License
URL:              http://pydev.sourceforge.net/
Group:            Development/Java

Source0:          http://downloads.sourceforge.net/pydev/org.python.pydev.feature-src-1_3_8.zip

%if %{gcj_support}
BuildRequires:    gcc-java >= 4.1.2
BuildRequires:    java-1.5.0-gcj-devel >= 1.5.0
Requires(post):   java-1.5.0-gcj >= 1.5.0
Requires(postun): java-1.5.0-gcj >= 1.5.0
%else
BuildRequires:    java-devel >= 1.5.0
%endif

Requires:         eclipse-jdt
Requires:         eclipse-cvs-client
Requires:         python
Requires:         commons-codec >= 1.3
Requires:         junit >= 3.8.1
Requires:         jython >= 2.2
BuildRequires:    eclipse-pde
BuildRequires:    jpackage-utils >= 0:1.5
BuildRequires:    junit >= 3.8.1
BuildRequires:    commons-codec >= 1.3
BuildRequires:    jython >= 2.2

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

# remove pre-generated build files
find . -name build.xml | xargs rm 

# remove pre-built jars
rm -f plugins/org.python.pydev.core/core.jar
rm -f plugins/org.python.pydev.ast/ast.jar
rm -f plugins/org.python.pydev.debug/pydev-debug.jar
rm -f plugins/org.python.pydev.parser/parser.jar
rm -f plugins/org.python.pydev/pydev.jar
rm -f plugins/org.python.pydev.jython/pydev-jython.jar
rm -f plugins/org.python.pydev.refactoring/refactoring.jar

# remove included retroweaver jars as it isn't being used
find . -name retroweaver-rt.jar | xargs rm 

# link to system jars
rm -f plugins/org.python.pydev.core/commons-codec.jar
ln -sf %{_javadir}/jakarta-commons-codec.jar \
       plugins/org.python.pydev.core/commons-codec.jar

rm -f plugins/org.python.pydev.core/lib/junit.jar
ln -sf %{_javadir}/junit.jar \
       plugins/org.python.pydev.core/junit.jar

rm -f plugins/org.python.pydev.jython/jython.jar
ln -sf %{_javadir}/jython.jar \
       plugins/org.python.pydev.jython/jython.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/JFlex.jar
# enable when tests are used
#ln -sf %{_javadir}/jflex.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/JFlex.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/xpp3_min-1.1.3.4.O.jar
# enable when tests are used
#ln -sf %{_javadir}/xpp3-minimal.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xpp3_min-1.1.3.4.O.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/xstream-1.2.1.jar
# enable when tests are used
#ln -sf %{_javadir}/xstream.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xstream-1.2.1.jar

rm -f plugins/org.python.pydev.refactoring/contrib/ch/hsr/ukistler/astgraph/jgraph.jar

# Remove #!'s from the .py files enclosed in org.python.pydev.jython
for f in `find plugins -name '*.py'` ; do 
    if [ -f $f ]; then
        sed --in-place "s/^#!.*$//" $f
    fi
done 


%build
# Copy the SDK for build
/bin/sh -x %{_datadir}/eclipse/buildscripts/copy-platform SDK %{_datadir}/eclipse
SDK=$(cd SDK > /dev/null && pwd)

# Eclipse may try to write to the home directory.
mkdir home
homedir=$(cd home > /dev/null && pwd)

# build the main pydev feature
%{java} -cp $SDK/startup.jar                              \
     -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration  \
     org.eclipse.core.launcher.Main                    \
     -application org.eclipse.ant.core.antRunner       \
     -Dtype=feature                                    \
     -Did=org.python.pydev.feature                     \
     -DbaseLocation=$SDK                               \
     -DsourceDirectory=$(pwd)                          \
     -DjavacSource=1.5  -DjavacTarget=1.5              \
     -DbuildDirectory=$(pwd)/build                     \
     -Dbuilder=%{_datadir}/eclipse/plugins/org.eclipse.pde.build/templates/package-build \
     -f %{_datadir}/eclipse/plugins/org.eclipse.pde.build/scripts/build.xml \
     -vmargs -Duser.home=$homedir

%install
rm -rf $RPM_BUILD_ROOT
install -d -m755 ${RPM_BUILD_ROOT}/%{_datadir}/eclipse
unzip -q -d $RPM_BUILD_ROOT%{_datadir}/eclipse/.. \
            build/rpmBuild/org.python.pydev.feature.zip

pushd $RPM_BUILD_ROOT%{_datadir}/eclipse/plugins
rm -rf org.python.pydev.core_%{version}/commons-codec.jar
ln -sf %{_javadir}/jakarta-commons-codec.jar \
       org.python.pydev.core_%{version}/commons-codec.jar

mkdir org.python.pydev.core_%{version}/lib
ln -sf %{_javadir}/junit.jar \
       org.python.pydev.core_%{version}/lib/junit.jar

rm -rf org.python.pydev.jython_%{version}/jython.jar
ln -sf %{_javadir}/jython.jar \
       org.python.pydev.jython_%{version}/jython.jar
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
%defattr(-,root,root,-)
%{_datadir}/eclipse/features/org.python.pydev*
%{_datadir}/eclipse/plugins/org.python.pydev_*
%{_datadir}/eclipse/plugins/org.python.pydev.ast*
%{_datadir}/eclipse/plugins/org.python.pydev.core*
%{_datadir}/eclipse/plugins/org.python.pydev.debug*
%{_datadir}/eclipse/plugins/org.python.pydev.help*
%{_datadir}/eclipse/plugins/org.python.pydev.parser*
%{_datadir}/eclipse/plugins/org.python.pydev.templates*
%{_datadir}/eclipse/plugins/org.python.pydev.jython*
%{_datadir}/eclipse/plugins/org.python.pydev.refactoring*

%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif
