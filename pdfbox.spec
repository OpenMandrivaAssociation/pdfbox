%{?_javapackages_macros:%_javapackages_macros}
Name:           pdfbox
Version:        1.8.7
Release:        1.3
Summary:        Java library for working with PDF documents
Group:		Development/Java
License:        ASL 2.0
URL:            http://pdfbox.apache.org/
Source0:        http://www.apache.org/dist/pdfbox/%{version}/%{name}-%{version}-src.zip
#Don't download anything
Patch0:         %{name}-nodownload.patch
#Use sysytem bitream-vera-sans-fonts instead of bundled fonts
Patch1:         %{name}-1.2.0-bitstream.patch

Patch2:         pdfbox-1.8.7-port-to-bouncycastle1.50.patch

BuildRequires:  ant
BuildRequires:  maven-local
BuildRequires:  maven-install-plugin
BuildRequires:  maven-war-plugin
BuildRequires:  apache-commons-logging
BuildRequires:  apache-rat-plugin
BuildRequires:  fonts-ttf-bitstream-vera
BuildRequires:  bouncycastle-mail
BuildRequires:  cobertura-maven-plugin
BuildRequires:  fontconfig
BuildRequires:  icu4j
BuildRequires:  javacc-maven-plugin
BuildRequires:  junit
%if 0%{?fedora} >= 18
BuildRequires:  lucene
%else
BuildRequires:  lucene-demo >= 2.4.1
%endif
BuildRequires:  pcfi
BuildRequires:  log4j12

BuildArch:      noarch

Requires:       java >= 1:1.6.0
Requires:       fonts-ttf-bitstream-vera

Obsoletes:      %{name}-app <= 1.6.0-4
Provides:       %{name}-app = %{version}-%{release}

%description
Apache PDFBox is an open source Java PDF library for working with PDF
documents. This project allows creation of new PDF documents, manipulation of
existing documents and the ability to extract content from documents. Apache
PDFBox also includes several command line utilities. Apache PDFBox is
published under the Apache License v2.0.

%package examples
Summary:        Examples for %{name}

%description examples
This package contains examples for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Provides:       fontbox-javadoc = %{version}-%{release}
Obsoletes:      fontbox-javadoc < %{version}-%{release}
Provides:       jempbox-javadoc = %{version}-%{release}
Obsoletes:      jempbox-javadoc < %{version}-%{release}

%description javadoc
This package contains the API documentation for %{name}.

%package ant
Summary:        Apache PDFBox for Ant

%description ant
%{summary}.

%package -n fontbox
Summary:        Apache FontBox

%description -n fontbox
FontBox is a Java library used to obtain low level information from font
files. FontBox is a subproject of Apache PDFBox.

%package -n jempbox
Summary:        Apache JempBox

%description -n jempbox
JempBox is an open source Java library that implements Adobe's XMP(TM)
specification. JempBox is a subproject of Apache PDFBox.

%package -n preflight
Summary:        Apache Preflight

%description -n preflight
The Apache Preflight library is an open source Java tool that implements 
a parser compliant with the ISO-19005 (PDF/A) specification. Preflight is a 
subproject of Apache PDFBox.

%package -n xmpbox
Summary:        Apache XmpBox

%description -n xmpbox
The Apache XmpBox library is an open source Java tool that implements Adobe's
XMP(TM) specification.  It can be used to parse, validate and create xmp
contents.  It is mainly used by subproject preflight of Apache PDFBox. 
XmpBox is a subproject of Apache PDFBox.

%prep
%setup -q
%patch0 -p1 -b .nodownload
%patch1 -p1 -b .bitstream

# Skip testImageIOUtils
# https://issues.apache.org/jira/browse/PDFBOX-2084
sed -i -e "/TestImageIOUtils.java/d" pdfbox/pom.xml
# Remove unpackaged deps for the above tests
%pom_remove_dep net.java.dev.jai-imageio:jai-imageio-core-standalone pdfbox
%pom_remove_dep com.levigo.jbig2:levigo-jbig2-imageio pdfbox
rm -rf pdfbox/src/test/java/org/apache/pdfbox/util/TestImageIOUtils.java \
 pdfbox/src/test/java/org/apache/pdfbox/pdmodel/graphics/xobject/PDJpegTest.java \
 pdfbox/src/test/java/org/apache/pdfbox/pdmodel/graphics/xobject/PDCcittTest.java
sed -i -e /PDJpegTest/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java
sed -i -e /PDCcittTest/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java
sed -i -e /TestImageIOUtils/d pdfbox/src/test/java/org/apache/pdfbox/TestAll.java

%pom_remove_dep javax.activation:activation preflight

%pom_disable_module war

sed -i.ant "s|<artifactId>ant-nodeps</artifactId>|<artifactId>ant</artifactId>|" pom.xml */pom.xml

sed -i.log4j12 "s|<version>1.2.12</version>|<version>1.2.17</version>|" preflight*/pom.xml

#Disable lucene, not compatible with lucene 3.6
%pom_disable_module lucene
#Use jdk16 version of bcprov
sed -i -e s/jdk15/jdk16/g */pom.xml
# Don't build app (it's just a bundle of everything)
sed -i -e /app/d pom.xml
find -name '*.class' -delete
find -name '*.jar' -delete
#Fix line endings
sed -i -e 's|\r||' RELEASE-NOTES.txt
#Remove META-INF file that does not exist
sed -i -e '/META-INF/d' pdfbox/pom.xml
#Remove included fonts
rm -r pdfbox/src/main/resources/org/apache/pdfbox/resources/ttf

