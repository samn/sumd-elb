#! /usr/bin/env python
import boto.ec2
import boto.ec2.elb
import json
from optparse import OptionParser
import sys

class ElbCheck():
    def __init__(self, options):
        self.region = options.region
        self.load_balancers = None
        if options.load_balancers:
            self.load_balancers = options.load_balancers.split(",")
        self.access_key = options.access_key
        self.access_secret = options.access_secret
        self.elb_conn = self.create_elb_connection() 
        self.ec2_conn = self.create_ec2_connection() 

    def create_elb_connection(self):
        return boto.ec2.elb.connect_to_region(self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.access_secret)

    def create_ec2_connection(self):
        return boto.ec2.connect_to_region(self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.access_secret)

    def get_load_balancers(self):
        return self.elb_conn.get_all_load_balancers(load_balancer_names=self.load_balancers)

    def get_instances(self, instance_ids):
        reservations = self.ec2_conn.get_all_instances(instance_ids=instance_ids)
        return [i for r in reservations for i in r.instances]

    def lb_name_from_dns(self, dns_name):
        """
        Finds the load balancer's name from a public dns name like rails-settings-1257625549.us-east-1.elb.amazonaws.com
        """
        sub_domain = dns_name.split(".")[0]
        # strip out the last part of the subdomain, separated by -'s.
        # that should be the name of the load balancer.
        return "-".join(sub_domain.split("-")[0:-1])

    def construct_event(self, load_balancer, instance, instance_state):
        event = {}
        event["service"] = "%s ELB Status" % self.lb_name_from_dns(load_balancer.dns_name)
        event["host"] = instance.public_dns_name
        if instance_state.state == "InService":
            event["state"] = "ok"
        else:
            event["state"] = "error"
        event["description"] = "Instance health in ELB"
        # TODO add a metric?
        event["attributes"] = {}
        event["attributes"]["region"] = self.region
        event["attributes"]["availability_zone"] = instance.placement
        event["attributes"]["instance_state"] = instance_state.state
        event["attributes"]["instance_id"] = instance.id
        return event

    def report(self):
        events = []
        for load_balancer in self.get_load_balancers():
            instance_states = load_balancer.get_instance_health()
            instance_ids = [i_s.instance_id for i_s in instance_states]
            instances = dict((instance.id, instance) for instance in self.get_instances(instance_ids))
            for instance_state in instance_states: 
                event = self.construct_event(load_balancer, instances[instance_state.instance_id], instance_state)
                events.append(event)
        print json.dumps(events)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--region", default="us-east-1", help="What region are the ELBs in?")
    parser.add_option("--load-balancers",  help="Comma separated list of load balancer names to check.  Defaults to all for the region if absent.")
    parser.add_option("--access-key", help="AWS Access Key")
    parser.add_option("--access-secret", help="AWS Access Secret")
    options, args = parser.parse_args()
    if options.access_key is None or options.access_secret is None:
        parser.print_help()
        exit(-1)
    ElbCheck(options).report()
