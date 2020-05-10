#!/usr/bin/env python3
#   apt-tool.py - APT package manipulation tool
#   Copyright (c) 2018-2020 Lazaro Morales <moraleslazaro@gmail.com>
#
#   This script uses the Python binding for APT available at:
#   <https://pypi.org/project/python-apt/>
#
#   This programm is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#   more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this file.  If not, see <https://www.gnu.org/licenses/>.
#
#   How to use it:
#   ~~~~~~~~~~~~~~
#   On the source system:
#   $ apt-tool export
#
#   This will create a file named 'installed_pkgs.txt' that will be used on the
#   target system.
#
#   On the target system:
#   # apt-tool import installed_pkgs.txt   # Need root privileges
#
#   The latest version will be installed on the new system.
#
import sys
import os
import apt
import apt.progress
import apt_pkg
import apt.package

# TODO: Use 'argparse' to handle params. (See `pydoc argparse`)
if len(sys.argv) == 1:
    print("Usage: " + sys.argv[0] + " [export|import] [filename]")
    sys.exit(1)

# Save the installed packages from the source system
if sys.argv[1] == 'export' and len(sys.argv) <= 3:
    # First step will be get a list of the installed packages on the source
    # system to use them on the target system
    pkg_cache = apt.Cache()

    installed_pkgs = list()  # List containing the installed packages

    # Store all the installed packages
    for pkg in pkg_cache:
        if pkg.is_installed:
            # TODO: Review the versions lists to check if there are more
            # versions installed.
            print("Package '" + str(pkg.versions[0]) + "' is installed.")
            installed_pkgs.append(pkg)

    # Save them in a plain-text file
    if len(sys.argv) == 2:
        filename = "installed_pkgs.txt"
    else:
        filename = sys.argv[2]

    with open(filename, 'w') as file:
        for pkg in installed_pkgs:
            file.write(pkg.name + "\n")

    print("\nFile '" + filename + "' has been created.")
    sys.exit(0)
elif sys.argv[1] == 'import' and len(sys.argv) <= 3:
    # Check for privileges
    if os.getuid() != 0:
        print("You must be root to import packages.")
        exit(1)

    # Install/Upgrade all the save packages from the source system to the
    # target system
    pkg_cache = apt.Cache()

    # Read the packages from the text file and remove the trailing '\n'
    # character
    if len(sys.argv) == 2:
        filename = "installed_pkgs.txt"
    else:
        filename = sys.argv[2]

    try:
        with open(filename, 'r') as file:
            pkg_list = file.read().rstrip().split("\n")
    except FileNotFoundError:
        print("File '" + filename + "' not found.")
        exit(1)

    for i in pkg_list:
        pkg = pkg_cache.get(i)
        if not pkg:
            print("[WARNING] Package '" + i + "' not found.")
            # Log not found packages
            with open('missing_packages.txt', 'a') as file:
                file.write(i + "\n")
        else:
            # Mark package for installation if found
            try:
                pkg.mark_install()
                print("Marking '" + str(pkg.versions[0])
                      + "' for installation.")
            except apt_pkg.Error:
                # BUG: For some reason some packages are reported as broken to
                # APT but are actually installed at the end. Decided to catch
                # the exception and fail silently to continue with the process.
                print("[ERROR] Package '" + str(pkg.versions[0])
                      + "' showing as broken.")

                # Log the packages with issues
                # TODO: Investigate the package dependencies using
                # `apt.package.Version`
                with open("broken_packages.txt", "a") as file:
                    file.write(pkg.name + "\n")

    # Commit changes and display some info about the progress
    print("Committing changes to the package cache ...")
    pkg_cache.commit(apt.progress.text.AcquireProgress())
    exit(0)
else:
    print("Usage: " + sys.argv[0] + " [export|import] [filename]")
    sys.exit(1)
