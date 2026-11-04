# DevOps Capstone: Git → Docker → Kubernetes → Prometheus + Grafana → Jenkins → Terraform

One small project, six tools. You will take a tiny Python web app called **TaskTracker** and, step by step:

1. Track its code with **Git**
2. Package it with **Docker**
3. Run it on **Kubernetes**
4. Watch it with **Prometheus** and **Grafana**
5. Automate testing and building with **Jenkins**
6. Create its infrastructure with **Terraform**

You do not need to know any Python. Every command is copy-and-paste. Every module ends with a **Checkpoint** so you know it worked before moving on.

**Total time:** about 12 to 15 hours. Do one module per sitting.

---

## How the pieces fit together

```
  You ── git push ──▶ GitHub ──▶ JENKINS
                                   │  1. run tests
                                   │  2. docker build
                                   │  3. smoke test
                                   │  4. (optional) push + deploy
                                   ▼
                              DOCKER IMAGE
                                   │
        TERRAFORM ── creates ──▶ KUBERNETES cluster (kind) ── runs ──▶ app pods
                                                                          │ /metrics
                                         GRAFANA ◀── queries ── PROMETHEUS ┘
```

| Tool | The question it answers |
|---|---|
| Git | "What changed, who changed it, and can I undo it?" |
| Docker | "How do I make my app run the same way everywhere?" |
| Kubernetes | "How do I run many copies, keep them alive, and update them safely?" |
| Prometheus | "How is my app behaving right now?" (collects numbers) |
| Grafana | "Can I see those numbers as graphs?" |
| Jenkins | "How do I test and build automatically on every change?" |
| Terraform | "How do I describe my infrastructure in files instead of clicking?" |

---

## Module 0: Setup (about 1 hour)

### What to install

| Tool | Where to get it |
|---|---|
| Git | https://git-scm.com/downloads |
| Docker Desktop (Windows/Mac) or Docker Engine (Linux) | https://docs.docker.com/get-docker/ |
| kubectl | https://kubernetes.io/docs/tasks/tools/ |
| kind (Kubernetes in Docker) | https://kind.sigs.k8s.io/docs/user/quick-start/#installation |
| Terraform | https://developer.hashicorp.com/terraform/install |
| Python 3.10+ (optional, only for Module 2 and the traffic script) | https://www.python.org/downloads/ |
| A free GitHub account | https://github.com |

**Windows users:** use **WSL 2** (Ubuntu) or **Git Bash** as your terminal. Every command here is written for a bash-style shell.

**Computer needs:** 8 GB RAM minimum (16 GB is better), about 15 GB free disk.

### Check everything works

```bash
git --version
docker --version
docker compose version
kubectl version --client
kind --version
terraform -version
```

Each command should print a version number. Then confirm Docker is actually running:

```bash
docker run --rm hello-world
```

You should see "Hello from Docker!".

### Ports used in this project

| Port | What | When |
|---|---|---|
| 8000 | TaskTracker (Docker / Compose) | Modules 3, 4 |
| 9090 | Prometheus (Compose) | Module 4 |
| 3000 | Grafana (Compose) | Module 4 |
| 8001 / 9091 / 3001 | App / Prometheus / Grafana (Kubernetes port-forward) | Modules 5, 6 |
| 8080 | Jenkins | Module 7 |
| 8002 | App deployed by Terraform | Module 8 |

If a port is already in use on your machine, stop whatever is using it or change the left-hand number in the command.

### Project map

