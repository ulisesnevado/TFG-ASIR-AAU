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

  enable_deletion_protection = true

  tags = {
    Environment = "production"
  }
}

resource "aws_lb" "lb_test" {
  name               = "test-lb-tf"
  internal           = false
  load_balancer_type = "network"
  subnets            = ["subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"]

  enable_deletion_protection = true

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
    private_ipv4_address = "10.33.4.20"
  }

  subnet_mapping {
    subnet_id            = "subnet-0c3a053067ca6dd98"
    private_ipv4_address = "10.33.2.20"
  }
}

resource "aws_launch_configuration" "terralaunch" {
  name_prefix                 = "terralaunch-"
  image_id                    = "ami-0ec10929233384c7f"
  instance_type               = "t2.micro"
  key_name                    = "vockey"
  security_groups             = [aws_security_group.flask_instances_sg.id]
  associate_public_ip_address = true

  user_data = <<-EOF
#!/bin/bash
set -x

apt update -y
apt upgrade -y

apt install -y python3 python3-pip git mysql-client ansible

pip3 install flask

cd /home/ubuntu
git clone https://github.com/ulisesnevado/TFG-ASIR-AAU
cd TFG-ASIR-AAU

if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
fi

mysql -h ${var.db_host} -u ${var.db_username} -p${var.db_password} -e "SHOW DATABASES;" || true

cat <<EOT > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TFG-ASIR-AAU
ExecStart=/usr/bin/python3 /home/ubuntu/TFG-ASIR-AAU/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp

echo "DB_HOST=${var.db_host}" >> /etc/environment
echo "DB_USER=${var.db_username}" >> /etc/environment
echo "DB_PASS=${var.db_password}" >> /etc/environment
echo "DB_NAME=foca_teste" >> /etc/environment

source /etc/environment

ansible-pull -U https://github.com/ulisesnevado/TFG-ASIR-AAU.git webserver.yml
EOF
}

resource "aws_autoscaling_group" "terrform_scaling" {
  min_size             = 1
  max_size             = 4
  desired_capacity     = 1
  launch_configuration = aws_launch_configuration.terralaunch.name

  vpc_zone_identifier = [
    "subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"
  ]

  tag {
    key                 = "Name"
    value               = "terraform-instance"
    propagate_at_launch = true
  }
}
