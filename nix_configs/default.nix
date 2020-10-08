{pkgs, ...}:
let
  swarmMetricsPort = 9323;
  gwIP = "172.18.0";
  dockerBridgeIp = gwIP + ".0/16";
  dockerBridgeGateway = gwIP + ".1";
  dockerBridgeServiceName = "setup-docker-bridge-network";
in {

  imports = [
  ];

  networking = {
    firewall = {
      enable = true;
      allowedTCPPorts = [ 22 80 443 ];
    };
  };

  services = {
    do-agent.enable = true;
  };
  environment.systemPackages = with pkgs; [ 
    vim git neovim htop curl wget gnumake42 fd ripgrep starship
  ];
  users.defaultUserShell = pkgs.zsh;
  programs = {
    zsh = {
      ohMyZsh = {
        enable = true;
      };
      enable = true;
      enableCompletion = true;
      autosuggestions = {
        enable = true;
        highlightStyle = "fg=6";
        strategy = "match_prev_cmd";
      };
      interactiveShellInit = ''
        # z - jump around
        source ${pkgs.fetchurl {
          url = "https://raw.githubusercontent.com/rupa/z/6586b61384cff33d2c3ce6512c714e20ea59bfed/z.sh";
          sha256 = "b3969a36b35889a097cd5a38e5e9740762f0e45f994b5e45991e2a9bdb2b8079";
        }}
        source "${pkgs.fetchurl {
          name = "zshrc";
          url = "https://raw.githubusercontent.com/sebohe/dotfiles/71ec7adab84619418f08b95d5cdf69629efc8606/.zshrc";
          sha256 = "7eba8b9ad5e92181bd3f61fdd42c02304486ad37b8b5077db1499050968e4826";
        }}"
      '';
      promptInit = "";
    };
    tmux = {
      enable = true;
      extraConfig = builtins.readFile "${pkgs.fetchurl {
        name = "tmux.conf";
        url = "https://raw.githubusercontent.com/sebohe/dotfiles/master/.tmux.conf";
        sha256 = "6a1bba3ead2477f387a18bcae1049dbfd309d8ace064c73cfd4b6bf1efdc2a24";
      }}";
    };
  };
  # Docker swarm
  networking.firewall.interfaces = {
      "docker_gwbridge".allowedTCPPorts = [ swarmMetricsPort ];
  };
  virtualisation.docker = {
    enable = true;
    liveRestore = false;
    enableOnBoot = true;
    autoPrune.enable = true;
    extraOptions = ''--metrics-addr=172.17.0.1:${toString swarmMetricsPort} --experimental'';
  };

  systemd.services."${dockerBridgeServiceName}" = {
    description = "Sets the docker ";
    wantedBy = [ "multi-user.target" ];
    after = [ "docker.service" ];
    requires = [ "docker.service" ];
    script = ''
      docker network create \
        --subnet=${dockerBridgeIp} \
        --gateway ${dockerBridgeGateway} \
        -o com.docker.network.bridge.enable_icc=false \
        -o com.docker.network.bridge.name=docker_gwbridge \
        #-o com.docker.network.bridge.enable_ip_masquerade=true \
        docker_gwbridge
    '';
    serviceConfig.Type="oneshot";
  };

  systemd.services.init-swarm = {
    description = "Init Docker swarm";
    wantedBy = [ "multi-user.target" ];
    after = [ "docker.service" ];
    requires = [ "docker.service" "${dockerBridgeGateway}" ];
    script = ''
      IP=$(${pkgs.curl}/bin/curl -s https://ident.me)
      ${pkgs.docker}/bin/docker swarm init --advertise-addr=$IP || true
    '';
    serviceConfig.Type="oneshot";
  };
}
