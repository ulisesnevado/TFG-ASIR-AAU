resource "aws_instance" "monitor" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  key_name                    = var.key_name
  subnet_id                   = aws_subnet.public[0].id
  vpc_security_group_ids      = [aws_security_group.monitor.id]
  associate_public_ip_address = true

  iam_instance_profile = var.iam_instance_profile

  user_data = base64encode(templatefile("${path.module}/monitor_user_data.sh", {
    github_repo = var.github_repo
  }))

  # Forzar recreación de la EC2 si cambia el user_data
  user_data_replace_on_change = true

  tags = {
    Name = "${var.project_name}-monitor"
  }
}
