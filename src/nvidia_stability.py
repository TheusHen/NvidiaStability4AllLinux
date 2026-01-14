#!/usr/bin/env python3

import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Optional, Dict, Tuple, List


GPU_POWER_LIMITS = {
    "RTX 4090": {"tdp": 450, "mem_clock": 1313, "graphics_clock": 2520},
    "RTX 4080 SUPER": {"tdp": 320, "mem_clock": 1438, "graphics_clock": 2550},
    "RTX 4080": {"tdp": 320, "mem_clock": 1400, "graphics_clock": 2505},
    "RTX 4070 Ti SUPER": {"tdp": 285, "mem_clock": 1313, "graphics_clock": 2610},
    "RTX 4070 Ti": {"tdp": 285, "mem_clock": 1313, "graphics_clock": 2610},
    "RTX 4070 SUPER": {"tdp": 220, "mem_clock": 1313, "graphics_clock": 2475},
    "RTX 4070": {"tdp": 200, "mem_clock": 1313, "graphics_clock": 2475},
    "RTX 4060 Ti": {"tdp": 160, "mem_clock": 1125, "graphics_clock": 2535},
    "RTX 4060": {"tdp": 115, "mem_clock": 1125, "graphics_clock": 2460},
    "RTX 3090 Ti": {"tdp": 450, "mem_clock": 1313, "graphics_clock": 1860},
    "RTX 3090": {"tdp": 350, "mem_clock": 1219, "graphics_clock": 1695},
    "RTX 3080 Ti": {"tdp": 350, "mem_clock": 1188, "graphics_clock": 1665},
    "RTX 3080": {"tdp": 320, "mem_clock": 1188, "graphics_clock": 1710},
    "RTX 3070 Ti": {"tdp": 290, "mem_clock": 1188, "graphics_clock": 1770},
    "RTX 3070": {"tdp": 220, "mem_clock": 1188, "graphics_clock": 1725},
    "RTX 3060 Ti": {"tdp": 200, "mem_clock": 1188, "graphics_clock": 1670},
    "RTX 3060": {"tdp": 170, "mem_clock": 1875, "graphics_clock": 1777},
    "RTX 3050": {"tdp": 130, "mem_clock": 1750, "graphics_clock": 1777},
    "RTX 2080 Ti": {"tdp": 250, "mem_clock": 1750, "graphics_clock": 1545},
    "RTX 2080 SUPER": {"tdp": 250, "mem_clock": 1937, "graphics_clock": 1815},
    "RTX 2080": {"tdp": 215, "mem_clock": 1750, "graphics_clock": 1710},
    "RTX 2070 SUPER": {"tdp": 215, "mem_clock": 1750, "graphics_clock": 1770},
    "RTX 2070": {"tdp": 175, "mem_clock": 1750, "graphics_clock": 1620},
    "RTX 2060 SUPER": {"tdp": 175, "mem_clock": 1750, "graphics_clock": 1650},
    "RTX 2060": {"tdp": 160, "mem_clock": 1750, "graphics_clock": 1680},
    "GTX 1080 Ti": {"tdp": 250, "mem_clock": 1376, "graphics_clock": 1582},
    "GTX 1080": {"tdp": 180, "mem_clock": 1251, "graphics_clock": 1733},
    "GTX 1070 Ti": {"tdp": 180, "mem_clock": 1001, "graphics_clock": 1683},
    "GTX 1070": {"tdp": 150, "mem_clock": 1001, "graphics_clock": 1683},
    "GTX 1060": {"tdp": 120, "mem_clock": 1002, "graphics_clock": 1708},
    "GTX 1050 Ti": {"tdp": 75, "mem_clock": 875, "graphics_clock": 1392},
    "GTX 1050": {"tdp": 75, "mem_clock": 875, "graphics_clock": 1455},
    "GTX 1660 Ti": {"tdp": 120, "mem_clock": 1500, "graphics_clock": 1770},
    "GTX 1660 SUPER": {"tdp": 125, "mem_clock": 1750, "graphics_clock": 1785},
    "GTX 1660": {"tdp": 120, "mem_clock": 1000, "graphics_clock": 1785},
    "GTX 1650 SUPER": {"tdp": 100, "mem_clock": 1500, "graphics_clock": 1725},
    "GTX 1650": {"tdp": 75, "mem_clock": 1000, "graphics_clock": 1590},
    "GTX 980 Ti": {"tdp": 250, "mem_clock": 875, "graphics_clock": 1075},
    "GTX 980": {"tdp": 165, "mem_clock": 875, "graphics_clock": 1126},
    "GTX 970": {"tdp": 145, "mem_clock": 875, "graphics_clock": 1050},
    "GTX 960": {"tdp": 120, "mem_clock": 875, "graphics_clock": 1127},
    "GTX 950": {"tdp": 90, "mem_clock": 825, "graphics_clock": 1024},
    "GTX TITAN X": {"tdp": 250, "mem_clock": 875, "graphics_clock": 1000},
    "GTX TITAN": {"tdp": 250, "mem_clock": 750, "graphics_clock": 837},
    "TITAN RTX": {"tdp": 280, "mem_clock": 1750, "graphics_clock": 1770},
    "TITAN V": {"tdp": 250, "mem_clock": 850, "graphics_clock": 1455},
    "TITAN Xp": {"tdp": 250, "mem_clock": 1426, "graphics_clock": 1582},
}

