#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           NVIDIA Stability for All Linux                      ║"
    echo "║           GPU Configuration & Optimization Tool               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_warn "This script should be run as root for full functionality"
        log_info "Some operations will require sudo password"
    fi
}

detect_distro() {
    local distro_id=""
    local distro_name=""
    local distro_version=""
    local distro_family=""

    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        distro_id="${ID:-unknown}"
        distro_name="${NAME:-Unknown}"
        distro_version="${VERSION_ID:-}"
    elif [[ -f /etc/lsb-release ]]; then
        source /etc/lsb-release
        distro_id="${DISTRIB_ID:-unknown}"
        distro_name="${DISTRIB_DESCRIPTION:-Unknown}"
        distro_version="${DISTRIB_RELEASE:-}"
    fi

    distro_id=$(echo "$distro_id" | tr '[:upper:]' '[:lower:]')

    case "$distro_id" in
        debian|ubuntu|linuxmint|pop|elementary|zorin|kali|parrot|mx|deepin|peppermint|bodhi|sparky|devuan|trisquel|pureos)
            distro_family="debian"
            ;;
        fedora|centos|rhel|rocky|alma|oracle|scientific|clearos)
            distro_family="rhel"
            ;;
        arch|manjaro|endeavouros|arcolinux|garuda|artix|parabola|blackarch)
            distro_family="arch"
            ;;
        opensuse*|suse|gecko)
            distro_family="suse"
            ;;
        gentoo|funtoo|calculate|sabayon)
            distro_family="gentoo"
            ;;
        void)
            distro_family="void"
            ;;
        alpine)
            distro_family="alpine"
            ;;
        slackware|salix|porteus|zenwalk)
            distro_family="slackware"
            ;;
        nixos)
            distro_family="nixos"
            ;;
        solus)
            distro_family="solus"
            ;;
        clear-linux-os)
            distro_family="clear"
            ;;
        *)
            distro_family="unknown"
            ;;
    esac

    echo "$distro_id|$distro_name|$distro_version|$distro_family"
}

detect_gpu() {
    local gpu_info=""

    if command -v lspci &> /dev/null; then
        gpu_info=$(lspci -nn 2>/dev/null | grep -iE "(VGA|3D)" | grep -i nvidia || true)
    fi

    if [[ -z "$gpu_info" ]]; then
        echo ""
        return
    fi

    echo "$gpu_info"
}

