Epoch: 1

%define eclipse_base     %{_libdir}/eclipse
%define install_loc      %{_libdir}/eclipse/dropins
%define gcj_support         0

%define major     1
%define minor     4
%define maint     4

%define qualifier 2636

Summary:          Eclipse Python development plug-in
Name:             eclipse-pydev
Version:          %{major}.%{minor}.%{maint}
Release:          %mkrel 0.0.2
License:          Eclipse Public License
URL:              http://pydev.sourceforge.net/
Group:            Development/Python
Source0:          http://downloads.sourceforge.net/pydev/org.python.pydev.feature-%{major}.%{minor}.%{maint}.%{qualifier}-sources.zip
Source1:          org.python.pydev.mylyn.feature-fetched-src-pydev_1_3_7.tar.bz2
Source2:          fetch-pydev-mylyn.sh

# Back-port from HEAD
# http://pydev.cvs.sourceforge.net/pydev/org.python.pydev/src/org/python/copiedfromeclipsesrc/CopiedWorkbenchLabelProvider.java?revision=1.3&view=markup
#Patch0:           %{name}-%{version}-compileerrors.patch


%if %{gcj_support}
BuildRequires:    java-1.5.0-gcj-devel >= 1.5.0
%else
BuildRequires:    java-devel >= 1.5.0
%endif

Requires:         eclipse-jdt
Requires:         python
Requires:         commons-codec >= 1.3
Requires:         junit >= 3.8.1
Requires:         jython >= 2.2
Requires:         jakarta-commons-codec >= 1.3
Requires:         jakarta-commons-logging
Requires:         xmlrpc3-common
Requires:         xmlrpc3-client
Requires:         xmlrpc3-server
Requires:         junit >= 3.8.1
Requires:         jython >= 2.2
%ifarch %{ix86}
Requires:         python-psyco
%endif
BuildRequires:    zip
BuildRequires:    eclipse-pde
# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
BuildRequires:    eclipse-mylyn
BuildRequires:    eclipse-mylyn-ide
%endif
BuildRequires:    commons-codec >= 1.3
BuildRequires:    eclipse-pde
BuildRequires:    eclipse-mylyn
BuildRequires:    jpackage-utils >= 0:1.5
BuildRequires:    junit >= 3.8.1
BuildRequires:    jakarta-commons-codec >= 1.3
BuildRequires:    jakarta-commons-logging
BuildRequires:    ws-commons-util
BuildRequires:    xmlrpc3-common
BuildRequires:    xmlrpc3-client
BuildRequires:    xmlrpc3-server
BuildRequires:    jython >= 2.2
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root

%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%package  mylyn
Summary:  Pydev Mylyn Focused UI
Requires: eclipse-mylyn
Requires: %{name} = %{epoch}:%{version}-%{release}
Group: Development/Python

%description mylyn
Mylyn Task-Focused UI extensions for Pydev.

%prep
%setup -q -c

tar jxf %{SOURCE1}

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

rm -f plugins/org.python.pydev.debug/commons-logging-1.1.jar
ln -sf %{_javadir}/jakarta-commons-logging.jar \
       plugins/org.python.pydev.debug/commons-logging-1.1.jar

rm -f plugins/org.python.pydev.debug/ws-commons-util-1.0.2.jar
ln -sf %{_javadir}/ws-commons-util.jar \
       plugins/org.python.pydev.debug/ws-commons-util-1.0.2.jar

rm -f plugins/org.python.pydev.debug/xmlrpc-client-3.1.jar
ln -sf %{_javadir}/xmlrpc3-client.jar \
       plugins/org.python.pydev.debug/xmlrpc-client-3.1.jar

rm -f plugins/org.python.pydev.debug/xmlrpc-common-3.1.jar
ln -sf %{_javadir}/xmlrpc3-common.jar \
       plugins/org.python.pydev.debug/xmlrpc-common-3.1.jar

rm -f plugins/org.python.pydev.debug/xmlrpc-server-3.1.jar
ln -sf %{_javadir}/xmlrpc3-server.jar \
       plugins/org.python.pydev.debug/xmlrpc-server-3.1.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/JFlex.jar

