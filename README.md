
feeder
=======

[![Build Status](https://travis-ci.org/nir0s/feeder.svg?branch=develop)](https://travis-ci.org/nir0s/feeder)

[![Gitter chat](https://badges.gitter.im/nir0s/feeder.png)](https://gitter.im/nir0s/feeder)

[![PyPI](http://img.shields.io/pypi/dm/feeder.svg)](http://img.shields.io/pypi/dm/feeder.svg)

[![PypI](http://img.shields.io/pypi/v/feeder.svg)](http://img.shields.io/pypi/v/feeder.svg)

feeder generates events/logs using a specified formatter and sends them using the specified transport.
It can also generate fake data using fake-factory.

### Quick Start
[Quick Start](http://feeder.readthedocs.org/en/latest/quick_start.html)

### Documentation
[feeder Documentation](http://feeder.readthedocs.org)

### Installation
```shell
 pip install feeder
 # or, for dev:
 pip install https://github.com/nir0s/feeder/archive/develop.tar.gz
```

### Usage Examples
see [feeder config](http://feeder.readthedocs.org/en/latest/configuration.html) and [advanced config](http://feeder.readthedocs.org/en/latest/advanced_configuration.html)
to configure your transports and formatters.
```shell
 # this will assume config.py in the cwd and assume default for each option
 mouth feed
 # or.. you can specify whatever you want in the cli..
 mouth feed -c /my/config/file/path.py -t AMQP -f Json -g 0.001 -m 100000000
 mouth feed -t UDP -f Custom -g 0.00001 -m 102831028
 # you can also send in batches
 mouth feed -t UDP -f Custom -g 0.01 -m 102831028 -b 1000
 # and even use some common formatters like apache's..
 mouth feed -t Stream -f ApacheError
 # print fake data types that you can use in the config...
 mouth list fake
 # print a list of available transports
 mouth list transports
 # print a list of available formatters
 mouth list formatters
```

### Additional Information
- [Use Case](http://feeder.readthedocs.org/en/latest/case_study.html)
- [Configuration](http://feeder.readthedocs.org/en/latest/configuration.html)
- [formatters](http://feeder.readthedocs.org/en/latest/formatters.html)
- [transports](http://feeder.readthedocs.org/en/latest/transports.html)
- [API](http://feeder.readthedocs.org/en/latest/api.html)
- [InHouseFaker](http://feeder.readthedocs.org/en/latest/inhousefaker.html)

### Vagrant
A vagrantfile is provided: It will load a machine and install feeder on it in a virtualenv so that you can experiment with it.
In the future, another machine will be provided with rabbitmq, logstash, elasticsearch and kibana so that you can experiment with different types of formats and transports.
