## sumd-riemann

A script to report the status of hosts in an ELB
to [Riemann](http://riemann.io/)
via [riemann-sumd](https://github.com/bmhatfield/riemann-sumd).

### Usage

    Usage: sumd-elb.py [options]

    A script to report the status of hosts in an ELB to Riemann via sumd. See
    http://riemann.io/ & https://github.com/bmhatfield/riemann-sumd

    Options:
    -h, --help            show this help message and exit
    --region=REGION       What region are the ELBs in?
    --load-balancers=LOAD_BALANCERS
                            Comma separated list of load balancer names to check.
                            Defaults to all for the region if absent.
    --access-key=ACCESS_KEY
                            AWS Access Key
    --access-secret=ACCESS_SECRET
                            AWS Access Secret

### riemann-sumd config

    service: 'sumd-elb'
    arg: 'sumd-elb.py --region=REGION --access-key=ACCESS_KEY --access-secret=ACCESS_SECRET --load-balancers=load,balancers'
    ttl: 60
    tags: ['notify', 'elb']
    type: 'json'

### Requirements

* `boto` (python-boto)

### Is it Terrible?

eh