```
devops-capstone/
├── app/                     The TaskTracker app (Python/Flask)
│   ├── app.py               The code
│   ├── test_app.py          Automated tests
│   ├── Dockerfile           Recipe to build the Docker image
│   └── requirements*.txt    Python dependencies
├── docker-compose.yml       App + Prometheus + Grafana on your laptop
├── monitoring/              Prometheus + Grafana configuration
├── k8s/                     Kubernetes manifests (YAML)
│   ├── kind-config.yaml     Local cluster definition
│   ├── app/                 Namespace, ConfigMap, Deployment, Service
│   ├── monitoring/          Prometheus and Grafana inside the cluster
│   └── extras/              Traffic generator
├── Jenkinsfile              The CI pipeline
├── jenkins/                 Runs Jenkins in Docker
├── terraform/
│   ├── 01-basics/           Learn Terraform with no cloud and no cluster
│   └── 02-kubernetes/       Deploy the app to Kubernetes with Terraform
└── scripts/traffic.py       Sends fake traffic so graphs have data
```

### What the app does

| Endpoint | Purpose |
|---|---|
| `GET /` | Greeting, version, and the name of the container that answered |
| `GET /health` | Health check used by Docker and Kubernetes |
| `GET /tasks`, `POST /tasks`, `DELETE /tasks/<id>` | A tiny to-do list kept in memory |
| `GET /slow` | Responds slowly on purpose (for latency graphs) |
| `GET /error` | Always fails with HTTP 500 (for error graphs) |
| `GET /metrics` | Numbers for Prometheus |

---

## Module 1: Git (about 1 hour)

**Goal:** put the project under version control, practice branching and merging, and publish it to GitHub. Jenkins will need it there in Module 7.

### Concepts

- **Repository (repo):** a project folder whose history Git tracks.
- **Commit:** a saved snapshot with a message.
- **Branch:** a separate line of work, so experiments do not break the main code.
- **Merge:** combining a branch back into another.
- **Remote:** a copy of the repo on a server such as GitHub.

### Steps

**1. Tell Git who you are (one time only):**

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**2. Create the repository** from inside the `devops-capstone` folder:

```bash
cd devops-capstone
git init -b main
git status
```

`git status` lists every file as "untracked". The `.gitignore` file already tells Git to ignore junk such as `venv/` and Terraform state.

**3. Make the first commit:**

```bash
git add .
git commit -m "Initial commit: TaskTracker DevOps capstone"
git log --oneline
```

**4. Work on a branch.** Create one, then change the greeting:

```bash
git switch -c feature/new-greeting
```

Open `app/app.py` and change this line:

```python
APP_GREETING = os.getenv("APP_GREETING", "Hello from TaskTracker!")
```

to:

```python
APP_GREETING = os.getenv("APP_GREETING", "Welcome to my DevOps project!")
```

See exactly what changed, then commit it:

```bash
git diff
git add app/app.py
git commit -m "Change default greeting"
```

**5. Merge it back into main:**

```bash
git switch main
git merge feature/new-greeting
git log --oneline --graph
git branch -d feature/new-greeting
```

**6. Tag a release:**

```bash
git tag v1.0.0
git tag
```

**7. Publish to GitHub.** On github.com, click **New repository**, name it `devops-capstone`, make it **Public** (Jenkins can then clone it without a password), and do **not** add a README. Then run (replace `YOUR-USERNAME`):

```bash
git remote add origin https://github.com/YOUR-USERNAME/devops-capstone.git
git push -u origin main
git push --tags
```

GitHub asks you to sign in. If your password is rejected, create a **Personal Access Token** (GitHub → Settings → Developer settings) and paste it as the password.

### Checkpoint

Refresh your GitHub repo page. You should see all the project files and your commit history.

### Try it yourself

- Make a second branch, change a different line, and merge it.
- Run `git revert HEAD` to undo your last commit safely, then `git log --oneline` to see how Git records it.
- Create a deliberate merge conflict: change the same line on two branches, merge both, and learn to fix it.

---

## Module 2: Run the app and its tests (about 30 minutes)

**Python is optional here.** If you would rather not install it, skip to Module 3. Docker will run everything, and Jenkins runs the tests for you in Module 7.

**Goal:** see the app working before wrapping it in anything.

```bash
cd app
python3 -m venv venv
source venv/bin/activate          # Windows Git Bash: source venv/Scripts/activate
pip install -r requirements-dev.txt
pytest
```

