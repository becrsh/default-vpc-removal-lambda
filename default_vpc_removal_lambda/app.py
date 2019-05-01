import json
import boto3
import logging
import os

# import requests
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# If true we will do a dry-run
LOCAL_INVOKE = os.getenv("AWS_SAM_LOCAL")


class DefaultVpc:
    """
    DefaultVpc Class
    """
    def __init__(self, vpc_id, region, session):
        self.vpc_id = vpc_id
        self.region = region
        self._client = session.client('ec2', region)
        self.cannot_delete = False
        self.network_interfaces = []
        self.security_groups = []
        self.route_tables = []
        self.nat_gateways = []
        self.internet_gateway = None
        self.network_acls = []
        self.subnets = []

        self.__vpcFilter = [{
            'Name': 'vpc-id',
            'Values': [self.vpc_id]
        }]

        self.get_network_interfaces()
        self.get_security_groups()

    def get_network_interfaces(self):
        logger.debug("Getting Network Interfaces...")
        result = []
        paginator = self._client.get_paginator('describe_network_interfaces')
        iterator = paginator.paginate(Filters=self.__vpcFilter)

        for page in iterator:
            for interface in page['NetworkInterfaces']:
                if 'Attachment' in interface and (interface['Attachment']['Status'] == 'attached' or interface['Attachment']['status' == 'attaching']):
                    self.cannot_delete = True
                result.append(interface['NetworkInterfaceId'])

        self.network_interfaces = result

    def get_security_groups(self):
        logger.debug("Getting Security Groups...")
        result = []
        paginator = self._client.get_paginator('describe_security_groups')
        iterator = paginator.paginate(Filters=self.__vpcFilter)

        for page in iterator:
            for sg in page['SecurityGroups']:
                result.append(sg['GroupId'])

        self.security_groups = result

    def describe(self):
        return {
            'vpc_id': self.vpc_id,
            'region': self.region,
            'network_interfaces': self.network_interfaces,
            'security_groups': self.security_groups,
            'network_acls': self.network_acls,
            'route_tables': self.route_tables,
            'nat_gateways': self.nat_gateways,
            'subnets': self.subnets,
            'internet_gateway': self.internet_gateway,
            'cannot_delete': self.cannot_delete
        }

    def destroy(self):
        pass


def lambda_handler(event, context):
    dry_run = False
    if LOCAL_INVOKE == "true":
        logger.info("==== Local invocation detected! ====")
        dry_run = True

    session = boto3.session.Session()
    account_vpcs = {}

    # Do this for every region
    for region in get_regions(session):
        account_vpcs[region] = find_default_vpc(session, region)

    logger.info(f"Default VPCS in every region {json.dumps(account_vpcs)}")

    do_operations(session, account_vpcs, dry_run)

    return {
        "message": "Function executed successfully!",
        "event": event
    }


def get_regions(session):
    """
    Get all regions from the account. If new regions are added it will dynamically be included in the code through this
    function
    :param session: The general session from Boto3
    :return: List of regions
    """
    client = session.client("ec2")
    result = []
    response = client.describe_regions()
    for region_obj in response['Regions']:
        result.append(region_obj['RegionName'])

    return result


def find_default_vpc(session, region_name):
    """
    Looks for every default VPC in a region
    :param session: Boto3 Session
    :param region_name: The region name to look in
    :return: list of vpc id's
    """
    result = []
    client = session.client("ec2", region_name)
    response = client.describe_vpcs(
        Filters=[{
           'Name': 'isDefault',
           'Values': ['true']
        }]
    )

    for vpc in response['Vpcs']:
        if vpc['IsDefault']:
            result.append(vpc['VpcId'])

    return result


def do_operations(session, vpc_dict, dry_run):
    for region,vpc_ids in vpc_dict.items():
        for vpc_id in vpc_ids:
            vpc = DefaultVpc(
                session=session,
                vpc_id=vpc_id,
                region=region
            )
            if dry_run:
                logger.info(json.dumps(vpc.describe(), indent=2))
            else:
                vpc.destroy()