DISTRO_FAMILIES = {
    "debian": ["debian", "ubuntu", "linuxmint", "pop", "elementary", "zorin", "kali", "parrot", "mx", "antiX", "deepin", "peppermint", "bodhi", "sparky", "devuan", "trisquel", "pureos"],
    "rhel": ["fedora", "centos", "rhel", "rocky", "alma", "oracle", "scientific", "clearos", "springdale"],
    "arch": ["arch", "manjaro", "endeavouros", "arcolinux", "garuda", "artix", "parabola", "blackarch", "archbang"],
    "suse": ["opensuse", "suse", "opensuse-leap", "opensuse-tumbleweed", "gecko"],
    "gentoo": ["gentoo", "funtoo", "calculate", "sabayon"],
    "void": ["void"],
    "alpine": ["alpine"],
    "slackware": ["slackware", "salix", "porteus", "zenwalk"],
    "nixos": ["nixos"],
    "solus": ["solus"],
    "clear": ["clear-linux-os"],
}


class DistroDetector:
    @staticmethod
    def detect() -> Tuple[str, str, str]:
        distro_id = ""
        distro_name = ""
        distro_version = ""

        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro_id = line.strip().split("=")[1].strip('"').lower()
                    elif line.startswith("NAME="):
                        distro_name = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("VERSION_ID="):
                        distro_version = line.strip().split("=")[1].strip('"')

        if not distro_id and os.path.exists("/etc/lsb-release"):
            with open("/etc/lsb-release", "r") as f:
                for line in f:
                    if line.startswith("DISTRIB_ID="):
                        distro_id = line.strip().split("=")[1].strip('"').lower()

        return distro_id, distro_name, distro_version

    @staticmethod
    def get_family(distro_id: str) -> str:
        for family, distros in DISTRO_FAMILIES.items():
            if distro_id in distros:
                return family
        return "unknown"