get_gpu_specs() {
    local gpu_name="$1"
    local tdp=150
    local mem_clock=1000
    local graphics_clock=1500

    case "$gpu_name" in
        *"4090"*)
            tdp=450; mem_clock=1313; graphics_clock=2520 ;;
        *"4080 SUPER"*|*"4080 Super"*)
            tdp=320; mem_clock=1438; graphics_clock=2550 ;;
        *"4080"*)
            tdp=320; mem_clock=1400; graphics_clock=2505 ;;
        *"4070 Ti SUPER"*|*"4070 Ti Super"*)
            tdp=285; mem_clock=1313; graphics_clock=2610 ;;
        *"4070 Ti"*)
            tdp=285; mem_clock=1313; graphics_clock=2610 ;;
        *"4070 SUPER"*|*"4070 Super"*)
            tdp=220; mem_clock=1313; graphics_clock=2475 ;;
        *"4070"*)
            tdp=200; mem_clock=1313; graphics_clock=2475 ;;
        *"4060 Ti"*)
            tdp=160; mem_clock=1125; graphics_clock=2535 ;;
        *"4060"*)
            tdp=115; mem_clock=1125; graphics_clock=2460 ;;
        *"3090 Ti"*)
            tdp=450; mem_clock=1313; graphics_clock=1860 ;;
        *"3090"*)
            tdp=350; mem_clock=1219; graphics_clock=1695 ;;
        *"3080 Ti"*)
            tdp=350; mem_clock=1188; graphics_clock=1665 ;;
        *"3080"*)
            tdp=320; mem_clock=1188; graphics_clock=1710 ;;
        *"3070 Ti"*)
            tdp=290; mem_clock=1188; graphics_clock=1770 ;;
        *"3070"*)
            tdp=220; mem_clock=1188; graphics_clock=1725 ;;
        *"3060 Ti"*)
            tdp=200; mem_clock=1188; graphics_clock=1670 ;;
        *"3060"*)
            tdp=170; mem_clock=1875; graphics_clock=1777 ;;
        *"3050"*)
            tdp=130; mem_clock=1750; graphics_clock=1777 ;;
        *"2080 Ti"*)
            tdp=250; mem_clock=1750; graphics_clock=1545 ;;
        *"2080 SUPER"*|*"2080 Super"*)
            tdp=250; mem_clock=1937; graphics_clock=1815 ;;
        *"2080"*)
            tdp=215; mem_clock=1750; graphics_clock=1710 ;;
        *"2070 SUPER"*|*"2070 Super"*)
            tdp=215; mem_clock=1750; graphics_clock=1770 ;;
        *"2070"*)
            tdp=175; mem_clock=1750; graphics_clock=1620 ;;
        *"2060 SUPER"*|*"2060 Super"*)
            tdp=175; mem_clock=1750; graphics_clock=1650 ;;
        *"2060"*)
            tdp=160; mem_clock=1750; graphics_clock=1680 ;;
        *"1080 Ti"*)
            tdp=250; mem_clock=1376; graphics_clock=1582 ;;
        *"1080"*)
            tdp=180; mem_clock=1251; graphics_clock=1733 ;;
        *"1070 Ti"*)
            tdp=180; mem_clock=1001; graphics_clock=1683 ;;
        *"1070"*)
            tdp=150; mem_clock=1001; graphics_clock=1683 ;;
        *"1060"*)
            tdp=120; mem_clock=1002; graphics_clock=1708 ;;
        *"1050 Ti"*)
            tdp=75; mem_clock=875; graphics_clock=1392 ;;
        *"1050"*)
            tdp=75; mem_clock=875; graphics_clock=1455 ;;
        *"1660 Ti"*)
            tdp=120; mem_clock=1500; graphics_clock=1770 ;;
        *"1660 SUPER"*|*"1660 Super"*)
            tdp=125; mem_clock=1750; graphics_clock=1785 ;;
        *"1660"*)
            tdp=120; mem_clock=1000; graphics_clock=1785 ;;
        *"1650 SUPER"*|*"1650 Super"*)
            tdp=100; mem_clock=1500; graphics_clock=1725 ;;
        *"1650"*)
            tdp=75; mem_clock=1000; graphics_clock=1590 ;;
    esac

    echo "$tdp|$mem_clock|$graphics_clock"
}

install_drivers_debian() {
    local distro_id="$1"
    local version="$2"

    sudo apt update
    sudo apt install -y linux-headers-$(uname -r) build-essential dkms

    case "$distro_id" in
        debian)
            sudo apt install -y nvidia-driver firmware-misc-nonfree || true
            if [[ "$version" == "12"* ]]; then
                sudo apt -t bookworm-backports install -y nvidia-driver 2>/dev/null || true
                sudo apt -t bookworm-backports install -y linux-image-amd64 2>/dev/null || true
            elif [[ "$version" == "11"* ]]; then
                sudo apt -t bullseye-backports install -y nvidia-driver 2>/dev/null || true
            fi
            ;;
        ubuntu|pop|linuxmint|elementary|zorin)
            sudo add-apt-repository -y ppa:graphics-drivers/ppa 2>/dev/null || true
            sudo apt update
            sudo ubuntu-drivers install nvidia 2>/dev/null || sudo apt install -y nvidia-driver-550 2>/dev/null || sudo apt install -y nvidia-driver
            ;;
        *)
            sudo apt install -y nvidia-driver
            ;;
    esac

    sudo apt install -y cpufrequtils || true
}

