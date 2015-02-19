from distutils.command.bdist_rpm import bdist_rpm
from distutils.command.install_data import install_data
from distutils.command.sdist import sdist
from distutils.core import setup
import os
import platform

name = 'smart-agnc'
package = name.replace('-', '_')


class PreSourceBuild(sdist):
    def run(self):
        manifest_files = get_files('bin') + get_files('share') + \
            get_files(os.path.join('src', package)) + \
            [('', ['setup.py'])]
        with open('MANIFEST', 'w') as f:
            for unused_path, files in manifest_files:
                for fpath in files:
                    if not (fpath.endswith('.svg') or fpath.endswith('.po')):
                        f.write(fpath + '\n')

        sdist.run(self)


class PreInstall(install_data):

    data_files = []

    def run(self):
        if os.path.isdir('debian'):
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

        install_data.run(self)


class PreBdistRpm(bdist_rpm):
    def run(self):
        self.post_uninstall = self.post_install = 'post-install.sh'
        with open(self.post_install, 'w') as pi:
            for dirname in os.listdir(os.path.join('share', 'icons')):
                pi.write('gtk-update-icon-cache -q -t -f %s\n' %
                         os.path.join('/usr', 'share', 'icons', dirname))

        bdist_rpm.run(self)


def get_files(path, prefix=''):
    all_files = []
    for root, unused_subdirs, files in os.walk(path):
        dir_files = []
        for filename in files:
            dir_files.append(os.path.join(root, filename))
        if len(dir_files) > 0:
            all_files.append((os.path.join(prefix, root), dir_files))
    return all_files

setup(
    name=name,
    version='0.1.3',
    description='Smart AT&T Global Network Client',
    #long_description=readme,
    author='Ariel Barabas',
    author_email='ariel.baras@gmail.com',
    url='https://github.com/knoid/smart-agnc',
    download_url='https://github.com/knoid/smart-agnc/releases',
    packages=[package],
    scripts=['bin/smart-agnc',
             'bin/sagnc-service-restart', 'bin/sagnc-bind'],
    license='GNUv2',
    cmdclass={
        'sdist': PreSourceBuild,
        'install_data': PreInstall,
        'bdist_rpm': PreBdistRpm
    },
    data_files=get_files('share', '/usr'),
    package_dir={package: os.path.join('src', package)}
)
