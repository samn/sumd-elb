## sumd-riemann

A script to report the status of hosts in an ELB
to [Riemann](http://riemann.io/)
via [riemann-sumd](https://github.com/bmhatfield/riemann-sumd).

### Usage

    Usage: sumd-elb.py [options]

    A script to report the status of hosts in an ELB to Riemann via sumd. See
    http://riemann.io/ & https://github.com/bmhatfield/riemann-sumd

    Options:
    -h, --help              show this help message and exit
    --region=REGION         What region are the ELBs in?
    --load-balancers=LOAD_BALANCERS
                            Comma separated list of load balancer names to check.
                            Defaults to all for the region if absent.
    --warn-percent=WARN_PERCENT
                            Set the ELB state to warn when this percent of hosts
                            are in service. default = 25
    --critical-percent=CRITICAL_PERCENT
                            Set the ELB state to critical when this percent of hosts
                            are in service. default = 50
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

An event is emitted to riemann-sumd (and sent to Riemann) for each instance in each ELB.
It have a state of "ok" & metric of 1 if the instance is in service,
and a state of "warn" & metric of 0 otherwise.

The event's service will include the ELB name.
The host will be the public DNS name of the instance, as described by AWS.

An event is also emitted for each ELB describing the percent of in service hosts.
The state is set by comparing the percentage of hosts that are in service with the
warn and critical percent thresholds (75 & 50 by default).

## Sample Events

Per Instance:

    {
        "attributes": {
            "availability_zone": "us-east-1c",
            "instance_id": "i-350",
            "instance_state": "InService",
            "region": "us-east-1"
        },
        "description": "Instance health in ELB",
        "host": "ec2-1-255-250-255.compute-1.amazonaws.com",
        "metric": 1,
        "service": "load-balancer ELB Instance Status",
        "state": "ok"
    }

Per ELB:

    {
        "attributes": {
            "dns_name": "load-balancer-1223929292.us-east-1.elb.amazonaws.com"
        },
        "description": "Percentage of in service hosts for this ELB.",
        "host": "load-balancer-1223929292.us-east-1.elb.amazonaws.com",
        "metric": 100.0,
        "service": "load-balancer ELB Status",
        "state": "ok"
    }

### Requirements

* `boto` (python-boto)

### Notes

If an ELB has a terminated instance in it then it will not be monitored.

### Is it Terrible?

eh
