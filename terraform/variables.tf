variable "aws_region" {
  description = "AWS region (Mumbai by default)"
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  type    = string
  default = "sarps"
}

variable "instance_type" {
  description = "Free-tier eligible size"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of an existing EC2 key pair for SSH"
  type        = string
}

variable "admin_cidr" {
  description = "Your public IP in CIDR form, e.g. 203.0.113.10/32. Never use 0.0.0.0/0"
  type        = string
  validation {
    condition     = var.admin_cidr != "0.0.0.0/0"
    error_message = "admin_cidr must be a specific IP range, not 0.0.0.0/0."
  }
}

variable "docker_image" {
  description = "Image to run, e.g. youruser/sarps-web:latest"
  type        = string
}
