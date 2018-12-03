# apt-tool
APT Package Manipulation Tool

Export a list of the installed packages in a Ubuntu/Debian system and
import it on a new version of the system. The result will be have
installed the latest version of the packages available on the new
version of the operating system's repository.

## How to use it

On the source system:

`$ apt-tool export`

> This will create a file named 'installed_packages.txt' that will be
> used on the target system.

On the target system:

`# apt-tool import installed_pkgs.txt # Need root privileges`

The latest version of the packages will be installed on the new system.
