terraform {
  required_version = ">= 1.5.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

variable "student_name" {
  description = "Your name - it will be written into the file"
  type        = string
  default     = "student"
}

# A resource that generates a random two-word name, e.g. "happy-lion"
resource "random_pet" "server" {
  length = 2
}

# A resource that creates a text file on your computer
resource "local_file" "hello" {
  filename = "${path.module}/output/hello-${random_pet.server.id}.txt"
  content  = "Hello ${var.student_name}! Terraform created this file for server ${random_pet.server.id}.\n"
}

output "server_name" {
  value = random_pet.server.id
}

output "file_path" {
  value = local_file.hello.filename
}
