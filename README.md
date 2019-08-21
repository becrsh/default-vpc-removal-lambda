# default-vpc-removal-lambda

A Lambda that will query every region and destroy the default VPC. It will run on a schedule of 7 days.

## TODO
* Setup Notification
* Removal of VPN Gateway and customer gateways attached to the vpc
* Removal of VPC Endpoints attached to the vpc 

## Installation

The Lambda is available in the Serverless Application Repository

## Local Installation

Make sure that you have [installed SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) on your local machine. Use SAM Package
and deploy to install the lambda in your account.

Firstly, we need a `S3 bucket` where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```

Next, run the following command to package our Lambda function to S3:

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME
```

Next, the following command will create a Cloudformation Stack and deploy your SAM resources.

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name default-vpc-removal-lambda \
    --capabilities CAPABILITY_IAM
```

> **See [Serverless Application Model (SAM) HOWTO Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-quick-start.html) for more details in how to get started.**


## IAM Role

The lambda requires permissions in the Account. The following role is created
for the lambda:

```json
{
    "Statement": [
        {
            "Action": [
                "ec2:DeleteSubnet",
                "ec2:DeleteClientVpnEndpoint",
                "ec2:DeleteVpcPeeringConnection",
                "ec2:DeleteVpcEndpoints",
                "ec2:DescribeClientVpnConnections",
                "ec2:DescribeByoipCidrs",
                "ec2:DeleteRouteTable",
                "ec2:DisassociateVpcCidrBlock",
                "ec2:DeleteVpnGateway",
                "ec2:DescribeAccountAttributes",
                "ec2:DeleteInternetGateway",
                "ec2:DescribeNetworkInterfacePermissions",
                "ec2:DeleteVpnConnection",
                "ec2:DescribeNetworkAcls",
                "ec2:DescribeRouteTables",
                "ec2:DescribeClientVpnEndpoints",
                "ec2:DescribeEgressOnlyInternetGateways",
                "ec2:DescribeClientVpnRoutes",
                "ec2:DescribeVpcClassicLinkDnsSupport",
                "ec2:DescribeVpnConnections",
                "ec2:DescribeVpcPeeringConnections",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeClientVpnTargetNetworks",
                "ec2:DetachInternetGateway",
                "ec2:DescribeVpcEndpointServiceConfigurations",
                "ec2:DisassociateRouteTable",
                "ec2:DescribeVpcClassicLink",
                "ec2:DetachVpnGateway",
                "ec2:DescribeVpcEndpointServicePermissions",
                "ec2:DeleteNatGateway",
                "ec2:DescribeVpcEndpoints",
                "ec2:DeleteVpc",
                "ec2:DescribeSubnets",
                "ec2:DeleteNetworkAclEntry",
                "ec2:DescribeVpnGateways",
                "ec2:DescribeAddresses",
                "ec2:DescribeRegions",
                "ec2:DescribeVpcEndpointServices",
                "ec2:DeleteVpcEndpointServiceConfigurations",
                "ec2:DescribeVpcAttribute",
                "ec2:DeleteNetworkInterfacePermission",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeNetworkInterfaceAttribute",
                "ec2:DescribeVpcEndpointConnections",
                "ec2:DeleteNetworkAcl",
                "ec2:DeleteEgressOnlyInternetGateway",
                "ec2:DetachNetworkInterface",
                "ec2:DisassociateClientVpnTargetNetwork",
                "ec2:DeleteRoute",
                "ec2:DescribeNatGateways",
                "ec2:DisassociateSubnetCidrBlock",
                "ec2:DescribeVpcEndpointConnectionNotifications",
                "ec2:DescribeSecurityGroups",
                "ec2:DeleteVpnConnectionRoute",
                "ec2:DeleteVpcEndpointConnectionNotifications",
                "ec2:DeleteCustomerGateway",
                "ec2:DescribeSecurityGroupReferences",
                "ec2:DescribeVpcs",
                "ec2:DeleteClientVpnRoute",
                "ec2:DescribeClientVpnAuthorizationRules",
                "ec2:DescribePublicIpv4Pools",
                "ec2:DeleteSecurityGroup",
                "ec2:DescribeStaleSecurityGroups",
                "ec2:DescribeInternetGateways"
            ],
            "Resource": "*",
            "Effect": "Allow",
            "Sid": "AllowVPCActions"
        }
    ]
}
```