You should see `7 passed`. These tests are what Jenkins will run automatically later.

Start the app:

```bash
python app.py
```

Open http://localhost:8000 in your browser. You will see JSON with a greeting. Also open http://localhost:8000/health and http://localhost:8000/metrics.

In a **second terminal**, create a task:

```bash
curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Learn Docker"}'
curl http://localhost:8000/tasks
```

Stop the app with `Ctrl+C`, then leave the virtual environment and go back to the project root:

```bash
deactivate
cd ..
```

### Checkpoint

You saw the greeting, `/health`, and your task in the list.

> **Look at `/metrics`.** That plain-text page is how Prometheus will read the app's numbers. Notice lines starting with `app_http_requests_total`.

---

## Module 3: Docker (about 1.5 hours)

**Goal:** package the app into an image and run it as a container.

### Concepts

- **Image:** a read-only template containing your app and everything it needs.
- **Container:** a running instance of an image. You can start many from one image.
- **Dockerfile:** the recipe for building an image.
- **Layer cache:** Docker reuses unchanged steps, so rebuilds are fast.

### Read the Dockerfile

Open `app/Dockerfile`. Each step has a comment. The key idea: dependencies are copied and installed **before** the code, so changing `app.py` does not reinstall everything.

### Build and run

```bash
docker build -t tasktracker:1.0.0 ./app
docker images tasktracker
```

Run it. `-p 8000:8000` connects port 8000 on your laptop to port 8000 in the container:

```bash
docker run -d --name tasktracker -p 8000:8000 tasktracker:1.0.0
docker ps
```

Test it:

```bash
curl http://localhost:8000
```

Look at `served_by`: that is the **container ID**, not your laptop name.

### Everyday Docker commands

```bash
docker logs tasktracker             # see the app's output
docker logs -f tasktracker          # follow logs live (Ctrl+C to stop)
docker exec -it tasktracker bash    # open a shell inside (type exit to leave)
docker stop tasktracker             # stop it
docker rm tasktracker               # delete the stopped container
```

### Configure with an environment variable

```bash
docker run -d --name tasktracker -p 8000:8000 -e APP_GREETING="Hi from my container" tasktracker:1.0.0
curl http://localhost:8000
docker rm -f tasktracker
```

### Checkpoint

You can build an image, run it, change its greeting without rebuilding, and remove it.

### Try it yourself

- Edit `app.py`, rebuild, and watch the output: steps using the cache say `CACHED`.
- Run two containers from the same image on ports 8000 and 8100. Both work independently.
- Run `docker history tasktracker:1.0.0` to see the layers.

---

## Module 4: Docker Compose + Prometheus + Grafana (about 2 hours)

**Goal:** start three connected containers with one command, then see live graphs.

### Concepts

- **Docker Compose:** describes several containers in one YAML file.
- **Prometheus:** every few seconds it visits `/metrics` on the app and stores the numbers (a "time series database").
- **Grafana:** draws graphs by asking Prometheus questions written in **PromQL**.

### Start everything

From the project root:

```bash
docker compose up -d --build
docker compose ps
```

You should see `tasktracker`, `prometheus`, and `grafana` running.

### Explore each service

1. **App:** http://localhost:8000
2. **Prometheus:** http://localhost:9090. Open **Status → Targets**. The `tasktracker` target should be **UP**. Open **Alerts** to see the two alert rules from `monitoring/alert-rules.yml`.
3. **Grafana:** http://localhost:3000. Log in with `admin` / `admin` (skip the password-change prompt). Open **Dashboards → TaskTracker Overview**.

The dashboard is empty because nobody is using the app. Generate traffic. Without Python, use this bash loop:

```bash
while true; do curl -s -o /dev/null localhost:8000/; curl -s -o /dev/null localhost:8000/slow; curl -s -o /dev/null localhost:8000/error; sleep 0.3; done
```

