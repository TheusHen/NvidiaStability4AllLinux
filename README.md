![Linus Torvalds to NVIDIA](<.github/assets/Linus Torvalds - Middle Finger.png>)

# NVIDIA Stability for All Linux

A comprehensive tool for automatically detecting and configuring NVIDIA graphics cards on any Linux distribution.

## Features

- **Universal Linux Support**: Works on Debian, Ubuntu, Fedora, Arch, openSUSE, Gentoo, Void, Alpine, NixOS, Solus, Clear Linux, and many more
- **Automatic GPU Detection**: Detects your NVIDIA GPU model and applies optimal settings
- **Driver Installation**: Installs the appropriate NVIDIA drivers for your distribution
- **Power Management**: Configures TDP limits and clock speeds based on your GPU model
- **Xorg Configuration**: Creates optimized Xorg configuration with Coolbits settings
- **Performance Optimizations**: Sets up environment variables for maximum performance
- **CPU Governor**: Optionally sets CPU governor to performance mode

## Supported GPUs

- RTX 40 Series (4090, 4080, 4070 Ti, 4070, 4060 Ti, 4060)
- RTX 30 Series (3090 Ti, 3090, 3080 Ti, 3080, 3070 Ti, 3070, 3060 Ti, 3060, 3050)
- RTX 20 Series (2080 Ti, 2080 Super, 2080, 2070 Super, 2070, 2060 Super, 2060)
- GTX 16 Series (1660 Ti, 1660 Super, 1660, 1650 Super, 1650)
- GTX 10 Series (1080 Ti, 1080, 1070 Ti, 1070, 1060, 1050 Ti, 1050)
- GTX 9 Series (980 Ti, 980, 970, 960, 950)
- TITAN Series (RTX, V, Xp, X)

## Supported Distributions

| Family | Distributions |
|--------|--------------|
| Debian | Debian, Ubuntu, Linux Mint, Pop!_OS, Elementary, Zorin, Kali, MX Linux, Deepin |
| RHEL | Fedora, CentOS, RHEL, Rocky Linux, AlmaLinux, Oracle Linux |
| Arch | Arch Linux, Manjaro, EndeavourOS, ArcoLinux, Garuda, Artix |
| SUSE | openSUSE Leap, openSUSE Tumbleweed, SUSE Enterprise |
| Gentoo | Gentoo, Funtoo, Calculate Linux |
| Other | Void Linux, Alpine, Slackware, NixOS, Solus, Clear Linux |

## Installation

### Quick Start (Bash)

```bash
git clone https://github.com/TheusHen/NvidiaStability4AllLinux.git
cd NvidiaStability4AllLinux
chmod +x bin/nvidia-stability.sh
sudo ./bin/nvidia-stability.sh
```

### Using Python

```bash
git clone https://github.com/TheusHen/NvidiaStability4AllLinux.git
cd NvidiaStability4AllLinux
sudo python3 src/nvidia_stability.py
```

## What It Does

1. **Detects your Linux distribution** and selects the appropriate package manager
2. **Detects your NVIDIA GPU** and looks up optimal settings
3. **Installs NVIDIA drivers** using your distribution's package manager
4. **Configures power management**:
   - Enables persistence mode (`nvidia-smi -pm 1`)
   - Sets power limit based on GPU TDP
   - Configures memory and graphics clocks
5. **Creates Xorg configuration** at `/etc/X11/xorg.conf.d/20-nvidia.conf`
6. **Updates ~/.profile** with performance environment variables:
   ```bash
   export __GL_THREADED_OPTIMIZATIONS=1
   export __GL_SHADER_CACHE=1
   export __GL_SHADER_CACHE_SIZE=1000000000
   export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
   ```
7. **Sets CPU governor** to performance mode
8. **Asks to restart** the system to apply changes

## Configuration Files Created

### /etc/X11/xorg.conf.d/20-nvidia.conf

```
Section "Device"
    Identifier "Nvidia Card"
    Driver "nvidia"
    Option "Coolbits" "28"
    Option "TripleBuffer" "True"
    Option "AllowIndirectGLXProtocol" "off"
EndSection
```

The Coolbits value varies based on GPU generation:
- RTX 20/30/40 Series: 28
- GTX 10/16 Series: 24
- GTX 9 Series: 12

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run Python tests
pytest tests/test_nvidia_stability.py -v

# Run Bash tests
chmod +x tests/test_bash.sh
./tests/test_bash.sh
```

## Requirements

- Linux operating system
- NVIDIA graphics card
- Root/sudo access
- Python 3.9+ (for Python version)
- Bash 4.0+ (for Bash version)

## Safety Notes

- The tool uses official distribution repositories for driver installation
- Power limits are set to manufacturer-specified TDP values
- All configurations can be easily reverted
- A backup of your profile is recommended before running

## License

This project is licensed under the Mozilla Public License 2.0 - see the [LICENSE](LICENSE) file for details.