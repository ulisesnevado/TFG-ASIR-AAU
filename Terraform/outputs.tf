output "alb_dns_name" {
  description = "DNS del ALB - apunta tu CNAME www.fandefocas.es aquí"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID del ALB (por si IONOS soportara ALIAS)"
  value       = aws_lb.main.zone_id
}

output "rds_endpoint" {
  description = "Endpoint de RDS"
  value       = aws_db_instance.main.address
}

output "monitor_public_ip" {
  description = "IP pública de la EC2 Monitor"
  value       = aws_instance.monitor.public_ip
}