With Python (works on any system):

```bash
python scripts/traffic.py
```

Stop either with `Ctrl+C`. Watch the dashboard (it refreshes every 5 seconds): requests per second by endpoint, error percentage, and 95th-percentile latency all move.

### Try PromQL in Prometheus

In the Prometheus page, open **Graph**, paste a query, and click **Execute**, then open the **Graph** tab:

| Query | What it shows |
|---|---|
| `up` | 1 = target reachable, 0 = down |
| `app_http_requests_total` | Total requests since the app started, by endpoint and status |
| `rate(app_http_requests_total[1m])` | Requests per second over the last minute |
| `sum by (endpoint) (rate(app_http_requests_total[1m]))` | The same, grouped by endpoint |
| `app_tasks_total` | Current number of tasks |

### Trigger an alert

```bash
docker stop tasktracker
```

Wait about 40 seconds, then open Prometheus **Alerts**. `TaskTrackerDown` turns **FIRING**. Start the app again:

```bash
docker start tasktracker
```

### Shut down

```bash
docker compose down
```

### Checkpoint

You saw a live dashboard, ran at least two PromQL queries, and made an alert fire.

### Try it yourself

- In Grafana, click a panel title → **Edit** to see its query.
- Add a new panel for `app_tasks_total`.
- Add a new alert rule for p95 latency above 1 second.

---

## Module 5: Kubernetes (about 3 hours)

**Goal:** run the app in a real (local) Kubernetes cluster and see scaling, self-healing and rolling updates.

### Concepts

| Word | Meaning |
|---|---|
| **Cluster** | A group of machines running Kubernetes |
| **Node** | One machine in the cluster (here, a Docker container pretending to be one) |
| **Pod** | The smallest unit: one or more containers that run together |
| **Deployment** | "Keep N copies of this pod running, and update them safely" |
| **Service** | A stable address that load-balances across pods |
| **Namespace** | A folder that groups resources |
| **ConfigMap** | Settings stored outside the image |

Everything in Kubernetes is described in **YAML manifests**. You tell Kubernetes the state you *want*, and it keeps making reality match.

### 1. Create the cluster

```bash
kind create cluster --name devops --config k8s/kind-config.yaml
kubectl cluster-info --context kind-devops
kubectl get nodes
```

You should see 3 nodes (1 control-plane, 2 workers), all `Ready`. This takes a few minutes the first time.

> **Low on RAM?** Delete the two `- role: worker` lines in `k8s/kind-config.yaml` for a single-node cluster.

### 2. Give the cluster your image

The cluster cannot see images on your laptop automatically. Load it in:

```bash
docker build -t tasktracker:1.0.0 ./app
kind load docker-image tasktracker:1.0.0 --name devops
```

### 3. Deploy the app

Read the files in `k8s/app/` first. They are short and commented. Then:

```bash
kubectl apply -f k8s/app/
kubectl get all -n tasktracker
```

Wait until both pods show `Running` and `1/1` ready:

```bash
kubectl get pods -n tasktracker -w     # Ctrl+C to stop watching
```

Which node is each pod on?

```bash
kubectl get pods -n tasktracker -o wide
```

### 4. Reach the app

Services are only reachable inside the cluster by default. Forward a local port to the Service (leave this terminal open):

```bash
kubectl port-forward svc/tasktracker 8001:80 -n tasktracker
```

In another terminal:

```bash
curl http://localhost:8001
```

> **Why does `served_by` always show the same pod?** `kubectl port-forward` connects to a *single* pod behind the Service. In Module 6 you will send traffic from inside the cluster, where the Service really does spread requests across pods.

### 5. Scaling

```bash
kubectl scale deployment tasktracker --replicas=4 -n tasktracker
kubectl get pods -n tasktracker
kubectl scale deployment tasktracker --replicas=2 -n tasktracker
```

### 6. Self-healing

Delete a pod and watch Kubernetes replace it:

