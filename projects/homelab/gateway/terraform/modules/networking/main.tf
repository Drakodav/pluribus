terraform {
  required_providers {
    oci = {
      source  = "hashicorp/oci"
      version = ">= 4.0.0"
    }
  }
}

# Virtual Cloud Network (VCN)
resource "oci_core_vcn" "homelab_vcn" {
  cidr_block     = var.vcn_cidr
  compartment_id = var.compartment_id
  display_name   = "${var.label_prefix}_vcn"
  dns_label      = var.label_prefix
}

# Internet Gateway
resource "oci_core_internet_gateway" "homelab_ig" {
  compartment_id = var.compartment_id
  display_name   = "${var.label_prefix}_internet_gateway"
  vcn_id         = oci_core_vcn.homelab_vcn.id
}

# Default Route Table
resource "oci_core_default_route_table" "homelab_rt" {
  manage_default_resource_id = oci_core_vcn.homelab_vcn.default_route_table_id
  display_name               = "${var.label_prefix}_route_table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.homelab_ig.id
  }
}

# Security List
resource "oci_core_security_list" "homelab_sl" {
  compartment_id = var.compartment_id
  display_name   = "${var.label_prefix}_security_list"
  vcn_id         = oci_core_vcn.homelab_vcn.id

  # Ingress Rules
  ingress_security_rules {
    protocol    = "6" # TCP
    source      = "0.0.0.0/0"
    description = "SSH"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol    = "6" # TCP
    source      = "0.0.0.0/0"
    description = "HTTP"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol    = "6" # TCP
    source      = "0.0.0.0/0"
    description = "HTTPS"
    tcp_options {
      min = 443
      max = 443
    }
  }

  ingress_security_rules {
    protocol    = "17" # UDP
    source      = "0.0.0.0/0"
    description = "WireGuard"
    udp_options {
      min = 51820
      max = 51820
    }
  }

  # Egress Rules
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# Subnet
resource "oci_core_subnet" "homelab_subnet" {
  cidr_block        = var.subnet_cidr
  display_name      = "${var.label_prefix}_subnet"
  dns_label         = "${var.label_prefix}sub"
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.homelab_vcn.id
  security_list_ids = [oci_core_security_list.homelab_sl.id]
  route_table_id    = oci_core_vcn.homelab_vcn.default_route_table_id
  dhcp_options_id   = oci_core_vcn.homelab_vcn.default_dhcp_options_id
}
