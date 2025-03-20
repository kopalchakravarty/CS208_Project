# CS208_Project
## Proactive Kubernetes Autoscaler

### Set Up Environment

### 1. Install Prometheus Stack
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install -n monitoring --set grafana.enabled=false --set nodeExporter.enabled=false prometheus prometheus-community/kube-prometheus-stack --create-namespace
```

### 2. Install Keda

```bash
# Enable the service monitor to ensure metrics are exposed

helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --create-namespace --namespace keda --set prometheus.operator.enabled=true --set prometheus.metricServer.enabled=true --set prometheus.operator.serviceMonitor.enabled=true --set prometheus.metricServer.serviceMonitor.enabled=true
```

### 3. Install Grafana
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana --namespace monitoring
```

### 4. Install Postgres

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgresql-dev oci://registry-1.docker.io/bitnamicharts/postgresql
```
### 5. Nginx Ingress
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

## Verify a load balancer service created and public IP is assigned to the service
kubectl get svc -n ingress-nginx
```

### Add data to Postgres DB

```bash
# Exec into the container, enter the DB password when prompted.
# The password is set up at the time of installation
kubectl exec -it postgresql-dev-0 -- psql -U postgres -d postgres
```

```sql
-- Create Table to store the timeseries data
CREATE TABLE timeseries_forecast (
  timestamp TIMESTAMP PRIMARY KEY,
  replicas DECIMAL
);
\copy timeseries_forecast FROM '/tmp/prediction_with_periodic.csv' WITH (FORMAT csv, HEADER true);
```

### Deploy Manifest Files

Deploy the manifest files to set up application/ingress/auth as necessary

### Configure Data Sources and Dashboards - Grafana
Compare Scaling Trends by visualizing Keda scaling and predicted scaling metrics
<img width="1278" alt="image" src="https://github.com/user-attachments/assets/6d686c9e-5fc4-445f-b625-f3ee5acff79f" />
<img width="1285" alt="image" src="https://github.com/user-attachments/assets/d06947d7-ce62-4bac-9ae7-36a122ad3316" />
<img width="1284" alt="image" src="https://github.com/user-attachments/assets/08d2cd28-d969-496d-8ec5-e752f0e8f9ff" />


### Monitor Application Scaling
```bash
kubectl get po -n default -l app=traffic-app
```

