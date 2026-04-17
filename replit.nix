{pkgs}: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
  ];
  env = {
    PYTHONUNBUFFERED = "1";
    PYTHONPATH = "/home/runner/${builtins.baseNameOf ./.}";
  };
}
