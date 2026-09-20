variable "compartment_id" {
  description = "OCI Compartment OCID"
  type        = string
}

variable "label_prefix" {
  description = "Prefix for resource names and DNS labels"
  type        = string
  default     = "homelab"
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the Subnet"
  type        = string
  default     = "10.0.1.0/24"
}
