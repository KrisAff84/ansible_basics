import boto3
import json


def stop_ec2_instances(Instance1, Instance2, Instance3):
    ec2 = boto3.client('ec2')
    response = ec2.stop_instances(
        InstanceIds=[
            Instance1,
            Instance2,
            Instance3
        ]
    )
    print(json.dumps(response, indent=4, default=str))


def main():
    Instance1='i-087bca9f24f40d3b0'
    Instance2='i-0ad9cc67b5e19048b'
    Instance3='i-0d19d158a0ba8dca2'
    stop_ec2_instances(Instance1, Instance2, Instance3)

if __name__ == '__main__':
    main()