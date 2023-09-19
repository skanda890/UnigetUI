"""

wingetui/PackageManagers/sampleHelper.py

This file holds a sample package manager implementation. The code here must be reimplemented before being used

"""

import os
import subprocess

from PySide6.QtCore import *
from tools import *
from tools import _

from .PackageClasses import *


class DotNetToolPackageManager(DynamicPackageManager):

    EXECUTABLE = "dotnet.exe"
    NAME = ".Net Tool"
    CACHE_FILE = os.path.join(os.path.expanduser("~"), f".wingetui/cacheddata/{NAME}CachedPackages")
    CAHCE_FILE_PATH = os.path.join(os.path.expanduser("~"), ".wingetui/cacheddata")

    BLACKLISTED_PACKAGE_NAMES = []
    BLACKLISTED_PACKAGE_IDS = []
    BLACKLISTED_PACKAGE_VERSIONS = []

    Capabilities = PackageManagerCapabilities()
    Capabilities.CanRunAsAdmin = True
    Capabilities.CanSkipIntegrityChecks = True
    Capabilities.CanRunInteractively = False
    Capabilities.CanRemoveDataOnUninstall = False
    Capabilities.SupportsCustomVersions = True
    Capabilities.SupportsCustomArchitectures = False
    Capabilities.SupportsCustomScopes = False

    LoadedIcons = False

    if not os.path.exists(CAHCE_FILE_PATH):
        try:
            os.makedirs(CAHCE_FILE_PATH)
        except FileExistsError:
            pass

    def isEnabled(self) -> bool:
        return not getSettings(f"Disable{self.NAME}")

    def getPackagesForQuery(self, query: str) -> list[Package]:
        f"""
        Will retieve the packages for the given "query: str" from the package manager {self.NAME} in the format of a list[Package] object.
        """
        print(f"🔵 Starting {self.NAME} query search")
        try:
            p = subprocess.Popen([self.EXECUTABLE, "tool", "search", query], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
            packages: list[Package] = []
            dashesPassed = False
            while p.poll() is None:
                line: str = str(p.stdout.readline().strip(), "utf-8", errors="ignore")
                if line:
                    if not dashesPassed:
                        if "---" in line:
                            dashesPassed = True
                    else:
                        if len(line.split(" ")) >= 2:
                            package = list(filter(None, line.split(" ")))
                            name = formatPackageIdAsName(package[0])
                            id = package[0]
                            version = package[1]
                            source = self.NAME
                            if name not in self.BLACKLISTED_PACKAGE_NAMES and id not in self.BLACKLISTED_PACKAGE_IDS and version not in self.BLACKLISTED_PACKAGE_VERSIONS:
                                packages.append(Package(name, id, version, source, Dotnet))
                        else:
                            continue

            print(f"🟢 {self.NAME} package query finished successfully")
            return packages
        except Exception as e:
            report(e)
            return []

    def getAvailableUpdates(self) -> list[UpgradablePackage]:
        f"""
        Will retieve the upgradable packages by {self.NAME} in the format of a list[UpgradablePackage] object.
        """
        print(f"🔵 Starting {self.NAME} search for updates")
        try:
            if shutil.which("dotnet-tools-outdated") is None:
                print("🟡 Installing dotnet-tools-outdated, that was missing...")
                Command = [self.EXECUTABLE, "tool", "install", "-g", "dotnet-tools-outdated"] + self.getParameters(InstallationOptions())
                p = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, cwd=GSUDO_EXE_LOCATION, env=os.environ)
                p.wait()
                print(p.stdout.readlines())

            rawoutput: str = "\n--------dotnet\n\n"
            packages: list[UpgradablePackage] = []
            p = subprocess.Popen(["dotnet-tools-outdated"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ.copy(), shell=True)
            dashesPassed = False
            while p.poll() is None:
                line: str = str(p.stdout.readline().strip(), "utf-8", errors="ignore")
                if line:
                    print(line)
                    rawoutput += line + "\n"
                    if not dashesPassed:
                        if "---" in line:
                            dashesPassed = True
                    else:
                        if len(line.split(" ")) >= 3:
                            package = list(filter(None, line.split(" ")))
                            name = formatPackageIdAsName(package[0])
                            id = package[0]
                            version = package[1]
                            newVersion = package[2]
                            source = self.NAME
                            if name not in self.BLACKLISTED_PACKAGE_NAMES and id not in self.BLACKLISTED_PACKAGE_IDS and version not in self.BLACKLISTED_PACKAGE_VERSIONS:
                                packages.append(UpgradablePackage(name, id, version, newVersion, source, Dotnet))

            print(f"🟢 {self.NAME} search for updates finished with {len(packages)} result(s)")
            globals.PackageManagerOutput += rawoutput
            return packages
        except Exception as e:
            report(e)
            return []

    def getInstalledPackages(self) -> list[Package]:
        f"""
        Will retieve the intalled packages by {self.NAME} in the format of a list[Package] object.
        """
        print(f"🔵 Starting {self.NAME} search for installed packages")
        try:
            rawoutput = "\n\n-------dotnet\n"
            packages: list[Package] = []
            p = subprocess.Popen([self.EXECUTABLE, "tool", "list"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
            dashesPassed = False
            while p.poll() is None:
                line: str = str(p.stdout.readline().strip(), "utf-8", errors="ignore")
                if line:
                    print(line)
                    rawoutput += line + "\n"
                    if not dashesPassed:
                        if "---" in line:
                            dashesPassed = True
                    else:
                        if len(line.split(" ")) >= 2:
                            package = list(filter(None, line.split(" ")))
                            name = formatPackageIdAsName(package[0])
                            id = package[0]
                            version = package[1]
                            source = self.NAME
                            if name not in self.BLACKLISTED_PACKAGE_NAMES and id not in self.BLACKLISTED_PACKAGE_IDS and version not in self.BLACKLISTED_PACKAGE_VERSIONS:
                                packages.append(Package(name, id, version, source, Dotnet))
            p = subprocess.Popen([self.EXECUTABLE, "tool", "list", "--global"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, env=os.environ.copy())
            dashesPassed = False
            while p.poll() is None:
                line: str = str(p.stdout.readline().strip(), "utf-8", errors="ignore")
                if line:
                    print(line)
                    rawoutput += line + "\n"
                    if not dashesPassed:
                        if "---" in line:
                            dashesPassed = True
                    else:
                        if len(line.split(" ")) >= 2:
                            package = list(filter(None, line.split(" ")))
                            name = formatPackageIdAsName(package[0])
                            id = package[0]
                            version = package[1]
                            source = self.NAME + " (Global)"
                            if name not in self.BLACKLISTED_PACKAGE_NAMES and id not in self.BLACKLISTED_PACKAGE_IDS and version not in self.BLACKLISTED_PACKAGE_VERSIONS:
                                packages.append(Package(name, id, version, source, Dotnet))
            print(f"🟢 {self.NAME} search for installed packages finished with {len(packages)} result(s)")
            globals.PackageManagerOutput += rawoutput + "\n\n"
            return packages
        except Exception as e:
            report(e)
            return []

    def getPackageDetails(self, package: Package) -> PackageDetails:
        """
        Will return a PackageDetails object containing the information of the given Package object
        """
        print(f"🔵 Starting get info for {package.Name} on {self.NAME}")
        details = PackageDetails(package)
        try:

            # The code that loads the package details goes here

            print(f"🟢 Get info finished for {package.Name} on {self.NAME}")
            return details
        except Exception as e:
            report(e)
            return details

    def getIcon(self, source: str = "") -> QIcon:
        if not self.LoadedIcons:
            self.LoadedIcons = True
            self.Icon = QIcon(getMedia("dotnet"))
        return self.Icon

    def getParameters(self, options: InstallationOptions) -> list[str]:
        Parameters: list[str] = []
        if options.Architecture:
            Parameters += ["-a", options.Architecture]
        if options.CustomParameters:
            Parameters += options.CustomParameters
        if options.InstallationScope:
            Parameters += ["-s", options.InstallationScope]
        if options.InteractiveInstallation:
            Parameters.append("--interactive")
        if options.RemoveDataOnUninstall:
            Parameters.append("--remove-user-data")
        if options.SkipHashCheck:
            Parameters += ["--skip-integrity-checks", "--force"]
        if options.Version:
            Parameters += ["--version", options.Version]
        return Parameters

    def startInstallation(self, package: Package, options: InstallationOptions, widget: InstallationWidgetType) -> subprocess.Popen:
        print("🔴 This function should be reimplented!")
        Command: list[str] = [self.EXECUTABLE, "install", package.Name] + self.getParameters(options)
        if options.RunAsAdministrator:
            Command = [GSUDO_EXECUTABLE] + Command
        print(f"🔵 Starting {package} installation with Command", Command)
        p = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, cwd=GSUDO_EXE_LOCATION, env=os.environ)
        Thread(target=self.installationThread, args=(p, options, widget,), name=f"{self.NAME} installation thread: installing {package.Name}").start()
        return p

    def startUpdate(self, package: Package, options: InstallationOptions, widget: InstallationWidgetType) -> subprocess.Popen:
        print("🔴 This function should be reimplented!")
        Command: list[str] = [self.EXECUTABLE, "install", package.Name] + self.getParameters(options)
        if options.RunAsAdministrator:
            Command = [GSUDO_EXECUTABLE] + Command
        print(f"🔵 Starting {package} update with Command", Command)
        p = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, cwd=GSUDO_EXE_LOCATION, env=os.environ)
        Thread(target=self.installationThread, args=(p, options, widget,), name=f"{self.NAME} installation thread: updating {package.Name}").start()
        return p

    def installationThread(self, p: subprocess.Popen, options: InstallationOptions, widget: InstallationWidgetType):
        output = ""
        while p.poll() is None:
            line = str(getLineFromStdout(p), encoding='utf-8', errors="ignore").strip()
            if line:
                output += line + "\n"
                widget.addInfoLine.emit(line)
                if "downloading" in line:
                    widget.counterSignal.emit(3)
                elif "installing" in line:
                    widget.counterSignal.emit(7)
        print(p.returncode)
        widget.finishInstallation.emit(p.returncode, output)

    def startUninstallation(self, package: Package, options: InstallationOptions, widget: InstallationWidgetType) -> subprocess.Popen:
        print("🔴 This function should be reimplented!")
        Command: list[str] = [self.EXECUTABLE, "install", package.Name] + self.getParameters(options)
        if options.RunAsAdministrator:
            Command = [GSUDO_EXECUTABLE] + Command
        print(f"🔵 Starting {package} update with Command", Command)
        p = subprocess.Popen(Command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True, cwd=GSUDO_EXE_LOCATION, env=os.environ)
        Thread(target=self.uninstallationThread, args=(p, options, widget,), name=f"{self.NAME} installation thread: updating {package.Name}").start()
        return p

    def uninstallationThread(self, p: subprocess.Popen, options: InstallationOptions, widget: InstallationWidgetType):
        output = ""
        while p.poll() is None:
            line = str(getLineFromStdout(p), encoding='utf-8', errors="ignore").strip()
            if line:
                output += line + "\n"
                widget.addInfoLine.emit(line)
                if "removing" in line:
                    widget.counterSignal.emit(5)
        print(p.returncode)
        widget.finishInstallation.emit(p.returncode, output)

    def detectManager(self, signal: Signal = None) -> None:
        o = subprocess.run(f"{self.EXECUTABLE}  --version", shell=True, stdout=subprocess.PIPE)
        globals.componentStatus[f"{self.NAME}Found"] = o.returncode == 0
        globals.componentStatus[f"{self.NAME}Version"] = o.stdout.decode('utf-8').replace("\n", "")
        if signal:
            signal.emit()

    def updateSources(self, signal: Signal = None) -> None:
        pass  # This package manager does not need source refreshing
        if signal:
            signal.emit()


Dotnet = DotNetToolPackageManager()


if __name__ == "__main__":
    import __init__
