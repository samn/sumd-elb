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

### IAM Permissions

The user whose access keys you use to run this script needs to have the following permissions:

* ec2:DescribeRegions
* ec2:DescribeAvailabilityZones
* elasticloadbalancing:DescribeInstanceHealth
* elasticloadbalancing:DescribeLoadBalancers

### riemann-sumd config

    service: 'sumd-elb'
    arg: 'sumd-elb.py --region=REGION --access-key=ACCESS_KEY --access-secret=ACCESS_SECRET --load-balancers=load,balancers'
    ttl: 60
    tags: ['notify', 'elb']
    type: 'json'

### Riemann Event

The event emitted to riemann-sumd (and sent to Riemann) will
have a state of "ok" & metric of 1 if the instance is in service,
and a state of "error" & metric of 0 otherwise.

The event's service will include the ELB name.
The host will be the public DNS name of the instance, as described by AWS.

### Requirements

* `boto` (python-boto)

### Notes

If an ELB has a terminated instance in it then it will not be monitored.

### Is it Terrible?

eh
