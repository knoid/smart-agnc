from distutils.command.build_scripts import build_scripts
from distutils.command.install_data import install_data
from distutils.core import setup
import os
import platform
from subprocess import call

name = 'smart-agnc'
package = name.replace('-', '_')


class PreBuildScripts(build_scripts):
    def run(self):
        call('make')
        build_scripts.run(self)


class PreInstall(install_data):

    data_files = []

    def run(self):
        with open('debian/control', 'r') as f:
            lines = f.readlines()
        with open('debian/control', 'w') as f:
            for line in lines:
                if line.startswith('Architecture'):
                    if '64' in platform.processor():
                        line = line.replace('all', 'amd64')
                    else:
                        line = line.replace('all', 'i386')
                f.write(line)
        data_files = []
        for path, files in self.data_files:
            files = [fpath for fpath in files if not
                     (fpath.endswith('.svg') or fpath.endswith('.po'))]
            if len(path) > 0 and not path.startswith('src'):
                data_files.append((path, files))
        self.data_files = data_files

        print self.data_files
        install_data.run(self)


def get_files(path, prefix=''):
    all_files = []
    for root, subdirs, files in os.walk(path):
        dir_files = []
        for filename in files:
            dir_files.append(os.path.join(root, filename))
        if len(dir_files) > 0:
            all_files.append((os.path.join(prefix, root), dir_files))
    return all_files

share_files = get_files('share', '/usr')
share_files += [('', ['Makefile']), get_files('src/c-bind', '')]

setup(
    name=name,
    version='0.0.7',
    description='AT&T Global Network Client on steroids',
    #long_description=readme,
    author='Ariel Barabas',
    author_email='ariel.baras@gmail.com',
    url='https://github.com/knoid/smart-agnc',
    download_url='https://github.com/knoid/smart-agnc/releases',
    packages=[package],
    scripts=['bin/smart-agnc',
             'bin/sagnc-service-restart', 'bin/sagnc-bind'],
    license='GNUv2',
    cmdclass={'build_scripts': PreBuildScripts, 'install_data': PreInstall},
    data_files=share_files,
    package_dir={package: os.path.join('src', package)}
)