```bash
kubectl get pods -n tasktracker
kubectl delete pod <paste-one-pod-name> -n tasktracker
kubectl get pods -n tasktracker
```

A new pod appears within seconds, because the Deployment says "2 replicas".

### 7. Change configuration

Edit `k8s/app/01-configmap.yaml` (change the greeting text), then:

```bash
kubectl apply -f k8s/app/01-configmap.yaml
kubectl rollout restart deployment/tasktracker -n tasktracker
kubectl rollout status deployment/tasktracker -n tasktracker
```

Restart your `port-forward` (it was attached to an old pod) and `curl` again to see the new greeting.

### 8. Rolling update and rollback

Build a new version of the image, load it, and switch the Deployment to it:

```bash
docker build --build-arg APP_VERSION=1.0.1 -t tasktracker:1.0.1 ./app
kind load docker-image tasktracker:1.0.1 --name devops
kubectl set image deployment/tasktracker tasktracker=tasktracker:1.0.1 -n tasktracker
kubectl rollout status deployment/tasktracker -n tasktracker
```

Kubernetes replaces pods one at a time so there is no downtime. The version in `curl` output is now `1.0.1`. Now undo it:

```bash
kubectl rollout history deployment/tasktracker -n tasktracker
kubectl rollout undo deployment/tasktracker -n tasktracker
```

### 9. Debugging toolkit

```bash
kubectl describe pod <pod-name> -n tasktracker    # events at the bottom explain most problems
kubectl logs <pod-name> -n tasktracker
kubectl exec -it <pod-name> -n tasktracker -- bash
```

Common statuses: `ImagePullBackOff` means the image is not in the cluster (re-run `kind load`); `CrashLoopBackOff` means the app keeps crashing (read its logs); `Pending` means no room for it.

### Checkpoint

You deployed 2 pods, scaled them, deleted one and watched it return, and did a rolling update plus rollback.

### Try it yourself

- Set `replicas: 3` in `02-deployment.yaml`, run `kubectl apply -f k8s/app/`, and see the change.
- Set a wrong image name, apply, and use `describe` to find the error. Then fix it.
- Lower the memory limit to `10Mi` and see what happens (`OOMKilled`).

---

## Module 6: Prometheus + Grafana on Kubernetes (about 1.5 hours)

**Goal:** monitor the Kubernetes deployment. Prometheus now **discovers pods automatically**, so new pods are monitored without any config change.

### Deploy the monitoring stack

Stop any port-forward from Module 5 (`Ctrl+C`), then:

```bash
kubectl apply -f k8s/monitoring/
kubectl get pods -n monitoring -w
```

Wait until `prometheus-...` and `grafana-...` are `Running` and ready (Grafana can take about a minute). Press `Ctrl+C` to stop watching.

### Open them

Use two terminals (each command keeps running):

```bash
kubectl port-forward svc/prometheus 9091:9090 -n monitoring
```

```bash
kubectl port-forward svc/grafana 3001:3000 -n monitoring
```

- Prometheus: http://localhost:9091. Open **Status → Targets**. You should see **two** `tasktracker` targets, one per pod.
- Grafana: http://localhost:3001 (`admin` / `admin`). Open **Dashboards → TaskTracker Overview**.

### Send traffic from inside the cluster

```bash
kubectl apply -f k8s/extras/traffic-generator.yaml
```

Within a minute, the dashboard fills up. The "App instances up" panel shows 2.

### Watch Prometheus follow the cluster

```bash
kubectl scale deployment tasktracker --replicas=4 -n tasktracker
```

Refresh **Status → Targets** after about 15 seconds: four targets, with no configuration change. Scale back down:

```bash
kubectl scale deployment tasktracker --replicas=2 -n tasktracker
```

Also try this PromQL query to compare pods:

```
sum by (pod) (rate(app_http_requests_total[1m]))
```

### Checkpoint

You saw Prometheus discover pods by itself and Grafana show live data from the cluster.

