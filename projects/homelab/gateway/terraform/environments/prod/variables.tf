variable "tenancy_ocid" {
  description = "OCI Tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "OCI User OCID"
  type        = string
}

variable "fingerprint" {
  description = "OCI API Key Fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to OCI Private Key"
  type        = string
}

variable "region" {
  description = "OCI Region"
  type        = string
  default     = "us-ashburn-1"
}

variable "compartment_id" {
  description = "OCI Compartment OCID"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH Public Key for the instance"
  type        = string
}

variable "instance_shape" {
  description = "OCI Instance Shape"
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  description = "Number of OCPUs for ARM instance"
  type        = number
  default     = 4
}

variable "instance_memory_in_gbs" {
  description = "RAM in GBs for ARM instance"
  type        = number
  default     = 24
}

variable "availability_domain_index" {
  description = "Index of the availability domain to use (0, 1, or 2)"
  type        = number
  default     = 0
}
