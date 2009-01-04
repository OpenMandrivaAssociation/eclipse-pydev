Epoch: 1

%define eclipse_base     %{_libdir}/eclipse
%define gcj_support         0

Summary:          Eclipse Python development plug-in
Name:             eclipse-pydev
Version:          1.3.24
Release:          %mkrel 0.0.1
License:          Eclipse Public License
URL:              http://pydev.sourceforge.net/
Group:            Development/Python

Source0:          http://downloads.sourceforge.net/pydev/org.python.pydev.feature-src-1_3_20.zip
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
BuildRequires:    zip
BuildRequires:    eclipse-pde
# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
BuildRequires:    eclipse-mylyn
BuildRequires:    eclipse-mylyn-ide
%endif
BuildRequires:    java-rpmbuild >= 0:1.5
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
#patch0

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

%build
%{eclipse_base}/buildscripts/pdebuild \
  -a "-DjavacSource=1.5  -DjavacTarget=1.5" \
  -f org.python.pydev.feature

# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
%{eclipse_base}/buildscripts/pdebuild \
  -a "-DjavacSource=1.5  -DjavacTarget=1.5" \
  -d mylyn \
  -f org.python.pydev.mylyn.feature
%endif


%install
rm -rf $RPM_BUILD_ROOT
installDir=${RPM_BUILD_ROOT}/%{_datadir}/eclipse/dropins/pydev
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
#rm -rf org.python.pydev.core_%{version}/commons-codec.jar
#ln -sf %{_datadir}/java/jakarta-commons-codec.jar \
#       org.python.pydev.core_%{version}/commons-codec.jar

#mkdir org.python.pydev.core_%{version}/lib
#ln -sf %{_datadir}/java/junit.jar \
#       org.python.pydev.core_%{version}/lib/junit.jar
#
#rm -rf org.python.pydev.jython_%{version}/jython.jar
#ln -sf %{_datadir}/java/jython.jar \
#       org.python.pydev.jython_%{version}/jython.jar
popd

# rename cgi.py's shebang from /usr/local/bin/python to /usr/bin/env python
#sed -i 's/\/usr\/local\/bin\/python/\/usr\/bin\/env python/' ${RPM_BUILD_ROOT}%{_datadir}/eclipse/dropins/pydev/eclipse/plugins/org.python.pydev.jython_%{version}/Lib/cgi.py
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
%{_datadir}/eclipse/dropins/pydev
# no xmlrpc3 -> no mylyn on ppc64 due to:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=239123
%ifnarch ppc64
%{_datadir}/eclipse/dropins/pydev-mylyn
%endif

%{gcj_files}

