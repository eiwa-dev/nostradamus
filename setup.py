from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='nostradamus',
      version='0.3.2',
      description='Not An Object-document-mapper',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends'
      ],
      keywords='odm nosql mongodb persistence',
      url='https://bitbucket.org/eiwa_dev/nostradamus',
      author='Juan I Carrano <jc@eiwa.ag>, Federico M Pomar <fp@eiwa.ag>',
      author_email='fp@eiwa.ag',
      license='Proprietary',
      packages=['nostradamus', 'nostradamus.drivers'],
      install_requires=[
          'pymongo', 'pyyaml'
      ],
      include_package_data=True,
      zip_safe=True
    )
