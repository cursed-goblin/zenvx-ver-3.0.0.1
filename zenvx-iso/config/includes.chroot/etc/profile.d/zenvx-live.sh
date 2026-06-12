# zenvx-live.sh - detect the Install-to-Disk GRUB entry and launch the installer.
# The 'Install to Disk' GRUB entry adds the kernel parameter zenvx_install=yes.
if grep -qw 'zenvx_install=yes' /proc/cmdline 2>/dev/null; then
	if [ "$(tty)" = "/dev/tty1" ] && [ ! -f /var/lib/zenvx/.installer_launched ]; then
		touch /var/lib/zenvx/.installer_launched 2>/dev/null || true
		echo "Launching ZenvX disk installer..."
		sudo zenvx-install
	fi
fi