class GPUDetector:
    @staticmethod
    def detect() -> Optional[Dict]:
        try:
            result = subprocess.run(
                ["lspci", "-nn"],
                capture_output=True,
                text=True,
                check=True
            )
            nvidia_pattern = r"VGA.*NVIDIA.*\[([^\]]+)\]"
            match = re.search(nvidia_pattern, result.stdout, re.IGNORECASE)

            if not match:
                nvidia_pattern = r"3D.*NVIDIA.*\[([^\]]+)\]"
                match = re.search(nvidia_pattern, result.stdout, re.IGNORECASE)

            if match:
                gpu_name = match.group(1)
                return GPUDetector._get_gpu_info(gpu_name)

            for line in result.stdout.splitlines():
                if "NVIDIA" in line.upper():
                    gpu_name = GPUDetector._extract_gpu_name(line)
                    if gpu_name:
                        return GPUDetector._get_gpu_info(gpu_name)

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return None

    @staticmethod
    def _extract_gpu_name(line: str) -> Optional[str]:
        patterns = [
            r"(RTX\s*\d{4}\s*(?:Ti|SUPER)?(?:\s*Ti)?)",
            r"(GTX\s*\d{4}\s*(?:Ti|SUPER)?)",
            r"(GTX\s*TITAN\s*\w*)",
            r"(TITAN\s*\w+)",
            r"(GeForce\s+\w+\s*\d*\s*(?:Ti|SUPER)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _get_gpu_info(gpu_name: str) -> Dict:
        gpu_name_upper = gpu_name.upper().strip()
        gpu_name_normalized = re.sub(r'\s+', ' ', gpu_name_upper)

        for known_gpu, specs in GPU_POWER_LIMITS.items():
            known_upper = known_gpu.upper()
            if known_upper == gpu_name_normalized or known_upper == gpu_name_upper:
                return {
                    "name": known_gpu,
                    "detected_name": gpu_name,
                    "tdp": specs["tdp"],
                    "mem_clock": specs["mem_clock"],
                    "graphics_clock": specs["graphics_clock"],
                }

        sorted_gpus = sorted(GPU_POWER_LIMITS.keys(), key=len, reverse=True)

        for known_gpu in sorted_gpus:
            known_upper = known_gpu.upper()
            if known_upper in gpu_name_normalized or gpu_name_normalized in known_upper:
                specs = GPU_POWER_LIMITS[known_gpu]
                return {
                    "name": known_gpu,
                    "detected_name": gpu_name,
                    "tdp": specs["tdp"],
                    "mem_clock": specs["mem_clock"],
                    "graphics_clock": specs["graphics_clock"],
                }

        return {
            "name": gpu_name,
            "detected_name": gpu_name,
            "tdp": 150,
            "mem_clock": 1000,
            "graphics_clock": 1500,
        }


class PackageManager:
    def __init__(self, distro_family: str, distro_id: str, distro_version: str):
        self.family = distro_family
        self.distro_id = distro_id
        self.version = distro_version

    def get_install_commands(self) -> List[str]:
        commands = []

        if self.family == "debian":
            commands = self._get_debian_commands()
        elif self.family == "rhel":
            commands = self._get_rhel_commands()
        elif self.family == "arch":
            commands = self._get_arch_commands()
        elif self.family == "suse":
            commands = self._get_suse_commands()
        elif self.family == "gentoo":
            commands = self._get_gentoo_commands()
        elif self.family == "void":
            commands = self._get_void_commands()
        elif self.family == "alpine":
            commands = self._get_alpine_commands()
        elif self.family == "slackware":
            commands = self._get_slackware_commands()
        elif self.family == "nixos":
            commands = self._get_nixos_commands()
        elif self.family == "solus":
            commands = self._get_solus_commands()
        elif self.family == "clear":
            commands = self._get_clear_commands()

        return commands

    def _get_debian_commands(self) -> List[str]:
        commands = [
            "apt update",
            "apt install -y linux-headers-$(uname -r)",
            "apt install -y build-essential dkms",
        ]

        if self.distro_id == "debian":
            commands.extend([
                "apt install -y nvidia-driver firmware-misc-nonfree",
            ])
            if self.version and self.version.startswith("12"):
                commands.extend([
                    "apt -t bookworm-backports install -y nvidia-driver || true",
                    "apt -t bookworm-backports install -y linux-image-amd64 || true",
                ])
            elif self.version and self.version.startswith("11"):
                commands.extend([
                    "apt -t bullseye-backports install -y nvidia-driver || true",
                ])
        elif self.distro_id in ["ubuntu", "pop", "linuxmint", "elementary", "zorin"]:
            commands.extend([
                "add-apt-repository -y ppa:graphics-drivers/ppa || true",
                "apt update",
                "ubuntu-drivers install nvidia || apt install -y nvidia-driver-550 || apt install -y nvidia-driver",
            ])
        else:
            commands.append("apt install -y nvidia-driver")

        commands.append("apt install -y cpufrequtils")
        return commands

    def _get_rhel_commands(self) -> List[str]:
        commands = []

        if self.distro_id == "fedora":
            commands = [
                "dnf install -y kernel-devel kernel-headers",
                "dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm || true",
                "dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm || true",
                "dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda",
                "dnf install -y kernel-tools",
            ]
        elif self.distro_id in ["centos", "rhel", "rocky", "alma", "oracle"]:
            commands = [
                "yum install -y epel-release || dnf install -y epel-release",
                "yum install -y kernel-devel kernel-headers || dnf install -y kernel-devel kernel-headers",
                "yum install -y dkms || dnf install -y dkms",
                "yum install -y nvidia-driver nvidia-driver-cuda || dnf install -y nvidia-driver nvidia-driver-cuda",
                "yum install -y kernel-tools || dnf install -y kernel-tools",
            ]
        else:
            commands = [
                "dnf install -y kernel-devel kernel-headers akmod-nvidia xorg-x11-drv-nvidia",
                "dnf install -y kernel-tools",
            ]

        return commands

    def _get_arch_commands(self) -> List[str]:
        commands = [
            "pacman -Sy --noconfirm linux-headers",
            "pacman -S --noconfirm nvidia nvidia-utils nvidia-settings",
            "pacman -S --noconfirm cpupower",
        ]

        if self.distro_id == "manjaro":
            commands = [
                "mhwd -a pci nonfree 0300 || pacman -S --noconfirm nvidia nvidia-utils",
                "pacman -S --noconfirm cpupower",
            ]
        elif self.distro_id == "endeavouros":
            commands = [
                "pacman -Sy --noconfirm linux-headers nvidia-dkms nvidia-utils nvidia-settings",
                "pacman -S --noconfirm cpupower",
            ]

        return commands

    def _get_suse_commands(self) -> List[str]:
        commands = [
            "zypper install -y kernel-devel",
        ]

        if "tumbleweed" in self.distro_id.lower():
            commands.extend([
                "zypper addrepo --refresh https://download.nvidia.com/opensuse/tumbleweed NVIDIA || true",
                "zypper --gpg-auto-import-keys refresh",
                "zypper install -y nvidia-video-G06 nvidia-gl-G06",
            ])
        else:
            commands.extend([
                "zypper addrepo --refresh https://download.nvidia.com/opensuse/leap/$(. /etc/os-release && echo $VERSION_ID)/x86_64 NVIDIA || true",
                "zypper --gpg-auto-import-keys refresh",
                "zypper install -y nvidia-video-G06 nvidia-gl-G06 || zypper install -y nvidia-gfxG05-kmp-default",
            ])

        commands.append("zypper install -y cpupower")
        return commands

    def _get_gentoo_commands(self) -> List[str]:
        return [
            "emerge --sync",
            "emerge x11-drivers/nvidia-drivers",
            "emerge sys-power/cpupower",
        ]

    def _get_void_commands(self) -> List[str]:
        return [
            "xbps-install -Sy nvidia nvidia-libs nvidia-libs-32bit",
            "xbps-install -Sy linux-headers",
        ]

    def _get_alpine_commands(self) -> List[str]:
        return [
            "apk add --no-cache linux-headers",
            "apk add --no-cache nvidia-driver nvidia-utils",
        ]

    def _get_slackware_commands(self) -> List[str]:
        return [
            "sbopkg -i nvidia-driver nvidia-kernel",
        ]

    def _get_nixos_commands(self) -> List[str]:
        return [
            'echo "NixOS requires manual configuration in /etc/nixos/configuration.nix"',
            'echo "Add: services.xserver.videoDrivers = [ \\"nvidia\\" ];"',
            'echo "Then run: sudo nixos-rebuild switch"',
        ]

    def _get_solus_commands(self) -> List[str]:
        return [
            "eopkg install -y nvidia-glx-driver nvidia-glx-driver-32bit",
            "eopkg install -y linux-current-headers",
        ]

    def _get_clear_commands(self) -> List[str]:
        return [
            "swupd bundle-add kernel-native-dkms",
            "swupd bundle-add nvidia-driver",
        ]


class NvidiaConfigurator:
    def __init__(self, gpu_info: Dict):
        self.gpu_info = gpu_info

    def create_xorg_config(self) -> str:
        coolbits = self._get_coolbits()

        config = f'''Section "Device"
    Identifier "Nvidia Card"
    Driver "nvidia"
    Option "Coolbits" "{coolbits}"
    Option "TripleBuffer" "True"
    Option "AllowIndirectGLXProtocol" "off"
EndSection
'''
        return config

    def _get_coolbits(self) -> int:
        gpu_name = self.gpu_info.get("name", "").upper()

        if any(x in gpu_name for x in ["RTX 40", "RTX 30", "RTX 20"]):
            return 28
        elif any(x in gpu_name for x in ["GTX 16", "GTX 10"]):
            return 24
        elif "GTX 9" in gpu_name:
            return 12
        else:
            return 28

    def get_nvidia_smi_commands(self) -> List[str]:
        commands = [
            "nvidia-smi -pm 1",
            f"nvidia-smi -pl {self.gpu_info['tdp']}",
        ]
        return commands

    def get_clock_commands(self) -> List[str]:
        mem_clock = self.gpu_info.get("mem_clock", 1000)
        graphics_clock = self.gpu_info.get("graphics_clock", 1500)

        return [
            f"nvidia-smi -ac {mem_clock},{graphics_clock}",
        ]

    def get_profile_exports(self) -> str:
        exports = '''
# NVIDIA Performance Optimizations
export __GL_THREADED_OPTIMIZATIONS=1
export __GL_SHADER_CACHE=1
export __GL_SHADER_CACHE_SIZE=1000000000
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
export __GL_YIELD="USLEEP"
export __GL_MaxFramesAllowed=1
'''
        return exports


class SystemConfigurator:
    @staticmethod
    def run_command(cmd: str, sudo: bool = True) -> Tuple[bool, str]:
        if sudo and os.geteuid() != 0:
            cmd = f"sudo {cmd}"

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def write_xorg_config(content: str) -> bool:
        xorg_dir = Path("/etc/X11/xorg.conf.d")
        xorg_file = xorg_dir / "20-nvidia.conf"

        try:
            if os.geteuid() != 0:
                cmd = f'sudo mkdir -p {xorg_dir} && echo "{content}" | sudo tee {xorg_file}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0
            else:
                xorg_dir.mkdir(parents=True, exist_ok=True)
                xorg_file.write_text(content)
                return True
        except Exception:
            return False

    @staticmethod
    def update_profile(exports: str) -> bool:
        profile_path = Path.home() / ".profile"
        marker = "# NVIDIA Performance Optimizations"

        try:
            existing_content = ""
            if profile_path.exists():
                existing_content = profile_path.read_text()

            if marker in existing_content:
                return True

            with open(profile_path, "a") as f:
                f.write(exports)
            return True
        except Exception:
            return False

    @staticmethod
    def set_cpu_governor(family: str) -> bool:
        if family in ["arch", "manjaro"]:
            cmd = "cpupower frequency-set -g performance"
        else:
            cmd = "cpufreq-set -g performance"

        success, _ = SystemConfigurator.run_command(cmd)
        return success

    @staticmethod
    def ask_restart() -> bool:
        print("\n" + "=" * 60)
        print("Configuration complete!")
        print("A system restart is required to apply all changes.")
        print("=" * 60)

        while True:
            response = input("\nDo you want to restart now? (yes/no): ").strip().lower()
            if response in ["yes", "y"]:
                return True
            elif response in ["no", "n"]:
                return False
            print("Please enter 'yes' or 'no'")


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║           NVIDIA Stability for All Linux                      ║
║           GPU Configuration & Optimization Tool               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_status(message: str, success: bool = True):
    status = "✓" if success else "✗"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}[{status}]{reset} {message}")


