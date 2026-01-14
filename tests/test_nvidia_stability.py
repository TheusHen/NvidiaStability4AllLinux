#!/usr/bin/env python3

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nvidia_stability import (
    DistroDetector,
    GPUDetector,
    PackageManager,
    NvidiaConfigurator,
    GPU_POWER_LIMITS,
    DISTRO_FAMILIES,
)


class TestDistroDetector:
    def test_get_family_debian(self):
        assert DistroDetector.get_family("debian") == "debian"
        assert DistroDetector.get_family("ubuntu") == "debian"
        assert DistroDetector.get_family("linuxmint") == "debian"
        assert DistroDetector.get_family("pop") == "debian"

    def test_get_family_rhel(self):
        assert DistroDetector.get_family("fedora") == "rhel"
        assert DistroDetector.get_family("centos") == "rhel"
        assert DistroDetector.get_family("rocky") == "rhel"
        assert DistroDetector.get_family("alma") == "rhel"

    def test_get_family_arch(self):
        assert DistroDetector.get_family("arch") == "arch"
        assert DistroDetector.get_family("manjaro") == "arch"
        assert DistroDetector.get_family("endeavouros") == "arch"

    def test_get_family_suse(self):
        assert DistroDetector.get_family("opensuse") == "suse"
        assert DistroDetector.get_family("suse") == "suse"

    def test_get_family_gentoo(self):
        assert DistroDetector.get_family("gentoo") == "gentoo"
        assert DistroDetector.get_family("funtoo") == "gentoo"

    def test_get_family_void(self):
        assert DistroDetector.get_family("void") == "void"

    def test_get_family_alpine(self):
        assert DistroDetector.get_family("alpine") == "alpine"

    def test_get_family_nixos(self):
        assert DistroDetector.get_family("nixos") == "nixos"

    def test_get_family_solus(self):
        assert DistroDetector.get_family("solus") == "solus"

    def test_get_family_unknown(self):
        assert DistroDetector.get_family("unknown_distro") == "unknown"


class TestGPUDetector:
    def test_get_gpu_info_rtx_4090(self):
        result = GPUDetector._get_gpu_info("RTX 4090")
        assert result["name"] == "RTX 4090"
        assert result["tdp"] == 450
        assert result["mem_clock"] == 1313
        assert result["graphics_clock"] == 2520

    def test_get_gpu_info_rtx_3080(self):
        result = GPUDetector._get_gpu_info("GeForce RTX 3080")
        assert result["tdp"] == 320
        assert result["mem_clock"] == 1188
        assert result["graphics_clock"] == 1710

    def test_get_gpu_info_gtx_1080(self):
        result = GPUDetector._get_gpu_info("GTX 1080")
        assert result["tdp"] == 180
        assert result["mem_clock"] == 1251
        assert result["graphics_clock"] == 1733

    def test_get_gpu_info_unknown_gpu(self):
        result = GPUDetector._get_gpu_info("Unknown GPU Model")
        assert result["tdp"] == 150
        assert result["mem_clock"] == 1000
        assert result["graphics_clock"] == 1500

    def test_extract_gpu_name_rtx(self):
        line = "01:00.0 VGA compatible controller: NVIDIA Corporation GeForce RTX 3080 [10DE:2206]"
        result = GPUDetector._extract_gpu_name(line)
        assert "RTX 3080" in result or "GeForce" in result

    def test_extract_gpu_name_gtx(self):
        line = "01:00.0 VGA compatible controller: NVIDIA Corporation GeForce GTX 1080 Ti [10DE:1B06]"
        result = GPUDetector._extract_gpu_name(line)
        assert "GTX 1080 Ti" in result or "GeForce" in result


class TestPackageManager:
    def test_debian_commands(self):
        pm = PackageManager("debian", "debian", "12")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("apt" in cmd for cmd in commands)
        assert any("linux-headers" in cmd for cmd in commands)

    def test_ubuntu_commands(self):
        pm = PackageManager("debian", "ubuntu", "22.04")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("apt" in cmd for cmd in commands)

    def test_fedora_commands(self):
        pm = PackageManager("rhel", "fedora", "39")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("dnf" in cmd for cmd in commands)

    def test_arch_commands(self):
        pm = PackageManager("arch", "arch", "")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("pacman" in cmd for cmd in commands)

    def test_manjaro_commands(self):
        pm = PackageManager("arch", "manjaro", "")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("mhwd" in cmd or "pacman" in cmd for cmd in commands)

    def test_suse_commands(self):
        pm = PackageManager("suse", "opensuse-leap", "15.5")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("zypper" in cmd for cmd in commands)

    def test_gentoo_commands(self):
        pm = PackageManager("gentoo", "gentoo", "")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("emerge" in cmd for cmd in commands)

    def test_void_commands(self):
        pm = PackageManager("void", "void", "")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("xbps-install" in cmd for cmd in commands)

    def test_alpine_commands(self):
        pm = PackageManager("alpine", "alpine", "3.18")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("apk" in cmd for cmd in commands)

    def test_solus_commands(self):
        pm = PackageManager("solus", "solus", "")
        commands = pm.get_install_commands()
        assert len(commands) > 0
        assert any("eopkg" in cmd for cmd in commands)


