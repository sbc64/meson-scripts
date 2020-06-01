from subprocess import run
from collections import defaultdict

from utils import readSSH

def writePrometheus(hostnamesWithips):
    head = """
global:
  scrape_interval: 5s
  scrape_timeout: 5s
  evaluation_interval: 5s
alerting:
  alertmanagers:
  - static_configs:
    - targets: []
    scheme: http
    timeout: 5s
scrape_configs:
"""
    template = """
- job_name: {host}
  metrics_path: /metrics
  scheme: http
  static_configs:
  - targets:
    - {ip}:{port}
"""
    print(hostnamesWithips)
    with open('prometheus-copy.yml', 'w+') as f:
        f.write(head)
        for h, ip in hostnamesWithips.items():
            f.write(template.format(host=h.strip(), ip=ip.strip(), port=6543))

def main():
    hosts = readSSH()
    del hosts["monitoring"]
    del hosts["auth"]
    writePrometheus(hosts)

    host = "monitoring:/root"
    scp = ["scp", "-F", "ssh_config"]
    args = scp + ["prometheus-copy.yml", host+"/prometheus.yml"]
    run(args)

    args = scp + ["grafana.yml", host]
    run(args)

    args = scp + ["monitor-compose.yml", host]
    run(args)

    args =  "ssh -F ssh_config monitoring 'docker stack deploy monitoring -c /root/monitor-compose.yml'"
    run(args, shell=True)

if __name__ == "__main__":
    main()
