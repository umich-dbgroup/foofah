# Foofah

**Foofah** [1][2]  is a programming-by-example data transformation program synthesis system. It is able to generate a data transformation program defined in Professor Joe Hellerstein's Potter's Wheel paper [3] using an input-output example from the end user.

## Requirements

 - Linux
 - Python 2.7
 - g++
 - [Boost.Python](http://www.boost.org/doc/libs/1_64_0/libs/python/doc/html/index.html) ([Mac](http://www.pyimagesearch.com/2015/04/27/installing-boost-and-boost-python-on-osx-with-homebrew/), [Linux](https://stackoverflow.com/questions/12578499/how-to-install-boost-on-ubuntu))
 - [setuptools](https://pypi.python.org/pypi/setuptools)
	 ```sh
	$ python -m pip install -U pip setuptools
	```

In fact, other Python modules `numpy`, `tabulate`, `cherrypy`, `editdistance`, `python-Levenshtein` , `matplotlib` are also required. But they could be installed using setuptools in next section.

## Foofah on Docker

Build Foofah container
```sh
$ docker build -t foofah .
```

Run Foofah contrainer
```sh
$ docker run -p 8080:8080 foofah
```
Foofah web service will be available at [localhost:8080](http://0.0.0.0:8080).

## Installation
```sh
$ cd foofah
$ python setup.py install
```

## User Guide
##### Foofah Console
To test Foofah against individual test case from the console:
```sh
$ cd foofah
$ python foofah.py --input <test_file>
```
Note that each test case must be a json file that contains one json object with two members, `InputTable` and `OutputTable`, both of which are 2d array of strings, representing the user-provided input-output example.

 - [Link](https://raw.githubusercontent.com/markjin1990/foofah_benchmarks/master/exp0_proactive_wrangling_complex_2.txt) to an example test case.
 - [Link](https://github.com/markjin1990/foofah_benchmarks) to all benchmark test cases used in our full paper.

To learn other command-line argument options:
```sh
$ python foofah.py --help
```

##### Foofah Web Server

To interact with Foofah through a web interface (as shown in [video](https://youtu.be/Ura2pxez_Bo)):
```sh
$ python foofah_server.py
```
By default, the service will be available at [localhost:8080](http://0.0.0.0:8080).

## Acknowledgements
Foofah is being developed in the University of Michigan. This work in part supported by National Science Foundation grants IIS-1250880, IIS-1054913, NSF IGERT grant 0903629,
a Sloan Research Fellowship and a CSE Department Fellowship

## References
[1] [ "Foofah: Transforming Data By Example", SIGMOD 17',
Zhongjun Jin, Michael R. Anderson, Michael Cafarella, H. V. Jagadish](http://dl.acm.org/authorize?N37756)

[2] ["Foofah: A Programming-By-Example System for Synthesizing Data Transformation Programs", SIGMOD 17', Demo,
Zhongjun Jin, Michael R. Anderson, Michael Cafarella, H. V. Jagadish](http://dl.acm.org/authorize?N37718)

[3] ["Potter's wheel: An interactive data cleaning system." VLDB. Vol. 1. 2001.
Raman, Vijayshankar, and Joseph M. Hellerstein.  ](http://www.vldb.org/conf/2001/P381.pdf)