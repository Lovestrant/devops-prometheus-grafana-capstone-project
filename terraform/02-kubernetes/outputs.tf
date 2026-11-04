output "namespace" {
  value = kubernetes_namespace_v1.app.metadata[0].name
}

output "port_forward_command" {
  description = "Run this to open the app on http://localhost:8002"
  value       = "kubectl port-forward svc/tasktracker 8002:80 -n ${kubernetes_namespace_v1.app.metadata[0].name}"
}
