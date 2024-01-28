import boto3
import json
from datetime import datetime, timezone

# Define the regions and their descriptions
from datetime import timedelta
regions = ["us-east-1", "us-east-2", "us-west-1"]
region_descriptions = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)"
}
instance_type = "t2.large"

# Get spot price
def get_spot_price(region, instance_type):
    client = boto3.client('ec2', region_name=region)
    now = datetime.now(timezone.utc)
    response = client.describe_spot_price_history(
        InstanceTypes=[instance_type],
        ProductDescriptions=["Linux/UNIX"],
        StartTime=(now - timedelta(hours=1)).isoformat(),
        EndTime=now.isoformat(),
        MaxResults=1
    )
    if response['SpotPriceHistory']:
        return float(response['SpotPriceHistory'][0]['SpotPrice'])
    else:
        return None

# Get on-demand price
def get_on_demand_price(region, instance_type):
    client = boto3.client('pricing', region_name='us-east-1')
    region_description = region_descriptions[region]
    response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
            {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region_description},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'shared'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
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
        return None

# Calculate costs
def calculate_costs(price_per_hour, days):
    hours = days * 24
    return round(price_per_hour * hours, 2)

# Calculate percentage difference
def calculate_percentage_difference(on_demand_price, spot_price):
    if on_demand_price > 0:
        return round(((on_demand_price - spot_price) / on_demand_price) * 100, 2)
    else:
        return None

# Main execution
if __name__ == "__main__":
    for region in regions:
        spot_price = get_spot_price(region, instance_type)
        on_demand_price = get_on_demand_price(region, instance_type)

        print(f"Region: {region}")
        if spot_price is not None and on_demand_price is not None:
            percentage_difference = calculate_percentage_difference(on_demand_price, spot_price)
            print(f"  Spot Price (per hour): ${spot_price:.4f}")
            print(f"  On-Demand Price (per hour): ${on_demand_price:.4f}")
            print(f"  Percentage Difference: {percentage_difference}%")
            print(f"  Estimated Spot Costs - 7 Days: ${calculate_costs(spot_price, 7)}, 30 Days: ${calculate_costs(spot_price, 30)}, Annual: ${calculate_costs(spot_price, 365)}")
            print(f"  Estimated On-Demand Costs - 7 Days: ${calculate_costs(on_demand_price, 7)}, 30 Days: ${calculate_costs(on_demand_price, 30)}, Annual: ${calculate_costs(on_demand_price, 365)}")
        else:
            print("  Pricing information not available")
        print("\n")
