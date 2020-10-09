with import <nixpkgs> {};
let
  appName = "healthcheck";
  # Recommended node size is 4 cpu and 8gb can handle
  # 100 nodes
  # The biggest limitation is cpu
  scale = "120";
  composeFile = pkgs.writeText "docker-compose.yml" ''
    version: "3"
    services:
      ${appName}:
        image: sebohe/wcstress:latest
        restart: always
        deploy:
          replicas: ${scale}
        environment:
          STRESS_TEST: "1"

      logspout:
        image: gliderlabs/logspout
        volumes:
          - /etc/hostname:/etc/host_hostname:ro
          - /var/run/docker.sock:/var/run/docker.sock
        command: syslog+tls://logs2.papertrailapp.com:41136
  '';
in
{
  environment.systemPackages = with pkgs; [
    htop
    vim
  ];

  services.do-agent.enable = true;
  virtualisation.docker = {
     enable = true;
     liveRestore = false;
     enableOnBoot = true;
     autoPrune.enable = true;
  };
  systemd.services.init-swarm = {
    description = "Init Docker swarm";
    wantedBy = [ "multi-user.target" ];
    after = [ "docker.service" ];
    requires = [ "docker.service" ];
    script = ''
      IP=$(${pkgs.curl}/bin/curl -s https://ident.me)
      ${pkgs.docker}/bin/docker swarm init --advertise-addr=$IP || true
    '';
    serviceConfig = {
      Type="oneshot";
    };
  };
  systemd.services.stress_test = {
    description = "Stress test docker compose";
    wantedBy = [ "multi-user.target" ];
    after = [ "init-swarm.service" ];
    requires = [ "docker.service" ];
    serviceConfig = {
      ExecStart = "${pkgs.docker}/bin/docker stack deploy -c ${composeFile} stress_test";
      Type="simple";
    };
  };
}
