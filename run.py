#!/bin/python3

import argparse
import os
import shutil
import subprocess as sp
from pathlib import Path

# Parsing options from command line
parser = argparse.ArgumentParser(
    description="Build OpenSIM gui and GUI",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--test", "-t", help="Test after building", action="store_true")
parser.add_argument(
    "--build-type",
    help="Build type for CMake",
    action="store",
    choices=["Release", "RelWithDebInfo", "Debug"],
    default="RelWithDebInfo",
)
parser.add_argument("--clean", "-c", help="Do a clean install", action="store_true")
parser.add_argument(
    "--java-home",
    help="JAVA_HOME to use for the build",
    action="store",
    default=Path("/usr/bin/java").resolve().parent.parent.parent,
)
parser.add_argument(
    "--cpu-cores",
    "-j",
    help="Number of CPU cores to use in the build",
    type=int,
    action="store",
    choices=list(range(1, os.cpu_count() + 1)),
    default=os.cpu_count(),
)

# Opensim-core build options
core_opts = parser.add_argument_group("Opensim core build options")
core_opts.add_argument(
    "--core-source",
    help="Folder to clone/update opensim-core",
    action="store",
    type=Path,
    default=Path.cwd() / "core_source",
)
core_opts.add_argument(
    "--core-build",
    help="Folder to build opensim-core",
    type=Path,
    action="store",
    default=Path.cwd() / "core_build",
)
core_opts.add_argument(
    "--core-install",
    help="Folder to install opensim-core",
    type=Path,
    action="store",
    default=Path.cwd() / "core_install",
)
core_opts.add_argument(
    "--dep-source", help="Dependencies source folder", action="store", type=Path,
)
core_opts.add_argument(
    "--dep-build", help="Dependencies build folder", action="store", type=Path,
)
core_opts.add_argument(
    "--dep-install", help="Dependencies install folder", action="store", type=Path,
)
core_opts.add_argument(
    "--core-repo",
    help="Git repository for opensim-core",
    action="store",
    default="https://github.com/opensim-org/opensim-core.git",
)

# Opensim-gui command line options

gui_opts = parser.add_argument_group("GUI build options")
gui_opts.add_argument(
    "--gui-repo",
    help="Git repository for opensim-gui",
    action="store",
    default="https://github.com/opensim-org/opensim-gui.git",
)
gui_opts.add_argument(
    "--gui-source",
    help="Folder to clone/update opensim-gui",
    action="store",
    type=Path,
    default=Path.cwd() / "gui_source",
)
gui_opts.add_argument(
    "--gui-build",
    help="Folder to build opensim-gui",
    type=Path,
    action="store",
    default=Path.cwd() / "gui_build",
)
gui_opts.add_argument(
    "--gui-install",
    help="Folder to install opensim-gui",
    type=Path,
    action="store",
    default=Path.cwd() / "gui_install",
)
gui_opts.add_argument(
    "--netbeans-folder",
    help="Netbeans install folder",
    type=Path,
    action="store",
    default=next(
        (i for i in Path.home().iterdir() if i.is_dir() and "netbeans-" in i.name), None
    ),
)


def add_to_bash(content):
    bashr = Path("~/.bashrc").expanduser().read_text().splitlines()
    if content not in bashr:
        with Path("~/.bashrc").expanduser().open("a") as b:
            b.write(content + "\n")


args = parser.parse_args()
args.dep_source = (
    args.core_source / "dependencies" if not args.dep_source else args.dep_source
)
args.dep_build = args.core_build / "dep_build" if not args.dep_build else args.dep_build
args.dep_install = (
    args.core_build / "dep_install" if not args.dep_install else args.dep_install
)

os.environ["JAVA_HOME"] = args.java_home.as_posix()
os.environ["OPENSIM_HOME"] = args.core_install.as_posix()
os.environ["LD_LIBRARY_PATH"] = (args.core_install / "lib").as_posix()
os.environ["LIBRARY_PATH"] = (args.core_install / "lib").as_posix()

add_to_bash(f"export JAVA_HOME={args.java_home}")
add_to_bash(f"export OPENSIM_HOME={args.core_install}")
add_to_bash(f"export LD_LIBRARY_PATH={args.core_install/'lib'}")
add_to_bash(f"export LIBRARY_PATH={args.core_install/'lib'}")


if args.core_source.exists():
    sp.run(["git", "pull"], cwd=args.core_source, check=True)
else:
    sp.run(["git", "clone", args.core_repo, args.core_source], check=True)

if args.clean:
    shutil.rmtree(args.dep_build) if args.dep_build.exists() else None
    shutil.rmtree(args.dep_install) if args.dep_install.exists() else None
    shutil.rmtree(args.core_build) if args.core_build.exists() else None
    shutil.rmtree(args.core_install) if args.core_install.exists() else None

args.dep_build.mkdir(exist_ok=True, parents=True)
sp.run(
    [
        "cmake",
        "-S",
        args.dep_source,
        "-B",
        args.dep_build,
        f"-DCMAKE_INSTALL_PREFIX:PATH='{args.dep_install}'",
        "-DSUPERBUILD_BTK:BOOL='1'",
        f"-DCMAKE_BUILD_TYPE='{args.build_type}'",
    ],
    check=True,
)
sp.run(["make", f"-j{args.cpu_cores}"], cwd=args.dep_build, check=True)

sp.run(
    [
        "cmake",
        "-S",
        args.core_source,
        "-B",
        args.core_build,
        # "-DWITH_BTK:BOOL='1'",
        f"-DCMAKE_BUILD_TYPE='{args.build_type}'",
        "-DBUILD_JAVA_WRAPPING:BOOL='1'",
        "-DOPENSIM_PYTHON_VERSION:STRING='3'",
        "-DBUILD_PYTHON_WRAPPING:BOOL='1'",
        f"-DCMAKE_INSTALL_PREFIX:PATH='{args.core_install}'",
        f"-DOPENSIM_DEPENDENCIES_DIR:PATH='{args.dep_install}'",
        "-DSWIG_EXECUTABLE:FILEPATH='/usr/bin/swig3.0'",
        "-DSWIG_DIR:PATH='/usr/share/swig3.0'",
    ],
    check=True,
)
sp.run(["make", f"-j{args.cpu_cores}"], cwd=args.core_build, check=True)
sp.run(["make", f"-j{args.cpu_cores}", "install"], cwd=args.core_build, check=True)

if args.test:
    if sp.run(["ctest", f"-j{args.cpu_cores}"], cwd=args.core_build).returncode:
        if input("Some tests seem to have failed. Continue? (Y/N) ").lower() == "n":
            exit(1)

# Build the GUI

if not args.gui_source.exists():
    sp.run(["git", "clone", args.gui_repo, args.gui_source], check=True)

# check 4.1.0 tag
sp.run(["git", "fetch", "--all", "--tags"], cwd=args.gui_source, check=True)
sp.run(["git", "checkout", "tags/4.1.0"], cwd=args.gui_source, check=True)
sp.run(
    [
        "git",
        "submodule",
        "update",
        "--init",
        "--recursive",
        "--",
        "opensim-models",
        "opensim-visualizer",
        "Gui/opensim/threejs",
    ],
    cwd=args.gui_source,
    check=True,
)

# if args.clean:
shutil.rmtree(args.gui_build) if args.gui_build.exists() else None
shutil.rmtree(args.gui_install) if args.gui_install.exists() else None


osim_cmake_folder = args.core_install / "lib/cmake/OpenSim"
ant_binary_path = args.netbeans_folder / "extide/ant/bin/ant"
harness_folder = args.netbeans_folder / "harness"
sp.run(
    [
        "cmake",
        "-S",
        args.gui_source,
        "-B",
        args.gui_build,
        f"-DAnt_EXECUTABLE:FILEPATH='{ant_binary_path}'",
        f"-DCMAKE_PREFIX_PATH='{args.core_install}'",
        f"-DCMAKE_BUILD_TYPE='{args.build_type}'",
        f"-DOpenSim_DIR:PATH='{osim_cmake_folder}'",
        f"-DANT_ARGS='-Dnbplatform.default.netbeans.dest.dir={args.netbeans_folder};-Dnbplatform.default.harness.dir={harness_folder}'",
    ],
    check=True,
)
sp.run(["make", "CopyOpenSimCore"], cwd=args.gui_build, check=True)
sp.run(["make", "CopyVisualizer"], cwd=args.gui_build, check=True)
sp.run(["make", "CopyModels"], cwd=args.gui_build, check=True)
# sp.run(["make", "PrepareInstaller"], cwd=args.gui_build, check=True)

# opensim_install_dest = args.gui_source / "Gui/opensim"
# sp.run(
#     [
#         ant_binary_path,
#         f"-Dnbplatform.default.netbeans.dest.dir='{args.netbeans_folder}'",
#         f"-Dnbplatform.default.harness.dir='{harness_folder}'",
#         "-f",
#         opensim_install_dest,
#         "run",
#     ],
#     check=True,
# )
# # make -j$(nproc)
# make -j$(nproc) install

print(f"{args}")
