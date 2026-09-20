output "public_ip" {
  value       = oci_core_instance.gateway_node.public_ip
  description = "The public IP address of the gateway node."
}

output "instance_id" {
  value       = oci_core_instance.gateway_node.id
  description = "The OCID of the gateway compute instance."
}
