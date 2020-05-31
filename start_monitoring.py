from subprocess import run
from collections import defaultdict

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


def readSSH():
    host = defaultdict(str)
    temp=[]
    with open('ssh_config', 'r') as f:
        for line in f:
            if "Host" in line:
                temp.append(line)

    for index in range(0, len(temp), 2):
        host[temp[index].split(' ')[-1]] =  temp[index+1].split(' ')[-1]

    return host 

def main():
    writePrometheus(readSSH())

    host = "monitoring:/root"
    scp = ["scp", "-F", "ssh_config"]
    args = scp + ["prometheus-copy.yml", host+"/prometheus.yml"]
    run(args)

    args = scp + ["grafana.yml", host]
    run(args)

    args = scp + ["monitor-compose.yml", host]
    run(args)

    args =  ["ssh", "-F", "ssh_config", "monitoring", "'docker stack deploy monitoring -c /root/monitor-compose.yml'"]
    run(args)

if __name__ == "__main__":
    main()
