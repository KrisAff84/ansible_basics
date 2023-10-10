'''
This script starts all instances with the tag 'Type: ansible' and writes the public IPs to 
the zshrc file and ansible inventory file. The zshrc file is used to provide variables for 
easy SSH access to the instances. The ansible inventory file is used to provide the IPs to
the ansible playbook.
'''

import boto3


def start_ec2_fleet(region):
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
                'Name': 'tag:Type',
                'Values': [
                    'ansible'
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running',
                    'pending',
                    'shutting-down',
                    'stopped'
                ]
            }
        ]
    )

    instance_ids = []
    for instance in tagged_instances['Reservations']:
        instance_ids.append(instance['Instances'][0]['InstanceId'])

    instance_state = tagged_instances['Reservations'][0]['Instances'][0]['State']['Name']
    if ('running' or 'pending') in instance_state:
        return instance_ids
    if 'stopped' in instance_state:
        print('Starting instances...')
        response = ec2.start_instances(
            InstanceIds=instance_ids
        )
       
    if 'stopping' in instance_state:
        print('Waiting for instances to fully shut down...')
        stopped_waiter = ec2.get_waiter('instance_stopped')
        stopped_waiter.wait(InstanceIds=instance_ids)
        response = ec2.start_instances(
            InstanceIds=instance_ids
        )

    return instance_ids


def write_public_ips(instance_ids, zshrc_file, line_number1, line_number2, line_number3, inv_file):
    # This function writes the public IPs provided by parameter instance_ids to the zshrc file and ansible inventory file
    ec2 = boto3.client('ec2')
    waiter = ec2.get_waiter('instance_running')
    new_ips = []
    idx = 0
    for id in instance_ids:
        waiter.wait(InstanceIds=[id])
        response = ec2.describe_instances(
            InstanceIds=[
            id
            ],
        )
        print()
        for instance in response['Reservations'][0]['Instances']:
            print(f"Public IP of Node {idx + 1}: {instance['PublicIpAddress']}")
            new_ips.append(instance['PublicIpAddress'])
            idx += 1

    with open(zshrc_file, 'r') as file:
        lines = file.readlines()

    lines[line_number1 - 1] = f'ANode1="ec2-user@{new_ips[0]}" \n'
    lines[line_number2 - 1] = f'ANode2="ec2-user@{new_ips[1]}" \n'
    lines[line_number3 - 1] = f'ANode3="ec2-user@{new_ips[2]}" \n'

    with open(zshrc_file, 'w') as file:
        file.writelines(lines)  

    
    with open(inv_file, 'r') as file:
        lines = file.readlines()
    
    lines[0] = f'ec2-user@{new_ips[0]} \n'
    lines[1] = f'ec2-user@{new_ips[1]} \n'
    lines[2] = f'ec2-user@{new_ips[2]} \n'

    with open(inv_file, 'w') as file:
        file.writelines(lines)

    print()
    print('New IPs of fleet successfully written to config file')
    print('To SSH into instances open new terminal and use "ssh <$ANode1, $ANode2, $ANode3>"')
    print()  


def main():
    zshrc_file ='/Users/Kris/.zshrc'
    inv_file = '../ansible/inventory'
    line_number1 = 11
    line_number2 = 12
    line_number3 = 13
    region = 'us-west-2'
    instance_ids = start_ec2_fleet(region)
    print(instance_ids)
    write_public_ips(instance_ids, zshrc_file, line_number1, line_number2, line_number3, inv_file)


if __name__ == '__main__':
    main()
    