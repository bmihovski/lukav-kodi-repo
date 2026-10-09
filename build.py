#!/usr/bin/env python3
"""Build a Kodi addon repository from the addons in src/ into an output folder.

    python3 build.py <out_dir> <github_user> <github_repo>

Output (served by GitHub Pages at https://<user>.github.io/<repo>/):
    index.html                      Kodi file-manager source; links the repository zip
    addons.xml, addons.xml.md5
    datadir/<id>/<id>-<version>.zip (+ addon.xml, icon, fanart)
"""
import hashlib
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
# not shipped inside addon zips
SKIP = {'.git', '.github', 'build.py', '.gitignore', '.gitmodules', '.vscode', '__pycache__', 'tools', 'tests', 'dist', 'build.sh', 'README.md'}

REPO_ADDON = '''<?xml version="1.0" encoding="UTF-8"?>
<addon id="{id}" name="{user} Kodi Repository" version="{version}" provider-name="{user}">
    <extension point="xbmc.addon.repository" name="{user} Kodi Repository">
        <dir>
            <info compressed="false">{base}addons.xml</info>
            <checksum>{base}addons.xml.md5</checksum>
            <datadir zip="true">{base}datadir/</datadir>
        </dir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary lang="en_GB">Personal Kodi addon repository from https://github.com/{user}/{repo}</summary>
        <platform>all</platform>
        <license>GPL-3.0</license>
        <assets>
            <icon>icon.png</icon>
        </assets>
    </extension>
</addon>
'''


def zip_addon(src, addon_id, dest_zip):
    with zipfile.ZipFile(dest_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirs, files in os.walk(src):
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            for f in sorted(files):
                if f in SKIP or f.endswith(('.pyc', '.pyo')) or f == '.DS_Store':
                    continue
                full = os.path.join(dirpath, f)
                z.write(full, os.path.join(addon_id, os.path.relpath(full, src)))


def main(out, user, repo, repo_version='2.0.0'):
    base = 'https://%s.github.io/%s/' % (user, repo)
    repo_id = 'repository.%s' % user
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    # the repository addon itself is generated into a temp src folder
    gen = os.path.join(out, '.gen', repo_id)
    os.makedirs(gen)
    with open(os.path.join(gen, 'addon.xml'), 'w') as f:
        f.write(REPO_ADDON.format(id=repo_id, user=user, repo=repo, version=repo_version, base=base))
    shutil.copy(os.path.join(ROOT, '.github', 'templates', 'icon.png'), os.path.join(gen, 'icon.png'))

    srcdir = os.path.join(ROOT, 'src')
    sources = [gen] + [os.path.join(srcdir, d) for d in sorted(os.listdir(srcdir))
                       if os.path.isfile(os.path.join(srcdir, d, 'addon.xml'))]

    addons, links = ET.Element('addons'), []
    for src in sources:
        tree = ET.parse(os.path.join(src, 'addon.xml'))
        node = tree.getroot()
        aid, ver = node.get('id'), node.get('version')
        dest = os.path.join(out, 'datadir', aid)
        os.makedirs(dest)
        zname = '%s-%s.zip' % (aid, ver)
        zip_addon(src, aid, os.path.join(dest, zname))
        shutil.copy(os.path.join(src, 'addon.xml'), dest)
        for asset in node.iter():
            if asset.tag in ('icon', 'fanart') and asset.text and os.path.isfile(os.path.join(src, asset.text)):
                os.makedirs(os.path.dirname(os.path.join(dest, asset.text)), exist_ok=True)
                shutil.copy(os.path.join(src, asset.text), os.path.join(dest, asset.text))
        addons.append(node)
        links.append((aid, ver, 'datadir/%s/%s' % (aid, zname)))
        print('packed', aid, ver)

    shutil.rmtree(os.path.join(out, '.gen'))
    xml = ET.tostring(addons, encoding='unicode')
    with open(os.path.join(out, 'addons.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + xml + '\n')
    with open(os.path.join(out, 'addons.xml'), 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    with open(os.path.join(out, 'addons.xml.md5'), 'w') as f:
        f.write(md5)

    # Kodi's file manager parses <a href> links, so this page doubles as an install source
    repo_zip = links[0][2]
    rows = ''.join('<li><a href="%s">%s-%s.zip</a></li>\n' % (l, i, v) for i, v, l in links)
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('<!doctype html><meta charset="utf-8"><title>%s Kodi repository</title>\n'
                '<h1>%s Kodi repository</h1>\n'
                '<p>In Kodi: File manager &rarr; Add source &rarr; <code>%s</code>, then Add-ons &rarr; '
                'Install from zip file &rarr; <a href="%s">%s</a></p>\n<ul>\n%s</ul>\n'
                % (user, user, base, repo_zip, os.path.basename(repo_zip), rows))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