def main():
    print_banner()

    if os.geteuid() != 0:
        print("Warning: Running without root privileges. Some operations may require sudo.")
        print()

    print("Detecting system configuration...\n")

    distro_id, distro_name, distro_version = DistroDetector.detect()
    distro_family = DistroDetector.get_family(distro_id)

    print_status(f"Distribution: {distro_name} ({distro_id})")
    print_status(f"Version: {distro_version}")
    print_status(f"Family: {distro_family}")

    if distro_family == "unknown":
        print("\nWarning: Unknown distribution. Will attempt generic configuration.")

    gpu_info = GPUDetector.detect()
    if not gpu_info:
        print("\n[!] No NVIDIA GPU detected. Please ensure your GPU is properly connected.")
        sys.exit(1)

    print()
    print_status(f"GPU Detected: {gpu_info['detected_name']}")
    print_status(f"Matched Profile: {gpu_info['name']}")
    print_status(f"TDP Limit: {gpu_info['tdp']}W")
    print_status(f"Memory Clock: {gpu_info['mem_clock']}MHz")
    print_status(f"Graphics Clock: {gpu_info['graphics_clock']}MHz")

    print("\n" + "=" * 60)
    print("Starting installation and configuration...")
    print("=" * 60 + "\n")

    pkg_manager = PackageManager(distro_family, distro_id, distro_version)
    install_commands = pkg_manager.get_install_commands()

    if install_commands:
        print("Installing NVIDIA drivers and dependencies...\n")
        for cmd in install_commands:
            print(f"  Running: {cmd}")
            success, output = SystemConfigurator.run_command(cmd)
            print_status(f"  {cmd[:50]}...", success)

    configurator = NvidiaConfigurator(gpu_info)

    print("\nConfiguring NVIDIA power management...")
    for cmd in configurator.get_nvidia_smi_commands():
        success, _ = SystemConfigurator.run_command(cmd)
        print_status(f"  {cmd}", success)

    print("\nSetting GPU clocks...")
    for cmd in configurator.get_clock_commands():
        success, _ = SystemConfigurator.run_command(cmd)
        print_status(f"  {cmd}", success)

    print("\nCreating Xorg configuration...")
    xorg_config = configurator.create_xorg_config()
    success = SystemConfigurator.write_xorg_config(xorg_config)
    print_status("  /etc/X11/xorg.conf.d/20-nvidia.conf", success)

    print("\nUpdating user profile with optimizations...")
    exports = configurator.get_profile_exports()
    success = SystemConfigurator.update_profile(exports)
    print_status("  ~/.profile updated", success)

    print("\nSetting CPU governor to performance...")
    success = SystemConfigurator.set_cpu_governor(distro_family)
    print_status("  CPU governor set to performance", success)

    if SystemConfigurator.ask_restart():
        print("\nRestarting system in 5 seconds...")
        SystemConfigurator.run_command("sleep 5 && reboot")
    else:
        print("\nPlease restart your system manually to apply all changes.")
        print("Command: sudo reboot")


if __name__ == "__main__":
    main()
