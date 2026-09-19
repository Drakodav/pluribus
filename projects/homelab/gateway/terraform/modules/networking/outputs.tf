output "subnet_id" {
  description = "OCID of the created subnet"
  value       = oci_core_subnet.homelab_subnet.id
}

output "vcn_id" {
  description = "OCID of the created VCN"
  value       = oci_core_vcn.homelab_vcn.id
}
