provider "aws" {
    region = "us-east-1"
}
resource "aws_security_group" "flask_instances_sg" {
  name        = "flask-instances"
  description = "Allow SSH, HTTP, HTTPS, MySQL, and Flask"

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

# -------------------------
# Load Balancer
# -------------------------
resource "aws_lb" "alb" {
  name               = "flask-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sg_alb.id]

  subnets = ["subnet-XXXX", "subnet-YYYY"]
}

# -------------------------
# Target Group
# -------------------------
resource "aws_lb_target_group" "tg" {
  name     = "flask-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = "vpc-XXXX"

  health_check {
    path = "/"
    port = "5000"
  }
}

# -------------------------
# Listener
# -------------------------
resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}


resource "aws_instance" "ubuntu_instance" {
  ami                    = "ami-0ec10929233384c7f"
  instance_type          = "t2.micro"
  key_name               = "vockey"
  vpc_security_group_ids = [aws_security_group.flask_instances_sg.id]

  user_data_base64 = base64encode(<<-EOF
    #!/bin/bash
    set -x

    apt update -y
    apt upgrade -y
    apt install -y python3 python3-pip git

    pip3 install flask

    cd /home/ubuntu
    git clone https://github.com/ulisesnevado/TFG-ASIR-AAU
    cd TFG-ASIR-AAU

    if [ -f requirements.txt ]; then
      pip3 install -r requirements.txt
    fi

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
  EOF
  )

  tags = {
    Name = "ubuntu-test"
  }
}

# -------------------------
# Attach EC2 al Target Group
# -------------------------
resource "aws_lb_target_group_attachment" "attach" {
  target_group_arn = aws_lb_target_group.tg.arn
  target_id        = aws_instance.ubuntu_instance.id
  port             = 5000
}