from setuptools import setup, find_packages

setup(
    name="Shikhandi",
    version="0.1.0",
    packages=find_packages(exclude=['tests*']),

    install_requires=['beautifulsoup4==4.5.1',
                      'bs4==0.0.1',
                      'requests==2.11.1'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.md', '*.rst'],
    },

    # metadata for upload to PyPI
    author="Will Skywalker",
    author_email="cxbats@gmail.com",
    description="A backup tool for renren. You can backup any of your friends' timeline and photos to local with it.",
    license="Apache 2.0",
    url="https://github.com/WillSkywalker/Shikhandi",   # project home page, if any
    keywords='crawler renren',

    # could also include long_description, download_url, classifiers, etc.
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',        
    ],
)