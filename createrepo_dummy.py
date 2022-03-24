#!/usr/bin/env python

import os
import sys
import shutil
import os.path
import createrepo_c as cr
import random
import hashlib

word_file = "/usr/share/dict/words"
WORDS = None
if os.path.exists(word_file):
    WORDS = open(word_file).read().splitlines()
else:
    print("Didn't find: " + word_file + ", using random characters (slower)")

def random_str(size=10):
    random_string = ''

    if (WORDS):
        return random.choice(WORDS)

    for _ in range(size):
        random_integer = random.randint(97, 97 + 26 - 1)
        # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))

    return random_string

def get_random_changelog():
    author = random_str() + " <" + random_str() + "@redhat.com>"
    data = random.randrange(10000000000)
    msg = ""
    for _ in range(0, random.randrange(100)):
        msg = msg + " " + random_str()

    return (author, data, msg)

def get_random_pkg():
    pkg = cr.Package()
    pkg.name = random_str()
    pkg.checksum_type = "sha256"
    pkg.pkgId = hashlib.sha256(pkg.name.encode('ascii')).hexdigest()
    pkg.arch = "x86_64"
    pkg.version = str(random.randrange(10))
    pkg.epoch = "0"
    pkg.release = str(random.randrange(100))
    pkg.summary = "sum"
    pkg.description = "desc"
    pkg.url = "http://foo"
    pkg.time_file = 111
    pkg.time_build = 112
    pkg.rpm_license = "EULA"
    pkg.rpm_vendor = "Me"
    pkg.rpm_group = "a-team"
    pkg.rpm_buildhost = "hal3000.space"
    pkg.rpm_sourcerpm = "source.src.rpm"
    pkg.rpm_header_start = 1
    pkg.rpm_header_end = 2
    pkg.rpm_packager = "Arnold Rimmer"
    pkg.size_package = 33
    pkg.size_installed = 44
    pkg.size_archive = 55
    pkg.location_href = "package/" + pkg.name + ".rpm"
    pkg.location_base = "file://dir/" + pkg.name

    pkg.requires = [(random_str(), 'GE', '1', '3.2.1', None, True)]
    pkg.provides = [(random_str(), None, None, None, None, False)]
    pkg.conflicts = [(random_str(), 'LT', '0', '1.0.0', None, False)]
    pkg.obsoletes = [(random_str(), 'GE', '0', '1.1.0', None, False)]
    pkg.suggests = [(random_str(), 'GE', '0', '1.1.0', None, False)]
    pkg.enhances = [(random_str(), 'GE', '0', '1.1.0', None, False)]
    pkg.recommends = [(random_str(), 'GE', '0', '1.1.0', None, False)]
    pkg.supplements = [(random_str(), 'GE', '0', '1.1.0', None, False)]
    pkg.files = [(None, '/' + random_str() + '/', random_str())]

    chnglogs = []
    for _ in range(0, random.randrange(500)):
        chnglogs.append(get_random_changelog())

    pkg.changelogs = chnglogs

    return pkg


def do_repodata(pkg_count):
    # Prepare repodata/ directory
    path = "./"
    repodata_path = os.path.join(path, "repodata")
    if os.path.exists(repodata_path):
        shutil.rmtree(repodata_path)
    os.mkdir(repodata_path)

    # Prepare metadata files
    repomd_path  = os.path.join(repodata_path, "repomd.xml")
    pri_xml_path = os.path.join(repodata_path, "primary.xml.gz")
    fil_xml_path = os.path.join(repodata_path, "filelists.xml.gz")
    oth_xml_path = os.path.join(repodata_path, "other.xml.gz")

    pri_xml = cr.PrimaryXmlFile(pri_xml_path)
    fil_xml = cr.FilelistsXmlFile(fil_xml_path)
    oth_xml = cr.OtherXmlFile(oth_xml_path)

    pri_xml.set_num_of_pkgs(pkg_count)
    fil_xml.set_num_of_pkgs(pkg_count)
    oth_xml.set_num_of_pkgs(pkg_count)

    # Process all packages
    for i in range(0, pkg_count):
        pkg = get_random_pkg()
        pri_xml.add_pkg(pkg)
        fil_xml.add_pkg(pkg)
        oth_xml.add_pkg(pkg)

    pri_xml.close()
    fil_xml.close()
    oth_xml.close()

    # Prepare repomd.xml
    repomd = cr.Repomd()

    # Add records into the repomd.xml
    repomdrecords = (("primary",      pri_xml_path, None),
                     ("filelists",    fil_xml_path, None),
                     ("other",        oth_xml_path, None))
    for name, path, db in repomdrecords:
        record = cr.RepomdRecord(name, path)
        record.fill(cr.SHA256)
        repomd.set_record(record)

    # Write repomd.xml
    open(repomd_path, "w").write(repomd.xml_dump())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s <pkg_count>" % (sys.argv[0]))
        sys.exit(1)

    try:
        int(sys.argv[1])
    except:
        print("Usage: %s <pkg_count>" % (sys.argv[0]))
        sys.exit(1)


    do_repodata(int(sys.argv[1]))

    print("Repository created with %s" % sys.argv[1])