### Understand the wiring

| File | Role |
|---|---|
| `02-prometheus-config.yaml` | Prometheus settings stored in a **ConfigMap** |
| `01-prometheus-rbac.yaml` | Permission for Prometheus to list pods |
| `04-grafana-config.yaml` | A **Secret** (admin password) and the data source settings |
| `05-grafana-dashboard.yaml` | The dashboard JSON stored in a ConfigMap |

### Clean up the traffic generator

```bash
kubectl delete -f k8s/extras/traffic-generator.yaml
```

### Try it yourself

- Check the **Alerts** page in Prometheus. Scale the app to 0 replicas: `TaskTrackerDown` does not fire because there are no targets at all. Think about why, and what alert would catch it instead.
- Edit the dashboard JSON `expr` for one panel and re-apply `05-grafana-dashboard.yaml`, then restart Grafana: `kubectl rollout restart deployment/grafana -n monitoring`.

---

## Module 7: Jenkins CI (about 2 hours)

**Goal:** every time you press **Build**, Jenkins gets the code from GitHub, runs tests, builds the Docker image, and smoke-tests the container.

### Concepts

- **Pipeline:** a series of automatic steps (checkout, test, build, ...).
- **Jenkinsfile:** the pipeline written as code and stored in the repo, so it is versioned with Git.
- **Stage:** one named step shown as a box in the Jenkins UI.
- **CI (Continuous Integration):** automatically testing every change.

### 1. Start Jenkins

```bash
cd jenkins
docker compose up -d --build
cd ..
```

The first build downloads a lot (about 5 minutes). Get the first-time password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080 and paste it. Choose **Install suggested plugins**, create your admin user, and accept the default URL.

> Jenkins here runs as root with access to your Docker socket, so its jobs can control your Docker. That is fine on a personal laptop for learning, never for a shared server.

### 2. Read the Jenkinsfile

Open `Jenkinsfile`. The stages are:

| Stage | What it does |
|---|---|
| Checkout | Downloads the code from your repo |
| Test | Creates a Python virtual environment and runs `pytest` |
| Build Image | `docker build` with the build number as the tag |
| Smoke Test | Starts the container and checks `/health` |
| Push Image | Optional: pushes to Docker Hub |
| Deploy to Kubernetes | Optional: updates the Deployment |

The `post` block always removes the smoke-test container, even when the build fails.

### 3. Make sure your latest code is on GitHub

```bash
git add .
git commit -m "Update project"
git push
```

(If there is nothing to commit, that is fine.)

### 4. Create the pipeline job

