variable "tenancy_ocid" {
  description = "OCI Tenancy OCID"
  type        = string
}

variable "compartment_id" {
  description = "OCI Compartment OCID"
  type        = string
}

variable "subnet_id" {
  description = "OCID of the Subnet to place the instance in"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH Public Key for the instance"
  type        = string
}

variable "label_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "homelab"
}

variable "instance_shape" {
  description = "OCI Instance Shape"
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  description = "Number of OCPUs for ARM instance"
  type        = number
  default     = 2
}

variable "instance_memory_in_gbs" {
  description = "RAM in GBs for ARM instance"
  type        = number
  default     = 12
}

variable "availability_domain_index" {
  description = "Index of the availability domain to use (0, 1, or 2)"
  type        = number
  default     = 0
}
