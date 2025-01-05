from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.11'
]
 
setup(
  name='adofaipy',
  version='3.2.3',
  description='A library that makes automating events in ADOFAI levels more convenient.',
  long_description=open('README.md',encoding='utf-8-sig').read() + open('CHANGELOG.md').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/M1n3c4rt/adofaipy',
  author='M1n3c4rt',
  author_email='vedicbits@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords='adofai',
  packages=find_packages(),
  install_requires=[]
)