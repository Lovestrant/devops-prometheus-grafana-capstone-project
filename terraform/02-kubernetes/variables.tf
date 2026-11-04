variable "kube_context" {
  description = "kubectl context to use (kind names it kind-<cluster name>)"
  type        = string
  default     = "kind-devops"
}

variable "namespace" {
  description = "Namespace Terraform will create (different from the one made with kubectl)"
  type        = string
  default     = "tasktracker-tf"
}

variable "image" {
  description = "Container image to run"
  type        = string
  default     = "tasktracker:1.0.0"
}

variable "replicas" {
  description = "How many copies (pods) of the app to run"
  type        = number
  default     = 2
}

variable "greeting" {
  description = "Message returned by the app's home page"
  type        = string
  default     = "Hello from Terraform!"
}
