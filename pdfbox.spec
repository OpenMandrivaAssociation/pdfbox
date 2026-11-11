Name:		pdfbox
Version:	2.0.37
Release:	1
Summary:	Java library for reading and writing PDF documents
Group:		Development/Java
License:	Apache-2.0
URL:		https://pdfbox.apache.org/
# Tag 2.0.37. No prebuilt jars or class files.
Source0:	https://github.com/apache/pdfbox/archive/refs/tags/%{version}.tar.gz#/pdfbox-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(commons-logging:commons-logging)
BuildRequires:	mvn(org.bouncycastle:bcprov-jdk18on)
BuildRequires:	mvn(org.bouncycastle:bcutil-jdk18on)
BuildRequires:	mvn(org.bouncycastle:bcpkix-jdk18on)

%description
Apache PDFBox %{version} reads and writes PDF documents. The Gradle
build catalog asks for pdfbox 2.0.24 without a strict pin, and this
2.0 release keeps that API. fontbox and xmpbox from the same tag are
installed beside it. Public-key encryption is compiled against Bouncy
Castle jdk18on and left optional, matching upstream.

%prep
%autosetup -n pdfbox-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
find xmpbox/src/main/java -name '*.java' > xmp.list
find fontbox/src/main/java -name '*.java' > font.list
find pdfbox/src/main/java -name '*.java' > pdf.list
test "$(wc -l < xmp.list)" -eq 74
test "$(wc -l < font.list)" -eq 104
test "$(wc -l < pdf.list)" -eq 611
mkdir -p classes-xmp classes-font classes-pdf
javac --release 8 -encoding UTF-8 -Xlint:-options -d classes-xmp @xmp.list
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp classes-xmp:%{_javadir}/commons-logging.jar \
	-d classes-font @font.list
/bin/cp -a fontbox/src/main/resources/. classes-font/
javac --release 8 -encoding UTF-8 -Xlint:-options \
	-cp classes-xmp:classes-font:%{_javadir}/commons-logging.jar:%{_javadir}/bcprov-jdk18on.jar:%{_javadir}/bcutil-jdk18on.jar:%{_javadir}/bcpkix-jdk18on.jar \
	-d classes-pdf @pdf.list
/bin/cp -a pdfbox/src/main/resources/. classes-pdf/

cat > manifest-pdf.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.apache.pdfbox

EOF
cat > manifest-font.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.apache.fontbox

EOF
cat > manifest-xmp.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.apache.xmpbox

EOF
jar cfm pdfbox.jar manifest-pdf.mf -C classes-pdf .
jar cfm fontbox.jar manifest-font.mf -C classes-font .
jar cfm xmpbox.jar manifest-xmp.mf -C classes-xmp .
jar i pdfbox.jar
jar i fontbox.jar
jar i xmpbox.jar
javap -verbose -cp pdfbox.jar org.apache.pdfbox.pdmodel.PDDocument | grep -F 'major version: 52'
javap -verbose -cp fontbox.jar org.apache.fontbox.ttf.TTFParser | grep -F 'major version: 52'
javap -verbose -cp xmpbox.jar org.apache.xmpbox.XMPMetadata | grep -F 'major version: 52'
for jar in pdfbox.jar fontbox.jar xmpbox.jar; do
	jar --describe-module --file "$jar" > "describe-${jar}.txt"
	if grep -F -q 'Unable to derive' "describe-${jar}.txt"; then
		cat "describe-${jar}.txt"
		exit 1
	fi
done

cat > pdfbox.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.pdfbox</groupId>
  <artifactId>pdfbox</artifactId>
  <version>2.0.37</version>
  <name>Apache PDFBox</name>
  <description>Java library for reading and writing PDF documents</description>
  <url>https://pdfbox.apache.org/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.apache.pdfbox</groupId>
      <artifactId>fontbox</artifactId>
      <version>2.0.37</version>
    </dependency>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.4.0</version>
    </dependency>
    <dependency>
      <groupId>org.bouncycastle</groupId>
      <artifactId>bcprov-jdk18on</artifactId>
      <version>1.86</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.bouncycastle</groupId>
      <artifactId>bcutil-jdk18on</artifactId>
      <version>1.86</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>org.bouncycastle</groupId>
      <artifactId>bcpkix-jdk18on</artifactId>
      <version>1.86</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
EOF
cat > fontbox.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.pdfbox</groupId>
  <artifactId>fontbox</artifactId>
  <version>2.0.37</version>
  <name>Apache FontBox</name>
  <description>Font library used by Apache PDFBox</description>
  <url>https://pdfbox.apache.org/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.4.0</version>
    </dependency>
  </dependencies>
</project>
EOF
cat > xmpbox.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.pdfbox</groupId>
  <artifactId>xmpbox</artifactId>
  <version>2.0.37</version>
  <name>Apache XmpBox</name>
  <description>XMP metadata library used with Apache PDFBox</description>
  <url>https://pdfbox.apache.org/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact pdfbox.pom:pdfbox.jar \
	--file-name pdfbox \
	--filelist .mfiles
sysjar install --buildroot %{buildroot} \
	--artifact fontbox.pom:fontbox.jar \
	--file-name fontbox \
	--filelist .mfiles-font
sysjar install --buildroot %{buildroot} \
	--artifact xmpbox.pom:xmpbox.jar \
	--file-name xmpbox \
	--filelist .mfiles-xmp
while IFS= read -r line; do
	grep -qxF "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles-font
while IFS= read -r line; do
	grep -qxF "$line" .mfiles || printf '%s\n' "$line" >> .mfiles
done < .mfiles-xmp

%check
set -eo pipefail
PDF=%{buildroot}%{_javadir}/pdfbox.jar
FONT=%{buildroot}%{_javadir}/fontbox.jar
XMP=%{buildroot}%{_javadir}/xmpbox.jar
test -f "$PDF"
test -f "$FONT"
test -f "$XMP"
mkdir -p check
cat > check/Check.java << 'EOF'
import org.apache.fontbox.ttf.TTFParser;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.xmpbox.XMPMetadata;
public class Check {
	public static void main(String[] args) throws Exception {
		PDDocument doc = new PDDocument();
		doc.addPage(new PDPage());
		int pages = doc.getNumberOfPages();
		doc.close();
		TTFParser parser = new TTFParser();
		XMPMetadata meta = XMPMetadata.createXMPMetadata();
		System.out.println("pdfbox_ok " + pages + " " + parser.getClass().getSimpleName() + " " + meta.getClass().getSimpleName());
	}
}
EOF
CP="$PDF:$FONT:$XMP:%{_javadir}/commons-logging.jar"
javac --release 8 -encoding UTF-8 -Xlint:-options -cp "$CP" -d check check/Check.java
java -cp "check:$CP" Check > check/check.log
cat check/check.log
grep -F -q 'pdfbox_ok 1 TTFParser XMPMetadata' check/check.log

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
%doc README.md RELEASE-NOTES.txt
