# FIXME: As of Mar 2007, the latest release is 1.2.9, but Debian
# provides a source tarball plus a non-generics backport.

Epoch: 0

%define gcj_support      1
%define pkg_summary      Eclipse Python development plug-in
%define section          free
%define eclipse_name     eclipse
%define version_major    1
%define version_minor    2
%define version_majmin   %{version_major}.%{version_minor}
%define version_micro    5
%define eclipse_base     %{_datadir}/%{eclipse_name}
%define eclipse_lib_base %{_libdir}/%{eclipse_name}

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch     x86
%else
%define eclipse_arch     %{_arch}
%endif

Summary:        %{pkg_summary} 
Name:           %{eclipse_name}-pydev
Version:        %{version_majmin}.%{version_micro}
Release:        %mkrel 1.2
License:        CPL
Group:          Development/Java
URL:            http://pydev.sourceforge.net/
Requires:       bicyclerepair
Requires:       eclipse-platform
Requires:       jakarta-commons-codec
Requires:       jython
Requires:       python
# Note that following the Eclipse Releng process we do not distribute a 
# real .tar.gz file.  Instead, you must build it by hand.  The way to do 
# this is to check out org.python.pydev.releng.  Edit maps/pydev.map 
# to refer to the# tag appropriate to the release.  Then run the "fetch" 
# target to fetch everything.  Package this up, such that the tar
# file unpacks a new "org.python.pydev.releng" directory with all the
# contents.  See the java command to see how to invoke
# things in the releng build.xml.
Source0:        http://ftp.debian.org/debian/pool/main/e/eclipse-pydev/eclipse-pydev_1.2.5.orig.tar.gz
Patch0:         eclipse-pydev-1.2.5-backport-megapatch.patch
Patch1:         eclipse-pydev-remove-brm.patch
Patch2:         eclipse-pydev-remove-commons-codec.patch
Patch3:         eclipse-pydev-remove-jython.patch
Patch4:         eclipse-pydev-releng.patch
Patch5:         eclipse-pydev-setup-jython.patch
BuildRequires:  eclipse-platform
BuildRequires:  eclipse-jdt
BuildRequires:  eclipse-pde
BuildRequires:  ant >= 0:1.6
BuildRequires:  eclipse-platform
BuildRequires:  jakarta-commons-codec
BuildRequires:  java >= 0:1.4.2
BuildRequires:  java-devel >= 0:1.4.2
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  jython
%if %{gcj_support}
BuildRequires:  gcc-java >= 0:4.0.1
BuildRequires:  java-gcj-compat-devel >= 0:1.0.33
Requires(post): java-gcj-compat >= 0:1.0.33
Requires(postun): java-gcj-compat >= 0:1.0.33
%else
BuildArch:     noarch
BuildRequires: java-devel >= 0:1.4.2
%endif
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The eclipse-pydev package contains Eclipse plugins for
Python development.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%build

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
SDK=$(cd SDK && pwd)

mkdir home

homedir=$(cd home > /dev/null && pwd)

pushd `pwd` 
cd org.python.pydev.releng

# Call eclipse headless to process pydev releng build scripts
# need -Dosgi.install.area for http://gcc.gnu.org/bugzilla/show_bug.cgi?id=20198
%{java} -cp $SDK/startup.jar:$(build-classpath jakarta-commons-codec jython) \
    -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration \
    -Duser.home=$homedir \
    -Dosgi.install.area=%{eclipse_base} \
     org.eclipse.core.launcher.Main \
    -application org.eclipse.ant.core.antRunner \
    -DjavacFailOnError=true \
    -DdontUnzip=true \
    -DbaseLocation=%{eclipse_base} \
    -Dpde.build.scripts=$(echo $SDK/plugins/org.eclipse.pde.build_*)/scripts \
    -DdontFetchAnything=true \
    -DEC_HOME=%{eclipse_base} \
    -DEC_WORKSPACE=`pwd`/.. \
    -DPYDEV_VERSION=%{version} \
    -DBUILD_ID=`echo %{version} | %{__sed} -e 's/\./_/g'`
popd

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{eclipse_base}

# Dump the files from the releng tarball into the build root
for file in $(pwd)/org.python.pydev.releng/results/`echo %{version} | sed -e 's/\./_/g'`/*.zip; do
  case $file in
    *org.python.pydev*)
      # The ".." is needed since the zip files contain "eclipse/foo".  
      (cd %{buildroot}%{eclipse_base}/.. && %{_bindir}/unzip $file)
      ;;
  esac
done

%{__rm} -r %{buildroot}%{eclipse_base}/../features %{buildroot}%{eclipse_base}/../plugins

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%{_bindir}/find %{buildroot} -type f -name "*.py" \
                       -o -name fulltest.sh \
                       -o -name symilar \
                       -o -name noext \
                       -o -name pylint-gui \
                       -o -name pylint | %{_bindir}/xargs %{__chmod} 755

%clean 
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%{eclipse_base}/features/org.python.pydev*
%{eclipse_base}/plugins/org.python.pydev*
%if %{gcj_support}
%{_libdir}/gcj/%{name}
%endif


