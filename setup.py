from distutils.command.install_data import install_data as InstallDataBuild
from distutils.core import setup
import os


class ChangeArchitecture(InstallDataBuild):
    def run(self):
        with open('debian/control', 'r') as f:
            lines = f.readlines()
        with open('debian/control', 'w') as f:
            for line in lines:
                if line.startswith('Architecture'):
                    line = 'Architecture: amd64\n'
                f.write(line)

        InstallDataBuild.run(self)


def get_files(path, prefix=''):
    all_files = []
    for root, subdirs, files in os.walk(path):
        dir_files = []
        for filename in files:
            if not filename.endswith('.po') and not filename.endswith('.svg'):
                dir_files.append(os.path.join(root, filename))
        if len(dir_files) > 0:
            all_files.append((os.path.join(prefix, root), dir_files))
    return all_files

share_files = get_files('share', '/usr')

setup(
    name='smart-agnc',
    version='0.0.6',
    description='AT&T Global Network Client on steroids',
    author='Ariel Barabas',
    author_email='smart-agnc@knoid.me',
    url='https://github.com/knoid/smart-agnc',
    download_url='https://github.com/knoid/smart-agnc/releases',
    packages=['smart_agnc'],
    scripts=['bin/smart-agnc',
             'bin/sagnc-service-restart', 'bin/sagnc-bind'],
    license='GNUv2',
    cmdclass={'install_data': ChangeArchitecture},
    data_files=share_files,
    package_dir={'smart_agnc': os.path.join('src', 'smart_agnc')}
)
