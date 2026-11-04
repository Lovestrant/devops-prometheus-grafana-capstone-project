terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
  }
}

# Terraform talks to the cluster using your kubeconfig (the same one kubectl uses)
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = var.kube_context
}

resource "kubernetes_namespace_v1" "app" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_deployment_v1" "app" {
  metadata {
    name      = "tasktracker"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
    labels = {
      app = "tasktracker"
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = "tasktracker"
      }
    }

    template {
      metadata {
        labels = {
          app = "tasktracker"
        }
      }

      spec {
        container {
          name              = "tasktracker"
          image             = var.image
          image_pull_policy = "IfNotPresent"

          port {
            name           = "http"
            container_port = 8000
          }

          env {
            name  = "APP_GREETING"
            value = var.greeting
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            initial_delay_seconds = 3
            period_seconds        = 5
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "250m"
              memory = "128Mi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "app" {
  metadata {
    name      = "tasktracker"
    namespace = kubernetes_namespace_v1.app.metadata[0].name
  }

  spec {
    selector = {
      app = "tasktracker"
    }

    port {
      port        = 80
      target_port = "http"
    }
  }
}
