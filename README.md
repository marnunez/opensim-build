# opensim-build
Building OpenSIM from source in Linux

This python script tries to simplify OpenSIM-GUI and OpenSIM-core building on a Linux machine.

Usage:
```bash
usage: run.py [-h] [--test] [--build-type {Release,RelWithDebInfo,Debug}]
              [--clean] [--java-home JAVA_HOME]
              [--cpu-cores]
              [--core-source CORE_SOURCE] [--core-build CORE_BUILD]
              [--core-install CORE_INSTALL] [--dep-source DEP_SOURCE]
              [--dep-build DEP_BUILD] [--dep-install DEP_INSTALL]
              [--core-repo CORE_REPO] [--gui-repo GUI_REPO]
              [--gui-source GUI_SOURCE] [--gui-build GUI_BUILD]
              [--gui-install GUI_INSTALL] [--netbeans-folder NETBEANS_FOLDER]

Build OpenSIM gui and GUI

optional arguments:
  -h, --help            show this help message and exit
  --test, -t            Test after building (default: False)
  --build-type {Release,RelWithDebInfo,Debug}
                        Build type for CMake (default: RelWithDebInfo)
  --clean, -c           Do a clean install (default: False)
  --java-home JAVA_HOME
                        JAVA_HOME to use for the build (default: $JAVA_HOME)
  --cpu-cores {nCores}, -j {nCores}
                        Number of CPU cores to use in the build (default: all cores)

Opensim core build options:
  --core-source CORE_SOURCE
                        Folder to clone/update opensim-core (default:
                        $CWD/core_source)
  --core-build CORE_BUILD
                        Folder to build opensim-core (default:
                        $CWD/core_build)
  --core-install CORE_INSTALL
                        Folder to install opensim-core (default:
                        $CWD/core_install)
  --dep-source DEP_SOURCE
                        Dependencies source folder (default: None)
  --dep-build DEP_BUILD
                        Dependencies build folder (default: None)
  --dep-install DEP_INSTALL
                        Dependencies install folder (default: None)
  --core-repo CORE_REPO
                        Git repository for opensim-core (default:
                        https://github.com/opensim-org/opensim-core.git)

GUI build options:
  --gui-repo GUI_REPO   Git repository for opensim-gui (default:
                        https://github.com/opensim-org/opensim-gui.git)
  --gui-source GUI_SOURCE
                        Folder to clone/update opensim-gui (default:
                        $CWD/gui_source)
  --gui-build GUI_BUILD
                        Folder to build opensim-gui (default:
                        $CWD/gui_build)
  --gui-install GUI_INSTALL
                        Folder to install opensim-gui (default:
                        $CWD/gui_install)
  --netbeans-folder NETBEANS_FOLDER
                        Netbeans install folder (default: None)
```

## What it does
The script clones/pulls the dafault core and gui repo's master branch, configs and builds them with CMake, picks reasonable choices for Netbeans and Java locations, creates all the diferent project folders as needed, using the current directory as root. For the GUI, it runs CMake and the Netbean's ANT to run the project.

Tested in a Debian unstable x64, Netbeans 8.2, openjdk 8, SWIG 3.2

## What it doesn't (yet)
- Install all linux dependencies. They're there. I've built it :) python-dev, numpy, swig 3.0 etc. I'll add them eventually
- Moves all Resources files (Models, Geometries, etc) to the installation folder.
