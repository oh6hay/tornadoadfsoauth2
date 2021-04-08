from setuptools import setup
setup(
    name='tornadoadfsoauth2',
    version='0.0.1',
    description='ADFS Oauth2 authentication for tornadoweb',
    author='Ossi Vaananen',
    author_email='ossi.vaananen@me.com',
    packages=['tornadoadfsoauth2'],
    install_requires=['tornadoweb', 'pyjwt'],
    license='BSD 3-clause')
