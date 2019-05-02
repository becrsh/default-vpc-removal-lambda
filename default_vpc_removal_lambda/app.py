import json
import boto3
import logging
import os

# import requests
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# If true we will do a dry-run
LOCAL_INVOKE = os.getenv("AWS_SAM_LOCAL")


def lambda_handler(event, context):
    dry_run = False
    if LOCAL_INVOKE == "true":
        logger.info("==== Local invocation detected! ====")

    session = boto3.session.Session()
    account_vpcs = {}

    # Do this for every region
    for region in get_regions(session):
        account_vpcs[region] = find_default_vpc(session, region)

    logger.info(f"Default VPCS in every region {json.dumps(account_vpcs)}")

    do_operations(session, account_vpcs)

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


def do_operations(session, vpc_dict):
    for region,vpc_ids in vpc_dict.items():
        client = session.client('ec2', region)
        ec2 = session.resource('ec2', region)
        for vpc_id in vpc_ids:
            vpc = ec2.Vpc(vpc_id)
            delete_nat_gws(client, vpc_id)
            delete_network_interfaces(vpc.network_interfaces.all())
            delete_vpc_peering_connections(vpc.accepted_vpc_peering_connections.all())
            delete_vpc_peering_connections(vpc.requested_vpc_peering_connections.all())
            delete_network_acls(vpc.network_acls.all())
            delete_route_tables(vpc.route_tables.all())
            delete_subnets(vpc.subnets.all())
            detach_and_delete_internet_gateway(vpc.internet_gateways.all())
            logger.info(f"Delete VPC: {vpc.id}")
            if LOCAL_INVOKE != "true":
                vpc.delete()


def delete_nat_gws(client,vpc_id):
    response = client.describe_nat_gateways(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc_id,
                ]
            },
        ],
    )
    for nat_gateway in response['NatGateways']:
        logger.info(f"Deleting NAT GW: {nat_gateway['NatGatewayId']}")
        if LOCAL_INVOKE != "true":
            client.delete_nat_gateway(NatGatewayId=nat_gateway['NatGatewayId'])


def delete_vpc_peering_connections(peering_connections):
    for peering in peering_connections:
        logger.info(f"Deleting VPC Peering Connections: {peering.id}")
        if LOCAL_INVOKE != "true":
            peering.delete()


def delete_network_interfaces(network_interfaces):
    for network_interface in network_interfaces:
        logger.info(f"Deleting Network Interfaces: {network_interface.network_interface_id}")
        if LOCAL_INVOKE != "true":
            network_interface.delete()


def delete_network_acls(network_acls):
    for acl in network_acls:
        logger.info(f"Deleting Network ACL: {acl.id}")
        if LOCAL_INVOKE != "true":
            acl.delete()


def delete_route_tables(route_tables):
    for rt in route_tables:
        logger.info(f"Deleting Route Table: {rt.id}")
        if LOCAL_INVOKE != "true":
            rt.delete()


def delete_subnets(subnets):
    for subnet in subnets:
        logger.info(f"Delete Subnet: {subnet.id}")
        if LOCAL_INVOKE != "true":
            subnet.delete()


def detach_and_delete_internet_gateway(gws):
    for gw in gws:
        logger.info(f"Detach and Delete: {gw.id}")
        if LOCAL_INVOKE != "true":
            gw.detach_from_vpc()
            gw.delete()
