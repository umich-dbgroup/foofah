from setuptools import setup, Extension

setup(name='foofah',
      version='1.0',
      url='https://github.com/markjin1990/foofah',
      author='Zhongjun Jin',
      author_email='markjin@umich.edu',
      license='MIT',
      ext_modules=[
          Extension("foofah_utils", ["foofah_libs/foofah_utils.cpp"],
                    libraries=["boost_python"],
                    extra_compile_args=["-std=c++11"]
                    )
      ],
      install_requires=[
          'numpy', 'tabulate', 'cherrypy', 'editdistance', 'python-Levenshtein', 'matplotlib'
      ])
