terraform {
  required_providers {
    oci = {
      source  = "hashicorp/oci"
      version = ">= 4.0.0"
    }
  }
}

# Availability Domains
data "oci_identity_availability_domains" "ad" {
  compartment_id = var.tenancy_ocid
}

# Fetch the latest Canonical Ubuntu 24.04 ARM image
data "oci_core_images" "ubuntu_arm" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "24.04"
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

# Always-Free Compute Instance (aperio)
resource "oci_core_instance" "gateway_node" {
  availability_domain = data.oci_identity_availability_domains.ad.availability_domains[var.availability_domain_index].name
  compartment_id      = var.compartment_id
  display_name        = "${var.label_prefix}-gateway-node"
  shape               = var.instance_shape

  dynamic "shape_config" {
    for_each = can(regex("Flex$", var.instance_shape)) ? [1] : []
    content {
      ocpus         = var.instance_ocpus
      memory_in_gbs = var.instance_memory_in_gbs
    }
  }

  create_vnic_details {
    subnet_id        = var.subnet_id
    display_name     = "primary-vnic"
    assign_public_ip = true
    hostname_label   = "${var.label_prefix}-gateway"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_arm.images[0].id
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
  }

  preserve_boot_volume = false
}
