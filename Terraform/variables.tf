variable "aws_region" {
  description = "Región AWS"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefijo para nombrar recursos"
  type        = string
  default     = "foca"
}

variable "vpc_cidr" {
  description = "CIDR de la VPC"
  type        = string
  default     = "10.33.0.0/16"
}

variable "public_subnets" {
  description = "CIDRs de subnets públicas"
  type        = list(string)
  default     = ["10.33.1.0/24", "10.33.2.0/24"]
}

variable "private_subnets" {
  description = "CIDRs de subnets privadas (RDS)"
  type        = list(string)
  default     = ["10.33.10.0/24", "10.33.11.0/24"]
}

variable "azs" {
  description = "Availability Zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "instance_type" {
  description = "Tipo de instancia EC2 para Flask"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Nombre de la key pair"
  type        = string
  default     = "vockey"
}

variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "db_foca"
}

variable "db_username" {
  description = "Usuario master de RDS"
  type        = string
  default     = "focaadmin"
}

variable "db_password" {
  description = "Password del usuario master de RDS"
  type        = string
  default     = "foca.tfg.2026!!"
  sensitive   = true
}

variable "acm_certificate_arn" {
  description = "ARN del certificado ACM en us-east-1 para fandefocas.es"
  type        = string
}

variable "github_repo" {
  description = "Repo desde el que ansible-pull clona la configuración"
  type        = string
  default     = "https://github.com/ulisesnevado/TFG-ASIR-AAU"
}

variable "iam_instance_profile" {
  description = "Instance profile precreado por AWS Academy"
  type        = string
  default     = "LabInstanceProfile"
}