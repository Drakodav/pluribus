output "gateway_public_ip" {
  value       = module.compute.public_ip
  description = "The public IP address of the gateway node (aperio)."
}

output "gateway_instance_id" {
  value       = module.compute.instance_id
  description = "The OCID of the gateway compute instance."
}
