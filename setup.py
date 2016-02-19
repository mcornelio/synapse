__author__ = 'mcornelio'

from setuptools import setup
from datetime import datetime

def version_string():
    return "1.1.6"

readme = open('README.md', 'r')
README_TEXT = readme.read()
readme.close()


setup(name='synapse',
      version=version_string(),
      description='Cell-based device adapter',
      long_description=README_TEXT,
      url='http://github.com/cornelio/synapse',
      author='Michael Cornelio',
      author_email='michael@cornelio.com',
      license='MIT',
      packages=['synapse'],
      install_requires=[
          'cherrypy', 'requests', 'decorator', 'rpyc'
      ],
      scripts=[
            'scripts/synapse'
      ],
      classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Environment :: MacOS X",
            "Environment :: Win32 (MS Windows)",
            "Intended Audience :: Developers",
            "License :: MIT",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: JavaScript",
            "Programming Language :: Python :: 2"
      ],
      zip_safe=False)
