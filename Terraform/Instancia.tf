provider "aws" {
  region = "us-east-1"
}

variable "db_username" {
  default = "admin"
}

variable "db_password" {
  default = "admin"
}

variable "db_host" {
  default = "10.33.4.10"
}

resource "aws_security_group" "flask_instances_sg" {
  name        = "flask-instances"
  description = "Allow SSH, HTTP, HTTPS, MySQL, and Flask"
  vpc_id      = "vpc-07eaffbed50b97e02"

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

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "test" {
  name               = "test-lb-tf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.flask_instances_sg.id]
  subnets            = ["subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"]

  enable_deletion_protection = false

  tags = {
    Environment = "production"
  }
}

resource "aws_lb" "prueba8" {
  name               = "prueba-lb-tf"
  internal           = false
  load_balancer_type = "network"
  subnets            = ["subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"]

  enable_deletion_protection = false

  tags = {
    Environment = "production"
  }
}

resource "aws_lb" "example" {
  name               = "example"
  load_balancer_type = "network"
  internal           = true

  subnet_mapping {
    subnet_id            = "subnet-0e3eee204d87cff0d"
    private_ipv4_address = "10.33.4.30"
  }

  subnet_mapping {
    subnet_id            = "subnet-0c3a053067ca6dd98"
    private_ipv4_address = "10.33.8.30"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_launch_template" "terralaunch" {
  name_prefix   = "terralaunch-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = "vockey"

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.flask_instances_sg.id]
  }

  iam_instance_profile {
    name = "LabInstanceProfile"  # típico en AWS Academy; quítalo si no existe
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    db_host     = var.db_host
    db_username = var.db_username
    db_password = var.db_password
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "terraform-instance"
    }
  }
}

resource "aws_autoscaling_group" "terraform_scaling" {
  name                = "terraform-asg"
  min_size            = 1
  max_size            = 4
  desired_capacity    = 1
  vpc_zone_identifier = [
    "subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"
  ]

  launch_template {
    id      = aws_launch_template.terralaunch.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "terraform-instance"
    propagate_at_launch = true
  }
}