1. Jenkins home → **New Item**
2. Name: `tasktracker`, choose **Pipeline**, click **OK**
3. Scroll to **Pipeline** and set:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/YOUR-USERNAME/devops-capstone.git`
   - **Branch Specifier:** `*/main`
   - **Script Path:** `Jenkinsfile`
4. **Save**, then click **Build Now**

Click build **#1**, then **Console Output** to watch it. You can also open **Stage View** to see the colored boxes.

> **First-run quirk:** the first build of a pipeline with parameters runs without them. After build #1, the button becomes **Build with Parameters**.

### 5. Break it on purpose

1. In `app/test_app.py`, change `assert response.status_code == 200` in `test_health_is_ok` to `== 201`.
2. Commit and push, then build again.
3. The **Test** stage turns red and later stages never run. That is the whole point of CI: broken code never becomes an image.
4. Fix it, push, and build again for green.

### 6. Automatic builds (optional)

In the job → **Configure → Build Triggers → Poll SCM**, set the schedule to `H/2 * * * *`. Jenkins now checks GitHub every few minutes and builds when it finds new commits.

### Stretch goal: push to Docker Hub and deploy to Kubernetes

1. Create a free Docker Hub account and an **Access Token**. Create a **public** repository named `tasktracker`.
2. In Jenkins: **Manage Jenkins → Credentials → (global) → Add Credentials**
   - Kind: **Username with password**, ID: `dockerhub`, username = Docker Hub user, password = your access token.
3. Run **Build with Parameters** with `PUSH_IMAGE` ticked. Check Docker Hub for the new tag.
4. To deploy into your kind cluster, let Jenkins reach it:

   ```bash
   docker network connect kind jenkins
   kind get kubeconfig --name devops --internal > kubeconfig-jenkins.yaml
   ```

   In Jenkins add a credential of kind **Secret file**, ID `kubeconfig`, and upload `kubeconfig-jenkins.yaml`. Then build with `PUSH_IMAGE` and `DEPLOY_TO_K8S` ticked.
5. Check the rollout:

   ```bash
   kubectl get pods -n tasktracker
   kubectl describe deployment tasktracker -n tasktracker | grep Image
   ```

Do not commit `kubeconfig-jenkins.yaml` to Git. It holds cluster credentials.

### Checkpoint

You have a green pipeline, and you have seen a red one stop at the Test stage.

### Try it yourself

- Add a new stage called `Print Info` that runs `echo "Building commit" && git rev-parse --short HEAD`.
- Add a failing test, push, and see the stage fail.

---

## Module 8: Terraform (about 2 hours)

**Goal:** describe infrastructure in code, preview changes before making them, and destroy everything cleanly.

### Concepts

| Word | Meaning |
|---|---|
| **Provider** | A plugin that talks to a platform (Kubernetes, AWS, your local disk, ...) |
| **Resource** | A thing Terraform creates and manages |
| **Variable** | An input you can change |
| **Output** | A value Terraform prints at the end |
| **State** | Terraform's record of what it has created (`terraform.tfstate`) |
| `init` / `plan` / `apply` / `destroy` | Download plugins / preview / do it / remove it |

### Part A: Terraform basics with no cluster

```bash
cd terraform/01-basics
terraform init
terraform plan
terraform apply
```

Type `yes` when asked. Terraform creates a random name and a text file:

```bash
terraform output
cat output/hello-*.txt
```

Now change an input:

```bash
terraform apply -var="student_name=Moses"
cat output/hello-*.txt
```

Terraform updated the file only, and kept the same random name. Look at the plan output carefully: `+` create, `~` change, `-` destroy.

Remove everything:

```bash
terraform destroy
```

Read `main.tf` once more and match each block to the concepts above.

### Part B: Deploy to Kubernetes with Terraform

Make sure your kind cluster exists and has the image:

```bash
kind get clusters
kind load docker-image tasktracker:1.0.0 --name devops
```

If `kind get clusters` shows nothing, redo Module 5 steps 1 and 2.

```bash
cd ../02-kubernetes
terraform init
terraform plan
terraform apply
```

Terraform shows it will create 3 resources: a namespace, a Deployment, and a Service. Type `yes`.

```bash
kubectl get all -n tasktracker-tf
kubectl port-forward svc/tasktracker 8002:80 -n tasktracker-tf
```

In another terminal: `curl http://localhost:8002`. The greeting says "Hello from Terraform!".

### Change infrastructure through code

Stop the port-forward, then:

```bash
terraform apply -var="replicas=3" -var="greeting=Three pods now"
kubectl get pods -n tasktracker-tf
```

### Drift: when someone changes things by hand

```bash
kubectl scale deployment tasktracker --replicas=5 -n tasktracker-tf
terraform plan
```

The plan shows Terraform wants to change replicas back, because the code is the source of truth. Run `terraform apply` to fix the drift.

### Destroy

```bash
terraform destroy
cd ../..
```

### Checkpoint

You created, changed, and destroyed infrastructure from code, and saw drift detected.

### Try it yourself

- Open `variables.tf`, add a variable for the container memory limit, and use it in `main.tf`.
- Run `terraform fmt` (auto-formats your code) and `terraform validate` (checks it).
- Commit `.terraform.lock.hcl` to Git, but never `*.tfstate` (already in `.gitignore`, because state can contain secrets).

