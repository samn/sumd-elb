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
        self.warn_percent = options.warn_percent
        self.critical_percent = options.critical_percent
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
        try:
            reservations = self.ec2_conn.get_all_instances(instance_ids=instance_ids)
            return [i for r in reservations for i in r.instances]
        except boto.exception.EC2ResponseError:
            return []

    def lb_name_from_dns(self, dns_name):
        """
        Finds the load balancer's name from a public dns name like rails-settings-1257625549.us-east-1.elb.amazonaws.com
        """
        sub_domain = dns_name.split(".")[0]
        return sub_domain.rsplit("-", 1)[0]

    def is_instance_up(self, instance_state):
        return instance_state.state == "InService"

    def construct_instance_event(self, load_balancer, instance, instance_state):
        event = {}
        event["service"] = "%s ELB Instance Status" % self.lb_name_from_dns(load_balancer.dns_name)
        event["host"] = instance.public_dns_name
        if self.is_instance_up(instance_state):
            event["state"] = "ok"
            event["metric"] = 1
        else:
            event["state"] = "warn"
            event["metric"] = 0
        event["description"] = "Instance health in ELB"
        event["attributes"] = {}
        event["attributes"]["region"] = self.region
        event["attributes"]["availability_zone"] = instance.placement
        event["attributes"]["instance_state"] = instance_state.state
        event["attributes"]["instance_id"] = instance.id
        return event

    def construct_elb_event(self, load_balancer, percent_up):
        event = {}
        event["service"] = "%s ELB Status" % self.lb_name_from_dns(load_balancer.dns_name)
        event["host"] = load_balancer.dns_name
        if percent_up <= int(self.critical_percent):
            event["state"] = "critical"
        elif percent_up <= int(self.warn_percent): 
            event["state"] = "warn"
        else:
            event["state"] = "ok"
        event["metric"] = percent_up
        event["description"] = "Percentage of in service hosts for this ELB."
        event["attributes"] = {}
        event["attributes"]["dns_name"] = load_balancer.dns_name
        return event

    def report(self):
        events = []
        for load_balancer in self.get_load_balancers():
            num_up, num_down = 0 , 0
            instance_states = load_balancer.get_instance_health()
            instance_ids = [i_s.instance_id for i_s in instance_states]
            instances = dict((instance.id, instance) for instance in self.get_instances(instance_ids))
            if instances:
                for instance_state in instance_states: 
                    # A terminated instance won't be in the instances list, even though it has an ELB status
                    if instances.get(instance_state.instance_id, False):
                        event = self.construct_instance_event(load_balancer, instances[instance_state.instance_id], instance_state)
                        events.append(event)
                    if self.is_instance_up(instance_state):
                        num_up += 1
                    else:
                        num_down += 1
                if num_up + num_down > 0:
                    percent_up = 100 * (num_up / float(num_up + num_down))
                else:
                    percent_up = 0.0
                events.append(self.construct_elb_event(load_balancer, percent_up))

        print json.dumps(events)

if __name__ == "__main__":
    desc = """
A script to report the status of hosts in an ELB to Riemann via sumd.
See http://riemann.io/ & https://github.com/bmhatfield/riemann-sumd
    """
    parser = OptionParser(description=desc)
    parser.add_option("--region", default="us-east-1", help="What region are the ELBs in?")
    parser.add_option("--load-balancers",  help="Comma separated list of load balancer names to check.  Defaults to all for the region if absent.")
    parser.add_option("--warn-percent",  default="75", help="Set the ELB state to warn when this percent of hosts are in service. default = 25")
    parser.add_option("--critical-percent",  default="50", help="Set the ELB state to critical when this percent of hosts are in service. default = 50")
    parser.add_option("--access-key", help="AWS Access Key")
    parser.add_option("--access-secret", help="AWS Access Secret")
    options, args = parser.parse_args()
    if options.access_key is None or options.access_secret is None:
        parser.print_help()
        exit(-1)
    ElbCheck(options).report()