install_drivers_rhel() {
    local distro_id="$1"

    case "$distro_id" in
        fedora)
            sudo dnf install -y kernel-devel kernel-headers
            sudo dnf install -y "https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm" 2>/dev/null || true
            sudo dnf install -y "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm" 2>/dev/null || true
            sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
            sudo dnf install -y kernel-tools
            ;;
        *)
            sudo yum install -y epel-release 2>/dev/null || sudo dnf install -y epel-release
            sudo yum install -y kernel-devel kernel-headers dkms 2>/dev/null || sudo dnf install -y kernel-devel kernel-headers dkms
            sudo yum install -y nvidia-driver nvidia-driver-cuda 2>/dev/null || sudo dnf install -y nvidia-driver nvidia-driver-cuda
            sudo yum install -y kernel-tools 2>/dev/null || sudo dnf install -y kernel-tools
            ;;
    esac
}

install_drivers_arch() {
    local distro_id="$1"

    case "$distro_id" in
        manjaro)
            sudo mhwd -a pci nonfree 0300 2>/dev/null || sudo pacman -S --noconfirm nvidia nvidia-utils
            ;;
        *)
            sudo pacman -Sy --noconfirm linux-headers
            sudo pacman -S --noconfirm nvidia nvidia-utils nvidia-settings
            ;;
    esac

    sudo pacman -S --noconfirm cpupower || true
}

install_drivers_suse() {
    local distro_id="$1"

    sudo zypper install -y kernel-devel

    if [[ "$distro_id" == *"tumbleweed"* ]]; then
        sudo zypper addrepo --refresh https://download.nvidia.com/opensuse/tumbleweed NVIDIA 2>/dev/null || true
    else
        local version=$(. /etc/os-release && echo $VERSION_ID)
        sudo zypper addrepo --refresh "https://download.nvidia.com/opensuse/leap/${version}/x86_64" NVIDIA 2>/dev/null || true
    fi

    sudo zypper --gpg-auto-import-keys refresh
    sudo zypper install -y nvidia-video-G06 nvidia-gl-G06 2>/dev/null || sudo zypper install -y nvidia-gfxG05-kmp-default
    sudo zypper install -y cpupower || true
}

install_drivers_gentoo() {
    sudo emerge --sync
    sudo emerge x11-drivers/nvidia-drivers
    sudo emerge sys-power/cpupower
}

install_drivers_void() {
    sudo xbps-install -Sy nvidia nvidia-libs nvidia-libs-32bit linux-headers
}

install_drivers_alpine() {
    sudo apk add --no-cache linux-headers nvidia-driver nvidia-utils
}

install_drivers_solus() {
    sudo eopkg install -y nvidia-glx-driver nvidia-glx-driver-32bit linux-current-headers
}

install_drivers_clear() {
    sudo swupd bundle-add kernel-native-dkms nvidia-driver
}

install_drivers() {
    local family="$1"
    local distro_id="$2"
    local version="$3"

    log_info "Installing NVIDIA drivers for $family family..."

    case "$family" in
        debian)
            install_drivers_debian "$distro_id" "$version"
            ;;
        rhel)
            install_drivers_rhel "$distro_id"
            ;;
        arch)
            install_drivers_arch "$distro_id"
            ;;
        suse)
            install_drivers_suse "$distro_id"
            ;;
        gentoo)
            install_drivers_gentoo
            ;;
        void)
            install_drivers_void
            ;;
        alpine)
            install_drivers_alpine
            ;;
        solus)
            install_drivers_solus
            ;;
        clear)
            install_drivers_clear
            ;;
        nixos)
            log_warn "NixOS requires manual configuration in /etc/nixos/configuration.nix"
            log_info "Add: services.xserver.videoDrivers = [ \"nvidia\" ];"
            log_info "Then run: sudo nixos-rebuild switch"
            ;;
        *)
            log_error "Unknown distribution family: $family"
            return 1
            ;;
    esac
}

configure_nvidia_power() {
    local tdp="$1"
    local mem_clock="$2"
    local graphics_clock="$3"

    log_info "Configuring NVIDIA power management..."

    sudo nvidia-smi -pm 1 2>/dev/null || log_warn "Could not enable persistence mode"
    sudo nvidia-smi -pl "$tdp" 2>/dev/null || log_warn "Could not set power limit to ${tdp}W"
    sudo nvidia-smi -ac "${mem_clock},${graphics_clock}" 2>/dev/null || log_warn "Could not set application clocks"
}