%pom_add_dep org.bouncycastle:bcpkix-jdk15on:1.50 %{name}
%patch2 -p0 -b .bouncycastle1.50

# TODO
rm -rf examples/src/main/java/org/apache/pdfbox/examples/signature/CreateSignature.java \
 examples/src/main/java/org/apache/pdfbox/examples/signature/CreateVisibleSignature.java

# Disable filtering
sed -i -e /filtering/d examples/pom.xml

%build
# install all libraries in _javadir
# NOTE: current guideline require all libraries must be installed in _javadir/%%name when JARs are > 2
%mvn_file :jempbox jempbox
%mvn_file :%{name} %{name}
%mvn_file :%{name}-ant %{name}-ant
%mvn_file :%{name}-examples %{name}-examples
%mvn_file :preflight preflight
%mvn_file :xmpbox xmpbox
%mvn_file :fontbox fontbox

# Merge paret poms in main package
%mvn_package :%{name} %{name}
%mvn_package :%{name}-parent %{name}
%mvn_package :%{name}-reactor %{name}

%mvn_package :fontbox fontbox
%mvn_package :jempbox jempbox
%mvn_package :preflight preflight
%mvn_package :xmpbox xmpbox

%mvn_build -s -- -Dadobefiles.jar=$(build-classpath pcfi)

%install
%mvn_install

#TODO - install/ship war

%files -f .mfiles-%{name}
%doc LICENSE.txt NOTICE.txt README.txt RELEASE-NOTES.txt

%files examples -f .mfiles-%{name}-examples
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%files ant -f .mfiles-%{name}-ant
%doc LICENSE.txt NOTICE.txt

%files -n fontbox -f .mfiles-fontbox
%doc LICENSE.txt NOTICE.txt

%files -n jempbox -f .mfiles-jempbox
%doc LICENSE.txt NOTICE.txt

%files -n preflight -f .mfiles-preflight
%doc LICENSE.txt NOTICE.txt

%files -n xmpbox -f .mfiles-xmpbox
%doc LICENSE.txt NOTICE.txt

%changelog
* Thu Oct 30 2014 gil cattaneo <puntogil@libero.it> 1.8.7-1
- update to 1.8.7

* Fri Sep 26 2014 gil cattaneo <puntogil@libero.it> 1.8.5-3
- build fix for bouncycastle 1.50 (rhbz#1100445)
- adapt to current guideline
- remove lucene sub package
- force log4j12 usage

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 21 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.5-1
- Add patch to disable test that needs missing deps
- Remove missing test deps from pdbbox pom
- Use junit instead of junit4

* Fri May 2 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.5-1
- Update to 1.8.5

* Sat Feb 1 2014 Orion Poplawski <orion@cora.nwra.com> - 1.8.4-1
- Update to 1.8.4

* Mon Dec 2 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.3-1
- Update to 1.8.3
- New pcfi.jar location

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 14 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.2-1
- Update to 1.8.2
- Drop unneeded maven BRs

* Wed Apr 17 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.1-1
- Update to 1.8.1

* Thu Mar 28 2013 Orion Poplawski <orion@cora.nwra.com> - 1.8.0-1
- Update to 1.8.0
- Add preflight and xmpbox sub-packages

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.7.0-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Sep 24 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-4
- Drop lucene sub-package for now, not compatible with lucene 3.6

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 3 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-2
- Fix javadocs -> javadoc typo

* Tue Jul 3 2012 Orion Poplawski <orion@cora.nwra.com> - 1.7.0-1
- Update to 1.7.0
- Add examples sub-package
- Add BR on bitstream font and fontconfig

* Wed Apr 18 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-5
- Drop pdfbox-app sub-package, nothing but a bundle (bug #813712)

* Wed Feb 1 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-4
- Add proper provides/obsoletes to javadoc sub-package (bug #785396)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Oct 24 2011 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-2
- BR separately packaged pcfi

* Wed Aug 10 2011 Orion Poplawski <orion@cora.nwra.com> - 1.6.0-1
- Update to 1.6.0
- Add pcfi-2010.08.09.jar to sources
- Drop depmap
- Use apache-commons-logging
- Other cleanup

* Fri Jun 3 2011 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-2
- Use maven 3
- Single javadoc package

* Thu Mar 10 2011 Orion Poplawski <orion@cora.nwra.com> - 1.5.0-1
- Update to 1.5.0

* Tue Dec 28 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.0-2
- Create sub-packages
- Use depmap file

* Tue Dec 21 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.0-1
- Update to 1.4.0

* Sat Nov 6 2010 Orion Poplawski <orion@cora.nwra.com> - 1.3.1-1
- Update to 1.3.1

* Fri Aug 13 2010 Orion Poplawski <orion@cora.nwra.com> - 1.3.0-0.1
- Update to 1.3.0-SNAPSHOT

* Thu Jul 15 2010 Orion Poplawski <orion@cora.nwra.com> - 1.2.1-1
- Update to 1.2.1

* Thu Jul 1 2010 Orion Poplawski <orion@cora.nwra.com> - 1.2.0-1
- Update to 1.2.0
- Drop gcj support

* Mon Oct 19 2009 Orion Poplawski <orion@cora.nwra.com> - 0.8.0-2
- Add Requires

* Thu Oct 15 2009 Orion Poplawski <orion@cora.nwra.com> - 0.8.0-1
- Initial Fedora package

