let
  appName = "healthcheck";
  scale = "10";
  composeFile = pkgs.writeText "docker-compose.yml" ''
    version: "3"
    services:
      ${appName}:
        image: sebohe/wcstress:latest
        restart: always

      logspout:
        image: gliderlabs/logspout:v3
        command: 'udp://logstash:5000'
        links:
          - logstash
        volumes:
          - '/var/run/docker.sock:/tmp/docker.sock'
        depends_on:
          - elasticsearch
          - logstash
          - kibana

      logstash:
        image: logstash:2.1.1
        environment:
          - STDOUT=true
        links:
          - elasticsearch
        depends_on:
          - elasticsearch
          - kibana
        command: 'logstash -e "input { udp { port => 5000 } } output { elasticsearch { hosts => elasticsearch } }"'
      kibana:
        image: kibana:4.1.2
        links:
          - elasticsearch
        environment:
          - ELASTICSEARCH_URL=http://elasticsearch:9200
        ports:
          - '5601:5601'
        depends_on:
          - elasticsearch
      elasticsearch:
        image: elasticsearch:1.5.2
        ports:
          - '9200:9200'
          - '9300:9300'
  '';
in
{
  services.do-agent.enable = true;
  virtualisation.docker = {
     enable = true;
     liveRestore = false;
     enableOnBoot = true;
     autoPrune.enable = true;
  };
  systemd.services.stress_test = {
    description = "Stress test docker compose";
    wantedBy = [ "multi-user.target" ];
    after = [ "docker.service" ];
    requires = [ "docker.service" ];
    serviceConfig = {
      ExecStart = "${pkgs.docker-compose}/bin/docker-compose -f ${composeFile} up --scale ${appName}=${scale}";
      ExecStop= "${pkgs.docker-compose}/bin/docker-compose -f ${composeFile} down";
      Restart="always";
      Type="simple";
      #RemainAfterExit="yes";
    };
  };
}
