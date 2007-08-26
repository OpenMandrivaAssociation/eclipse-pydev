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
Release:          %mkrel 0.1.1
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
aot-compile-rpm
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

%changelog
* Fri Aug 24 2007 Ben Konrath <bkonrath@redhat.com> 1:1.3.8-1
- 1.3.8

* Fri Apr 27 2007 Igor Foox <ifoox@redhat.com> 1:1.3.1-5
- Add runtime dependancy on the JDT.
- Reorganize Requires and BuildRequires.

* Mon Apr 02 2007 Andrew Overholt <overholt@redhat.com> 1:1.3.1-4
- Remove some whitespace, fix lines > 80 characters.
- Remove unnecessary rm of junit.jar.
- pushd to a deeper directory to fix long lines.
- Add missing popd.
- Typo in buildroot.

* Mon Apr 02 2007 Igor Foox <ifoox@redhat.com> 1:1.3.1-3
- Remove ExclusiveArch.

* Sun Apr 01 2007 Igor Foox <ifoox@redhat.com> 1:1.3.1-2
- Add Jython as a BuildRequires and Requires.
- Fix buildroot.
- Add dist tag.
- Remove pkg_summary and eclipse_name macros.
- Remove eclipse-jdt and eclipse-pde from BR as they are required by PDE.
- Fix permissions on defattr.
- Fix long lines.
- Renumber and comment patches.
- Update and simplify source drop generation comment.

* Tue Mar 27 2007 Igor Foox <ifoox@redhat.com> 1:1.3.1-1
- Update to PyDev 1.3.1.

* Mon Mar 26 2007 Igor Foox <ifoox@redhat.com> 1:1.3.0-2
- Add dependency on jython.

* Sun Mar 25 2007 Igor Foox <ifoox@redhat.com> 1:1.3.0-1
- Update to version 1.3.0.
- Update fetch script to include refactoring package.
- Fixeup changelog epochs.
- Remove #! lines from .py files.

* Sat Mar 24 2007 Igor Foox <ifoox@redhat.com> 1:1.2.5-2
- Update to version 1.2.5.
- Include Jython functionality again.
- Fix spacing issues.
- Remove backport to Java 1.4. 
- Change build method to package-build.
- Include script to create the tarball.

* Wed Jun 28 2006 Igor Foox <ifoox@redhat.com> 1:1.1.0-1
- Updated to version 1.1.0 (still backported)
- Excluded Jython functionality
- Removed _fc from version
- Indented

* Thu Feb 09 2006 Igor Foox <ifoox@redhat.com> 1:1.0.6_fc-1
- Building backported version.

* Thu Feb 09 2006 Andrew Overholt <overholt@redhat.com> 1:0.9.3_fc-14
- Build against 3.1.2.

* Fri Dec 16 2005 Andrew Overholt <overholt@redhat.com> 1:0.9.3_fc-13
- Build against gcc 4.1.

* Thu Oct 27 2005 Andrew Overholt <overholt@redhat.com> 1:0.9.3_fc-12
- Re-build.

* Tue Aug 02 2005 Jeff Pound <jpound@redhat.com> 1:0.9.3_fc-11
- Add patch to make python 2.4 default (bz#164847).

* Fri Jul 15 2005 Andrew Overholt <overholt@redhat.com> 1:0.9.3_fc-10
- Use gbenson's new aot-compile-rpm.

* Fri Jul 08 2005 Jeff Pound <jpound@redhat.com> 1:0.9.3_fc-9
- Fix eclipse build specification to be arch independant.
- Fix build.properties javacDebugInfo flag (Robin Green bz#161534)
- Add -g compile option (Robin Green bz#161534)

* Tue Jul 05 2005 Jeff Pound <jpound@redhat.com> 1:0.9.3_fc-8
- Apply Robin Greens patch to explicitly specify archive format (bz#162517)
- Fix spec file description.

* Tue Apr 26 2005 Andrew Overholt <overholt@redhat.com> 1:0.9.3_fc-7
- Re-organize and make use of scripts.
- Remove old tarball from sources.

* Tue Apr 26 2005 Jeff Pound <jpound@redhat.com> 1:0.9.3_fc-6
- Swap zip logic for tarball logic.
- Upgrade to 0.9.3.
- Remove 3.1 compat patch (included in 0.9.3).

* Fri Mar 4 2005 Phil Muldoon <pmuldoon@redhat.com> 1:0.9.0-4_fc
- Added x86_64 to ExclusiveArch

* Thu Mar 3 2005 Jeffrey Pound <jpound@redhat.com> 1:0.9.0-3_fc
- Rewrite for native build.
- Change gcc4 to gcc.
- Add python as requirement.
- Remove -g option for gcj.

* Tue Feb 08 2005 Jeff Pound <jpound@redhat.com> 1:0.9.0-1_fc
- Initial version