# enable when tests are used
#ln -sf %{_datadir}/java/jflex.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/JFlex.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/xpp3_min-1.1.3.4.O.jar
# enable when tests are used
#ln -sf %{_datadir}/java/xpp3-minimal.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xpp3_min-1.1.3.4.O.jar

rm -f plugins/org.python.pydev.refactoring/tests/lib/xstream-1.2.1.jar
# enable when tests are used
#ln -sf %{_datadir}/java/xstream.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xstream-1.2.1.jar

rm -f plugins/org.python.pydev.refactoring/contrib/ch/hsr/ukistler/astgraph/jgraph.jar

%build
%{eclipse_base}/buildscripts/pdebuild \
  -f org.python.pydev.feature

%{eclipse_base}/buildscripts/pdebuild \
  -d mylyn \
  -f org.python.pydev.mylyn.feature

# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
%{eclipse_base}/buildscripts/pdebuild \
  -d mylyn \
  -f org.python.pydev.mylyn.feature
%endif

%install
rm -rf $RPM_BUILD_ROOT
installDir=${RPM_BUILD_ROOT}/%{install_loc}/pydev
install -d -m755 $installDir
install -d -m755 ${installDir}-mylyn

# pydev main feature
unzip -q -d $installDir build/rpmBuild/org.python.pydev.feature.zip

# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
# pydev mylyn feature
unzip -q -d ${installDir}-mylyn build/rpmBuild/org.python.pydev.mylyn.feature.zip
%endif

# deal with linked deps
pushd $installDir/eclipse/plugins
rm -rf org.python.pydev.core_%{version}.%{qualifier}/commons-codec.jar
ln -sf %{_javadir}/jakarta-commons-codec.jar \
       org.python.pydev.core_%{version}.%{qualifier}/commons-codec.jar

mkdir org.python.pydev.core_%{version}.%{qualifier}/lib
ln -sf %{_javadir}/junit.jar \
       org.python.pydev.core_%{version}.%{qualifier}/lib/junit.jar

rm -rf org.python.pydev.debug_%{version}.%{qualifier}/commons-logging-1.1.jar
ln -sf %{_javadir}/jakarta-commons-logging.jar \
       org.python.pydev.debug_%{version}.%{qualifier}/commons-logging-1.1.jar

rm -rf org.python.pydev.debug_%{version}.%{qualifier}/ws-commons-util-1.0.2.jar
ln -sf %{_javadir}/ws-commons-util.jar \
       org.python.pydev.debug_%{version}.%{qualifier}/ws-commons-util-1.0.2.jar

rm -f org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-client-3.1.jar
ln -sf %{_javadir}/xmlrpc3-client.jar \
       org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-client-3.1.jar

rm -f org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-common-3.1.jar
ln -sf %{_javadir}/xmlrpc3-common.jar \
       org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-common-3.1.jar

rm -f org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-server-3.1.jar
ln -sf %{_javadir}/xmlrpc3-server.jar \
       org.python.pydev.debug_%{version}.%{qualifier}/xmlrpc-server-3.1.jar

rm -rf org.python.pydev.jython_%{version}.%{qualifier}/jython.jar
ln -sf %{_javadir}/jython.jar \
       org.python.pydev.jython_%{version}.%{qualifier}/jython.jar
popd

# rename cgi.py's shebang from /usr/local/bin/python to /usr/bin/env python
sed -i 's/\/usr\/local\/bin\/python/\/usr\/bin\/env python/' ${RPM_BUILD_ROOT}%{install_loc}/pydev/eclipse/plugins/org.python.pydev.jython_%{version}.%{qualifier}/Lib/cgi.py
# convert .py$ files from mode 0644 to mode 0755
chmod 0755 `find ${RPM_BUILD_ROOT} -name '*\.py' -perm 0644 | xargs`

# convert '\r\n' end-of-lines to *unix-like '\n'
# sed -i 's/\r//' `find ${RPM_BUILD_ROOT} -name '*\.py' | xargs`

%{gcj_compile}

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
%{install_loc}/pydev
# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123

%files mylyn
%{install_loc}/pydev-mylyn

%{gcj_files}
