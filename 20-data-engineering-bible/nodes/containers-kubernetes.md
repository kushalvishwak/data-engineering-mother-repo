---
id: containers-kubernetes
title: Containers and Kubernetes
tier: 2
priority: should-know
sources: [obenner/kubernetes, obenner/airflow, obenner/gcp, cookbook]
---

# Containers and Kubernetes

## Say it in one line
A container is a process with its own filesystem and dependencies but the host's kernel; Kubernetes is the scheduler that keeps a declared number of those containers running across a fleet of machines.

## Must be able to recite
- **Container vs VM** — A container shares the host kernel and ships only the application and its libraries (megabytes, starts in milliseconds); a VM ships a whole guest operating system on a hypervisor (gigabytes, starts in tens of seconds).
- **Image vs container** — The image is the immutable layered read-only template; the container is a running instance of it with a thin writable layer that is discarded when it stops.
- **Layers and build cache** — Each Dockerfile instruction produces a cached, shareable layer, so you put rarely-changing steps (install dependencies) before frequently-changing ones (copy source) or every build reinstalls everything.
- **Dockerfile essentials** — `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE`, and `ENTRYPOINT` for the command with `CMD` for its default arguments; a multi-stage build keeps compilers and build tools out of the shipped image.
- **Pod** — The smallest deployable unit: one or more containers sharing a network namespace, IP address and volumes, which is where sidecars and init containers live.
- **Init container** — Runs to completion before the app container starts, used to wait for a dependency, clone a repository or fetch configuration.
- **Deployment vs StatefulSet vs Job/CronJob vs DaemonSet** — Deployment for stateless replicas with rolling updates, StatefulSet for stable identity and per-pod storage, Job and CronJob for batch runs, DaemonSet for one pod per node such as a log or metrics agent.
- **Service** — A stable virtual IP and DNS name that load-balances to whichever pods match a label selector; ClusterIP is internal only, NodePort opens a port on every node, LoadBalancer asks the cloud for an external L4 balancer.
- **Ingress** — L7 HTTP routing by host and path with TLS terminated from a secret, implemented by an ingress controller pod, with a default backend for requests that match no rule.
- **ConfigMap vs Secret** — Both inject key-values as environment variables or mounted files; a Secret is only base64-encoded, so real protection needs encryption at rest, RBAC and preferably an external secret manager.
- **Requests vs limits** — The request is what the scheduler reserves and is what guarantees placement; the limit is the ceiling, where exceeding CPU throttles the container and exceeding memory gets it OOM-killed.
- **HPA vs Cluster Autoscaler** — The Horizontal Pod Autoscaler changes the replica count to hold a target metric; the Cluster Autoscaler adds nodes when pods cannot be scheduled — pod scaling and node scaling are two separate mechanisms.
- **Control plane vs node components** — api-server (the single entry point), scheduler, controller-manager and etcd on the control plane; kubelet, kube-proxy and a container runtime on every node.
- **Namespaces, RBAC and PodDisruptionBudget** — Namespaces partition one cluster between teams and environments, RBAC narrows permissions to the minimum, and a PDB stops a node drain from taking replicas below `minAvailable`.
- **Why data teams meet Kubernetes** — Airflow runs on it (KubernetesExecutor and KubernetesPodOperator give each task its own right-sized, dependency-isolated pod), Spark can use it as its cluster manager instead of YARN, and dbt, quality checks and API services all ship as images.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a container, and how does it differ from a virtual machine? — A container is an isolated process using the host kernel with its own filesystem, network and resource limits via namespaces and cgroups; a VM virtualises hardware and runs a full guest OS, so it is far larger and slower to start but isolates at the kernel boundary.
- ★ How do you control the resource usage of a pod? — With requests and limits per container: the request is what the scheduler reserves, and a container exceeding its CPU request is throttled while one exceeding its memory limit is terminated.
- What Kubernetes services run on the nodes, and what does each do? — kubelet applies the pod spec on that node and reports status, kube-proxy programmes the networking rules that make Services reachable, and the container runtime actually runs the containers; on the control plane the api-server is the entry point, the scheduler places pods, and the controller-manager reconciles actual state towards desired state.
- ★ How do you expose a service outside the cluster? — Set the Service `type` to NodePort (a port on every node) or LoadBalancer (a cloud L4 balancer), or put an Ingress with an ingress controller in front for L7 host/path routing; `kubectl port-forward` or `kubectl proxy` is for debugging only.
- ★ What is the difference between an Ingress and a LoadBalancer Service? — A LoadBalancer Service is layer 4 and gives one external IP per service; an Ingress is layer 7, terminates TLS and routes many hostnames and paths through a single entry point, and it needs an ingress controller running in the cluster to do anything.
- How do you reference a secret in a pod spec, and how safe is it? — With `valueFrom.secretKeyRef` (or a mounted volume) so the value lands in an environment variable or file; Secrets are only base64-encoded in etcd, so you enable encryption at rest, restrict RBAC, and prefer an external secret store for production credentials.
- How would you troubleshoot a pod that is not being scheduled? — `kubectl describe pod` and cluster events; the usual causes are insufficient CPU or memory on any node, an unsatisfiable node selector, affinity or taint, a missing PersistentVolumeClaim, or an image pull failure.
- How do you run a pod on a particular node? — `nodeName` pins it outright, `nodeSelector` matches a node label, and node affinity expresses hard (`requiredDuringScheduling...`) or soft (`preferredDuringScheduling...`) rules; taints and tolerations do the inverse by keeping pods off nodes.
- How do you perform maintenance on a Kubernetes node? — `kubectl cordon` marks it unschedulable, then `kubectl drain --ignore-daemonsets` evicts the pods so they are rescheduled elsewhere; after the patch you `kubectl uncordon` to bring it back.
- What is a Pod Disruption Budget? — A policy declaring the minimum number (or maximum unavailable fraction) of pods that must stay up, so a voluntary disruption like a drain blocks rather than dropping a quorum-based service below `minAvailable`.
- What is an init container and when would you use it? — A container that must finish successfully before the application container starts, used to wait for a dependency to become reachable, clone a repository into a shared volume, or run a schema migration.
- ★ Why use namespaces rather than the default namespace? — They group applications, give each team or environment its own scope for names, quotas and RBAC, and stop two teams silently overwriting each other's resources with the same object name.
- How do you increase the security of a Kubernetes cluster? — Network policies to stop every pod talking to every other pod, RBAC scoped to the minimum, namespaces as boundaries, admission policies that forbid privileged containers, audit logging on, and images scanned and pulled from a trusted registry.
- ★ How do you monitor a Kubernetes cluster and collect logs centrally? — Prometheus scrapes and stores metrics with exporters and Alertmanager on top; logs are shipped by a node-level agent as a DaemonSet or a sidecar (Fluent Bit, Filebeat) into Elasticsearch/OpenSearch or a cloud logging service.
- ★ What is the role of load balancing in Kubernetes? — Internally, a Service spreads requests across the healthy pods behind its label selector; externally, a cloud or ingress load balancer accepts traffic on one address and routes it in, removing pods that fail their health checks.
- What is the difference between Docker Swarm and Kubernetes? — Swarm is simpler to install and operate but limited; Kubernetes is harder to set up and far more capable, with pod autoscaling, richer scheduling and a large ecosystem, which is why it is what you meet in production.
- What are the pros and cons of the Airflow KubernetesExecutor? — Every task runs in its own pod with its own image and CPU/memory request, so dependencies are isolated and resources are right-sized per task; the costs are pod startup latency, a more complex setup and needing to understand Kubernetes to debug a failure.
- ★ What is GKE, and what is Cloud Run? — GKE is Google's managed Kubernetes for orchestrating containers; Cloud Run runs the same container images serverlessly with no cluster to manage, which is the better fit for a stateless API or a small transformation step.
- ★ What is an Operator and why is it needed? — A controller plus custom resources that encodes how to install, upgrade, back up and repair a specific application; stateless replicas are easy to reconcile, but stateful systems such as Kafka or Postgres need application-specific logic that would otherwise be a human runbook.
- What do image layers mean for a Dockerfile, and why does instruction order matter? — Each instruction is a cached layer, so ordering dependency installation before source copy means a code change rebuilds only the last layers, and a multi-stage build keeps the toolchain out of the final image (not in sources, but standard).
- How do you run Spark on Kubernetes? — Kubernetes acts as the cluster manager instead of YARN: the driver runs in a pod and requests executor pods, dynamic allocation adds and removes them, and the shuffle and event logs go to object storage (not in sources, but standard).
- How do you configure TLS on an Ingress? — Add a `tls` block listing the hosts and referencing a Secret holding the certificate and key, and the ingress controller terminates HTTPS for those hosts.
- What is the Ingress default backend? — Where requests that match no rule are sent, so users get a sensible response instead of an unexplained error.
- How do you run Kubernetes locally? — Minikube, kind or Docker Desktop run a single-node cluster on your laptop, which is enough to learn the objects and test manifests.
- What is the easiest way to learn Kubernetes quickly? — Run a local single-node cluster and deploy one real workload end to end (Deployment, Service, ConfigMap, Secret, Ingress), because the object model only makes sense once you have watched it reconcile.

## Traps
- Calling a container "a lightweight VM": say shared kernel with namespace and cgroup isolation, because the immediate follow-up is always what the difference from a VM actually is.
- Treating Secrets as encrypted: base64 is encoding, not encryption, so assume anyone who can read the namespace can read the credential.
- Running Spark or Airflow pods with no requests or limits: they get scheduled anywhere and then either get OOM-killed or starve their neighbours, and this is the most common real failure a data team hits on Kubernetes.
- Confusing the HPA with the Cluster Autoscaler: one changes the number of pods, the other the number of nodes, and a burst usually needs both.
- Assuming pods have stable IPs or can be restarted in place: pods are disposable and get new addresses, which is exactly why Services and StatefulSets exist.
- Volunteering deep Kubernetes internals in a data-engineer interview: two sentences on why Airflow and Spark run there is the expected depth, and going further without being asked spends time you need for SQL and modelling.

## Graph
- **Needs first:** [[cloud-fundamentals]], [[linux-shell]]
- **Leads to:** [[orchestration-airflow]]
- **Asked together with:** [[observability]]
