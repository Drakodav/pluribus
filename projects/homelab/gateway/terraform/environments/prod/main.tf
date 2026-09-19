module "networking" {
  source         = "../../modules/networking"
  compartment_id = var.compartment_id
  label_prefix   = "homelab"
}

module "compute" {
  source                    = "../../modules/compute"
  tenancy_ocid              = var.tenancy_ocid
  compartment_id            = var.compartment_id
  subnet_id                 = module.networking.subnet_id
  ssh_public_key            = var.ssh_public_key
  label_prefix              = "homelab"
  instance_shape            = var.instance_shape
  instance_ocpus            = var.instance_ocpus
  instance_memory_in_gbs    = var.instance_memory_in_gbs
  availability_domain_index = var.availability_domain_index
}
