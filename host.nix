{ config, pkgs, ... }:
{
  virtualisation.docker = {
    enable = true;
    liveRestore = false;
    enableOnBoot = true;
    autoPrune.enable = true;
    extraOptions = ''--metrics-addr=172.18.0.1:9323 --experimental'';
  };

  environment.systemPackages = with pkgs; [
    git
    neovim
    vim
    tmux
    starship
  ];
  programs = {
    zsh = {
      enable = true;
      enableCompletion = true;
      interactiveShellInit = ''
        # z - jump around
        source ${pkgs.fetchurl {
          url = "https://raw.githubusercontent.com/rupa/z/6586b61384cff33d2c3ce6512c714e20ea59bfed/z.sh";
          sha256 = "b3969a36b35889a097cd5a38e5e9740762f0e45f994b5e45991e2a9bdb2b8079";
        }}
        touch /root/.zshrc
        export ZSH=${pkgs.oh-my-zsh}/share/oh-my-zsh
        if [[ "$TMUX" == "" ]]; then
          WHOAMI=$(whoami)
          if tmux has-session -t $WHOAMI 2>/dev/null; then
            tmux -2 attach-session -t $WHOAMI
          else
              tmux -2 new-session -s $WHOAMI
          fi
        fi
      '';
      promptInit = "";
    };
  };
  users = {
    defaultUserShell = pkgs.zsh;
  };
}