class TestNvidiaConfigurator:
    def test_xorg_config_rtx_40(self):
        gpu_info = {"name": "RTX 4090", "tdp": 450, "mem_clock": 1313, "graphics_clock": 2520}
        config = NvidiaConfigurator(gpu_info)
        xorg = config.create_xorg_config()
        assert 'Identifier "Nvidia Card"' in xorg
        assert 'Driver "nvidia"' in xorg
        assert 'Coolbits' in xorg
        assert '"28"' in xorg

    def test_xorg_config_gtx_10(self):
        gpu_info = {"name": "GTX 1080", "tdp": 180, "mem_clock": 1251, "graphics_clock": 1733}
        config = NvidiaConfigurator(gpu_info)
        xorg = config.create_xorg_config()
        assert '"24"' in xorg

    def test_xorg_config_gtx_9(self):
        gpu_info = {"name": "GTX 980", "tdp": 165, "mem_clock": 875, "graphics_clock": 1126}
        config = NvidiaConfigurator(gpu_info)
        xorg = config.create_xorg_config()
        assert '"12"' in xorg

    def test_nvidia_smi_commands(self):
        gpu_info = {"name": "RTX 3080", "tdp": 320, "mem_clock": 1188, "graphics_clock": 1710}
        config = NvidiaConfigurator(gpu_info)
        commands = config.get_nvidia_smi_commands()
        assert "nvidia-smi -pm 1" in commands
        assert "nvidia-smi -pl 320" in commands

    def test_clock_commands(self):
        gpu_info = {"name": "RTX 3080", "tdp": 320, "mem_clock": 1188, "graphics_clock": 1710}
        config = NvidiaConfigurator(gpu_info)
        commands = config.get_clock_commands()
        assert "nvidia-smi -ac 1188,1710" in commands

    def test_profile_exports(self):
        gpu_info = {"name": "RTX 3080", "tdp": 320, "mem_clock": 1188, "graphics_clock": 1710}
        config = NvidiaConfigurator(gpu_info)
        exports = config.get_profile_exports()
        assert "__GL_THREADED_OPTIMIZATIONS=1" in exports
        assert "__GL_SHADER_CACHE=1" in exports
        assert "VK_ICD_FILENAMES" in exports


class TestGPUPowerLimits:
    def test_all_gpus_have_required_fields(self):
        for gpu_name, specs in GPU_POWER_LIMITS.items():
            assert "tdp" in specs, f"{gpu_name} missing tdp"
            assert "mem_clock" in specs, f"{gpu_name} missing mem_clock"
            assert "graphics_clock" in specs, f"{gpu_name} missing graphics_clock"

    def test_tdp_values_are_reasonable(self):
        for gpu_name, specs in GPU_POWER_LIMITS.items():
            assert 50 <= specs["tdp"] <= 600, f"{gpu_name} has unreasonable TDP: {specs['tdp']}"

    def test_clock_values_are_positive(self):
        for gpu_name, specs in GPU_POWER_LIMITS.items():
            assert specs["mem_clock"] > 0, f"{gpu_name} has invalid mem_clock"
            assert specs["graphics_clock"] > 0, f"{gpu_name} has invalid graphics_clock"


class TestDistroFamilies:
    def test_all_major_distros_covered(self):
        major_distros = ["debian", "ubuntu", "fedora", "arch", "manjaro", "opensuse", "gentoo"]
        for distro in major_distros:
            found = False
            for family, distros in DISTRO_FAMILIES.items():
                if distro in distros:
                    found = True
                    break
            assert found, f"Major distro {distro} not covered"

    def test_no_duplicate_distros(self):
        all_distros = []
        for distros in DISTRO_FAMILIES.values():
            all_distros.extend(distros)
        assert len(all_distros) == len(set(all_distros)), "Duplicate distros found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
