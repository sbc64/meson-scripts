with import <nixpkgs> { };

stdenv.mkDerivation {
  name = "python";
  buildInputs = [
    python38
    python37Packages.digital-ocean
  ];
}