---

## Capstone challenge (optional, about 2 hours)

Put it all together:

1. Create a new branch `feature/capstone` in Git.
2. Add a new endpoint to `app/app.py` (for example `GET /about`) and a test for it in `test_app.py`.
3. Push the branch, then point Jenkins at it (`*/feature/capstone`) and get a green build.
4. Deploy the new image to your cluster, either with your Jenkins deploy stage or by hand with `kind load` and `kubectl set image`.
5. Run the traffic generator and add a Grafana panel for your new endpoint.
6. Merge the branch into `main` and tag `v1.1.0`.
7. Make Terraform use the new image tag through a `-var="image=tasktracker:1.1.0"`.

---

## Clean up everything

```bash
docker compose down                       # Module 4 stack (run in project root)
docker compose -f jenkins/docker-compose.yml down -v    # Jenkins (the -v also deletes its data)
kind delete cluster --name devops         # Kubernetes cluster and everything inside it
docker system prune -f                    # unused containers/images
```

---

## Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| `port is already allocated` | Another program uses that port. Stop it, or change the left number in `-p 8000:8000`. |
| `Cannot connect to the Docker daemon` | Docker Desktop is not running. Start it. |
| Pod shows `ImagePullBackOff` | Image is not inside the cluster. Run `kind load docker-image tasktracker:1.0.0 --name devops`. |
| Pod shows `CrashLoopBackOff` | Run `kubectl logs <pod> -n tasktracker` and read the error. |
| `kubectl` talks to the wrong cluster | Run `kubectl config use-context kind-devops`. |
| Grafana dashboard is empty | No traffic yet, or wrong time range. Run the traffic generator and choose "Last 15 minutes". |
| Prometheus target is DOWN (Compose) | The app container is not running. Run `docker compose ps`. |
| Jenkins: `docker: permission denied` | Jenkins must have `user: root` and the socket mounted, as in `jenkins/docker-compose.yml`. |
| Jenkins: `python3 -m venv` fails | The image was not built with `python3-venv`. Rebuild: `docker compose -f jenkins/docker-compose.yml up -d --build`. |
| `terraform apply` cannot connect | Your cluster is not running, or `kube_context` is wrong. Check `kubectl config get-contexts`. |
| Very slow everything | Not enough RAM. Use a single-node kind cluster and close other apps. |

---

## Glossary

- **CI/CD:** automatically testing (CI) and releasing (CD) every change.
- **Container:** a running, isolated copy of an image.
- **Image:** a packaged app template.
- **Manifest:** a YAML file describing Kubernetes resources.
- **Metric:** a number measured over time (requests, errors, latency).
- **PromQL:** Prometheus's query language.
- **Scrape:** Prometheus fetching `/metrics` from a target.
- **State (Terraform):** Terraform's record of what exists.
- **Idempotent:** running it twice gives the same result as running it once (`kubectl apply` and `terraform apply` work this way).

## Self-check questions

1. What is the difference between an image and a container?
2. Why does the Dockerfile copy `requirements.txt` before `app.py`?
3. What does a Kubernetes Deployment do that a plain `docker run` does not?
4. Why are the two Kubernetes probes different (readiness vs. liveness)?
5. What does Prometheus store, and what does Grafana store?
6. Why does Jenkins stop when tests fail, and why is that useful?
7. What is Terraform state, and why must it not go into Git?
8. What does `terraform plan` tell you that `apply` alone does not?

## Where to go next

- Replace in-memory tasks with a database container (PostgreSQL) and add it to Compose and Kubernetes.
- Add an **Ingress** so you can reach the app by a hostname instead of port-forward.
- Add **Alertmanager** so alerts send an email.
- Use **Helm** to install Prometheus and Grafana the way most teams do.
- Move Terraform to a real cloud (for example a managed Kubernetes service) once you are comfortable.
