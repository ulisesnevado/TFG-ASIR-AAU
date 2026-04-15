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


    resource "aws_instance" "ubuntu_instance" {
        ami = "ami-0ec10929233384c7f"
        instance_type = "t2.micro"
        key_name = "vockey"
        vpc_security_group_ids = [aws_security_group.flask_instances_sg.id]
        tags = {
        Name = "ubuntu-test"
    }
}