create_xorg_config() {
    local gpu_name="$1"
    local coolbits=28

    if [[ "$gpu_name" == *"GTX 9"* ]]; then
        coolbits=12
    elif [[ "$gpu_name" == *"GTX 10"* ]] || [[ "$gpu_name" == *"GTX 16"* ]]; then
        coolbits=24
    fi

    log_info "Creating Xorg configuration..."

    sudo mkdir -p /etc/X11/xorg.conf.d

    cat << EOF | sudo tee /etc/X11/xorg.conf.d/20-nvidia.conf > /dev/null
Section "Device"
    Identifier "Nvidia Card"
    Driver "nvidia"
    Option "Coolbits" "${coolbits}"
    Option "TripleBuffer" "True"
    Option "AllowIndirectGLXProtocol" "off"
EndSection
EOF

    log_info "Created /etc/X11/xorg.conf.d/20-nvidia.conf"
}

update_profile() {
    local profile_file="$HOME/.profile"
    local marker="# NVIDIA Performance Optimizations"

    if grep -q "$marker" "$profile_file" 2>/dev/null; then
        log_info "Profile already configured"
        return 0
    fi

    log_info "Updating ~/.profile with NVIDIA optimizations..."

    cat << 'EOF' >> "$profile_file"

# NVIDIA Performance Optimizations
export __GL_THREADED_OPTIMIZATIONS=1
export __GL_SHADER_CACHE=1
export __GL_SHADER_CACHE_SIZE=1000000000
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
export __GL_YIELD="USLEEP"
export __GL_MaxFramesAllowed=1
EOF

    log_info "Updated ~/.profile"
}

set_cpu_governor() {
    local family="$1"

    log_info "Setting CPU governor to performance..."

    if [[ "$family" == "arch" ]]; then
        sudo cpupower frequency-set -g performance 2>/dev/null || log_warn "Could not set CPU governor"
    else
        sudo cpufreq-set -g performance 2>/dev/null || log_warn "Could not set CPU governor"
    fi
}

ask_restart() {
    echo ""
    echo "============================================================"
    echo "Configuration complete!"
    echo "A system restart is required to apply all changes."
    echo "============================================================"
    echo ""

    while true; do
        read -p "Do you want to restart now? (yes/no): " response
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                log_info "Restarting system in 5 seconds..."
                sleep 5
                sudo reboot
                ;;
            [Nn]|[Nn][Oo])
                log_info "Please restart your system manually to apply all changes."
                log_info "Command: sudo reboot"
                return 0
                ;;
            *)
                echo "Please enter 'yes' or 'no'"
                ;;
        esac
    done
}

main() {
    print_banner
    check_root

    echo "Detecting system configuration..."
    echo ""

    IFS='|' read -r distro_id distro_name distro_version distro_family <<< "$(detect_distro)"

    log_info "Distribution: $distro_name ($distro_id)"
    log_info "Version: $distro_version"
    log_info "Family: $distro_family"

    if [[ "$distro_family" == "unknown" ]]; then
        log_warn "Unknown distribution. Will attempt generic configuration."
    fi

    echo ""
    gpu_info=$(detect_gpu)

    if [[ -z "$gpu_info" ]]; then
        log_error "No NVIDIA GPU detected. Please ensure your GPU is properly connected."
        exit 1
    fi

    log_info "GPU Detected: $gpu_info"

    IFS='|' read -r tdp mem_clock graphics_clock <<< "$(get_gpu_specs "$gpu_info")"

    log_info "TDP Limit: ${tdp}W"
    log_info "Memory Clock: ${mem_clock}MHz"
    log_info "Graphics Clock: ${graphics_clock}MHz"

    echo ""
    echo "============================================================"
    echo "Starting installation and configuration..."
    echo "============================================================"
    echo ""

    install_drivers "$distro_family" "$distro_id" "$distro_version"

    configure_nvidia_power "$tdp" "$mem_clock" "$graphics_clock"

    create_xorg_config "$gpu_info"

    update_profile

    set_cpu_governor "$distro_family"

    ask_restart
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
