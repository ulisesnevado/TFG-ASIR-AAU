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
  description = "Allow SSH, HTTP, HTTPS, MySQL, and Flask"ç
  vpc_id      = "vpc-07eaffbed50b97e02"

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # MySQL
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flask (desde ALB)
  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Salida libre
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_autoscaling_group" "terrform_scaling" {
  min_size             = 1
  max_size             = 4
  desired_capacity     = 1
  launch_configuration = aws_launch_configuration.terramino.name
  vpc_zone_identifier = [
    "subnet-0e3eee204d87cff0d",
    "subnet-0c3a053067ca6dd98"
  ]

}

resource "aws_launch_template" "terralaunch" {
  ami                    = "ami-0ec10929233384c7f"
  instance_type          = "t2.micro"
  key_name               = "vockey"
  subnet_id              = "subnet-0e3eee204d87cff0d"
  vpc_security_group_ids = [aws_security_group.flask_instances_sg.id]
  associate_public_ip_address = true
  lifecycle {
      create_before_destroy = true
  }


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

# Comprobación conexión a la DB remota
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

  tags = {
    Name = "ubuntu-terra"
  }
}
