'''
This script starts all instances with a given tag, and writes the public IPs to 
the zshrc file and ansible inventory file. The zshrc file is used to provide variables for 
easy SSH access to the instances. The ansible inventory file is used to provide the IPs to
the ansible playbook.
'''

import boto3


def start_ec2_fleet(region, tag_name, tag_value):
    '''
    This function will start all instances with the tag 'Type: ansible'
    If instances are already running, it will simply return the instance ids
    If the instances are stopped, the instances will be started and their 
    ids returned. 
    '''
    ec2 = boto3.client('ec2', region_name=region)
    tagged_instances = ec2.describe_instances(
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
                    'pending',
                    'stopped', 
                    'stopping'
                ]
            }
        ]
    )

    instance_ids = []
    instance_ips = []
    instances_to_start = []
    instances_stopping = 0
    num_of_ips = 0

    for reservation in tagged_instances['Reservations']:
        num_of_ips = len(reservation['Instances'])
        for i in range(num_of_ips):
            instance_ips.append('placeholder')
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_state = instance['State']['Name']

            if instance_state in ['running', 'pending']:
                instance_ids.append(instance_id)

            elif instance_state in ['stopped', 'stopping']:
                instance_ids.append(instance_id)
                instances_to_start.append(instance_id)
                if instance_state == 'stopping':
                    instances_stopping += 1

    if instances_to_start:
        
        while instances_stopping > 0:
            print('Waiting for instances to stop...')
            stopped_waiter = ec2.get_waiter('instance_stopped')
            stopped_waiter.wait(InstanceIds=instances_to_start)
            instances_stopping = 0
        
        print('Starting instances...')   
        response = ec2.start_instances(
            InstanceIds=instances_to_start
        )
        running_waiter = ec2.get_waiter('instance_running')
        running_waiter.wait(InstanceIds=instances_to_start)
        print('Instances started successfully, waiting for status checks...')
        status_waiter = ec2.get_waiter('instance_status_ok')
        status_waiter.wait(InstanceIds=instances_to_start)
        print('Status checks passed, instances ready for use.')
    
    tagged_instances = ec2.describe_instances(
        InstanceIds=instance_ids
    )
    for reservation in tagged_instances['Reservations']:
        for instance in reservation['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    ip_index = tag['Value'].split('_')[-1]
                    instance_ips[int(ip_index) - 1] = instance['PublicIpAddress']

    return instance_ips


def write_public_ips(instance_ips, zshrc_file, first_line, inv_file):
    # This function writes the public IPs provided of the instances to the zshrc and ansible inventory files. 

    with open(zshrc_file, 'r') as file:
        lines = file.readlines()
        first_line -= 1
        idx = 1

    for ip in instance_ips:

        lines[first_line] = f'ANode{idx}="ec2-user@{ip}" \n'
        first_line += 1
        idx += 1

    with open(zshrc_file, 'w') as file:
        file.writelines(lines)  

    
    with open(inv_file, 'r') as file:
        lines = file.readlines()
        idx = 0
    
    for ip in instance_ips:
        lines[idx] = f'{ip} \n'
        idx += 1
    
    with open(inv_file, 'w') as file:
        file.writelines(lines)

    print()
    print('New IPs of fleet successfully written to config file')
    print('To SSH into instances open new terminal and use "ssh <$ANode1, $ANode2, $ANode3>"')
    print()  

def main():
    tag_name = 'Type'
    tag_value = 'ansible'
    zshrc_file ='/Users/Kris/.zshrc'
    first_line = 11
    inv_file = '../ansible/inventory'
    region = 'us-west-2'
    instance_ips = start_ec2_fleet(region, tag_name, tag_value)
    write_public_ips(instance_ips, zshrc_file, first_line, inv_file)


if __name__ == '__main__':
    main()
    