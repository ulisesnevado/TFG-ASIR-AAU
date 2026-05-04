resource "aws_instance" "monitor" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.monitor.id]
  associate_public_ip_address = true

  iam_instance_profile = var.iam_instance_profile

  tags = {
    Name = "${var.project_name}-monitor"
  }

  # Cuando integremos el código de tu compañero, le pasaremos un user_data aquí.
}