# This script will stop all instances with a given tag name and value. 


import boto3
import json


def stop_ec2_instances(region, tag_name, tag_value):
    instances_to_stop = []
    ec2 = boto3.client('ec2', region_name=region)
    instance_ids = ec2.describe_instances(
          Filters=[
            {
                'Name': f'tag:{tag_name}',
                'Values': [
                    tag_value
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                    'pending'
                ]
            }
        ]
    )
    # If instances are already stopped, print "Instances already stopped"
    if not instance_ids['Reservations']:
        print(f'Instances with with tag "{tag_name}": "{tag_value}" already stopped.')
        return
    else:
        for reservation in instance_ids['Reservations']:
            for instance in reservation['Instances']:
                instances_to_stop.append(instance['InstanceId'])
        print(f'Stopping instances with tag "{tag_name}": "{tag_value}"')

    response = ec2.stop_instances(
        InstanceIds=instances_to_stop
    )

    print(json.dumps(response, indent=4, default=str))


def main():
    region = 'us-west-2'
    tag_name = 'Type'
    tag_value = 'ansible'
    stop_ec2_instances(region, tag_name, tag_value)

if __name__ == '__main__':
    main()
