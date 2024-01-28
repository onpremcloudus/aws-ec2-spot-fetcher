import boto3
import json

# Define the regions
regions = ["us-east-1", "us-east-2", "us-west-1"]
instance_type = "t2.large"

def get_on_demand_price(region, instance_type):
    # Map AWS region codes to their full names as expected by the Price List API
    region_descriptions = {
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-west-1": "US West (N. California)"
    }

    region_description = region_descriptions.get(region, region)

    client = boto3.client('pricing', region_name='us-east-1')
    response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region_description},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': 'No License required'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'shared'},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
        ],
        MaxResults=1
    )

    if response['PriceList']:
        price_list = json.loads(response['PriceList'][0])
        on_demand = price_list['terms']['OnDemand']
        price_dimensions = next(iter(on_demand.values()))['priceDimensions']
        price_per_hour = float(next(iter(price_dimensions.values()))['pricePerUnit']['USD'])
        return price_per_hour
    else:
        return "Price Not Found"

for region in regions:
    price = get_on_demand_price(region, instance_type)
    if price != "Price Not Found":
        print(f"Region: {region}, On-Demand Price (per hour): ${price:.4f}")
    else:
        print(f"Region: {region}, On-Demand Price: {price}")
