# psyco: Bug 483357 - Empty eclipse-pydev-debuginfo
%global debug_package %{nil}
%global qualifier 2011020317
%global _python_bytecompile_errors_terminate_build 0


%global eclipse_base        %{_libdir}/eclipse
%global install_loc         %{_libdir}/eclipse/dropins

Summary:          Eclipse Python development plug-in
Name:             eclipse-pydev
Version:          1.6.5
Release:          1
Epoch:		  1
License:          EPL
URL:              http://pydev.org
Group:            Development/Java

Source0:          http://downloads.sourceforge.net/project/pydev/pydev/Pydev%20%{version}/org.python.pydev-%{version}.%{qualifier}-sources.zip
Patch0:           use-piccolo2d-bundle.patch
Patch1:           piccolo-swtimage-dispose.patch
Patch2:           pydev-removeruntimeerror.patch
Patch3:           remove-red-core.patch
BuildRequires:    java-devel >= 1.5.0

Requires:         eclipse-platform
Requires:         python
# Psyco has not yet been ported to Python 2.7, so this dependency is
# temporarily disabled: go ahead and re-enable it once a python-psyco
# which works with Python 2.7 is built - AdamW 2010/08/06
# Psyco is available only on x86
#ifarch %%{ix86}
#Requires:         python-psyco
#endif
Requires:         apache-commons-codec >= 1.3
Requires:         apache-commons-logging
Requires:         xmlrpc3-common
Requires:         xmlrpc3-client
Requires:         xmlrpc3-server
Requires:         junit >= 3.8.1
Requires:         jython >= 2.2
Requires:         pylint
Requires:         piccolo2d >= 1.3-1
Requires:         Django
BuildRequires:    eclipse-pde
BuildRequires:    eclipse-mylyn
BuildRequires:    jpackage-utils >= 0:1.5
BuildRequires:    junit >= 3.8.1
BuildRequires:    apache-commons-codec >= 1.3
BuildRequires:    apache-commons-logging
BuildRequires:    ws-commons-util
BuildRequires:    xmlrpc3-common
BuildRequires:    xmlrpc3-client
BuildRequires:    xmlrpc3-server
BuildRequires:    jython >= 2.2
BuildRequires:    piccolo2d >= 1.3-1

# This package can not be noarch because psyco is a x86 package.
#BuildArch:        noarch

%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%package  mylyn
Summary:  Pydev Mylyn Focused UI
Requires: eclipse-mylyn
Requires: %{name} = 1:%{version}-%{release}
Group: Development/Java

%description mylyn
Mylyn Task-Focused UI extensions for Pydev.

%prep
%setup -q -c
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
#fix mylyn plugin version
sed --in-place 's:version="0.3.0":version="%{version}.%{qualifier}":' features/org.python.pydev.mylyn.feature/feature.xml

# remove pre-generated build files
find . -name build.xml | xargs rm

#remove piccolo2d sources, we use the system one
rm -fr plugins/com.python.pydev/src/edu

# remove pre-built jars
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

# link to system jars
ln -sf %{_javadir}/commons-codec.jar \
       plugins/org.python.pydev.core/commons-codec.jar

ln -sf %{_javadir}/junit.jar \
       plugins/org.python.pydev.core/junit.jar

ln -sf %{_javadir}/jython.jar \
       plugins/org.python.pydev.jython/jython.jar

ln -sf %{_javadir}/commons-logging.jar \
       plugins/org.python.pydev.debug/commons-logging-1.1.jar

ln -sf %{_javadir}/ws-commons-util.jar \
       plugins/org.python.pydev.debug/ws-commons-util-1.0.2.jar

ln -sf %{_javadir}/xmlrpc3-client.jar \
       plugins/org.python.pydev.debug/xmlrpc-client-3.1.jar

ln -sf %{_javadir}/xmlrpc3-common.jar \
       plugins/org.python.pydev.debug/xmlrpc-common-3.1.jar

ln -sf %{_javadir}/xmlrpc3-server.jar \
       plugins/org.python.pydev.debug/xmlrpc-server-3.1.jar

# enable when tests are used
#ln -sf %%{_datadir}/java/jflex.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/JFlex.jar

# enable when tests are used
#ln -sf %%{_datadir}/java/xpp3-minimal.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xpp3_min-1.1.3.4.O.jar

# enable when tests are used
#ln -sf %%{_datadir}/java/xstream.jar \
#       plugins/org.python.pydev.refactoring/tests/lib/xstream-1.2.1.jar


mkdir orbitDeps
pushd orbitDeps
ln -s %{_javadir}/piccolo2d/piccolo2d-core.jar piccolo2d-core.jar
ln -s %{_javadir}/piccolo2d/piccolo2d-extras.jar piccolo2d-extras.jar
ln -s %{_javadir}/piccolo2d/piccolo2d-swt.jar piccolo2d-swt.jar
popd

%build
%{eclipse_base}/buildscripts/pdebuild \
  -d mylyn \
  -f org.python.pydev.feature -a "-DjavacSource=1.5 -DjavacTarget=1.5" -o `pwd`/orbitDeps

%{eclipse_base}/buildscripts/pdebuild \
  -d mylyn \
  -f org.python.pydev.mylyn.feature -a "-DjavacSource=1.5 -DjavacTarget=1.5" -o `pwd`/orbitDeps

%install
installDir=${RPM_BUILD_ROOT}/%{install_loc}/pydev
install -d -m755 $installDir
install -d -m755 ${installDir}-mylyn

# pydev main feature
unzip -q -d $installDir build/rpmBuild/org.python.pydev.feature.zip

# pydev mylyn feature
unzip -q -d ${installDir}-mylyn build/rpmBuild/org.python.pydev.mylyn.feature.zip

# deal with linked deps
pushd $installDir/eclipse/plugins
ln -s %{_javadir}/piccolo2d/piccolo2d-core.jar piccolo2d-core.jar
ln -s %{_javadir}/piccolo2d/piccolo2d-extras.jar piccolo2d-extras.jar
ln -s %{_javadir}/piccolo2d/piccolo2d-swt.jar piccolo2d-swt.jar
rm -rf org.python.pydev.core_%{version}.%{qualifier}/commons-codec.jar
ln -sf %{_javadir}/commons-codec.jar \
       org.python.pydev.core_%{version}.%{qualifier}/commons-codec.jar

mkdir org.python.pydev.core_%{version}.%{qualifier}/lib
ln -sf %{_javadir}/junit.jar \
       org.python.pydev.core_%{version}.%{qualifier}/lib/junit.jar

rm -rf org.python.pydev.debug_%{version}.%{qualifier}/commons-logging-1.1.jar
ln -sf %{_javadir}/commons-logging.jar \
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

%files
%defattr(-,root,root,-)
%{install_loc}/pydev

%files mylyn
%defattr(-,root,root,-)
%{install_loc}/pydev-mylyn

