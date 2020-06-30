with import <nixpkgs> { };

let
  pythonPackages = python38Packages;
in pkgs.mkShell rec {
  name = "meson-scripts-env";
  venvDir = "./.venv";
  buildInputs = [
    pythonPackages.python
    pythonPackages.pip
    pythonPackages.venvShellHook
    openssl
    git
  ];

  # Now we can execute any commands within the virtual environment.
  # This is optional and can be left out to run pip manually.
  postShellHook = ''
    pip install -r requirements.txt
  '';

}
