provider "aws" {
  region = "us-east-2"
}

# Create a new VPC
resource "aws_vpc" "ub_ov_d1" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "ub-ov-d1"
  }
}

# Create an internet gateway for the VPC
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.ub_ov_d1.id
}

# Create a subnet within the VPC
resource "aws_subnet" "subnet" {
  vpc_id     = aws_vpc.ub_ov_d1.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "ub-ov-d1-subnet"
  }
}

# Create a security group
resource "aws_security_group" "sg1_ub_ov_d1" {
  name        = "sg1-ub-ov-d1"
  description = "Allow SSH, HTTP, HTTPS"
  vpc_id      = aws_vpc.ub_ov_d1.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Request a Spot Instance
resource "aws_spot_instance_request" "spot_instance" {
  ami           = "ami-05fb0b8c1424f266b" # Ubuntu 22.04 LTS AMI in us-east-2
  instance_type = "t2.large"
  key_name      = "dog1"

  subnet_id          = aws_subnet.subnet.id
  vpc_security_group_ids = [aws_security_group.sg1_ub_ov_d1.id]

  root_block_device {
    volume_type = "gp2"
    volume_size = 10
  }

  tags = {
    Name = "ub-ov-d1"
  }
}

# DNS Configuration (A Record)
# This part will depend on how your DNS is managed, for example using AWS Route53.
