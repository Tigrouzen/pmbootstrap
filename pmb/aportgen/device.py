"""
Copyright 2017 Oliver Smith

This file is part of pmbootstrap.

pmbootstrap is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pmbootstrap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pmbootstrap.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import pmb.helpers.run
import pmb.aportgen.core
import pmb.parse.apkindex


def ask_for_architecture(args):
    architectures = pmb.config.build_device_architectures
    while True:
        ret = pmb.helpers.cli.ask(args, "Device architecture", architectures,
                                  "armhf")
        if ret in architectures:
            return ret
        logging.fatal("ERROR: Invalid architecture specified. If you want to"
                      " add a new architecture, edit build_device_architectures"
                      " in pmb/config/__init__.py.")


def ask_for_manufacturer(args):
    logging.info("Who produced the device (e.g. LG)?")
    return pmb.helpers.cli.ask(args, "Manufacturer", None, None, False)


def ask_for_name(args):
    logging.info("What is the official name (e.g. Google Nexus 5)?")
    return pmb.helpers.cli.ask(args, "Name", None, None, False)


def ask_for_keyboard(args):
    return pmb.helpers.cli.confirm(args, "Does the device has a hardware keyboard?")


def ask_for_external_storage(args):
    return pmb.helpers.cli.confirm(args, "Does the device have an sdcard or other"
                                   " external storage medium?")


def generate_deviceinfo(args, pkgname, name, manufacturer, arch, has_keyboard,
                        has_external_storage):
    content = """\
        # Reference: <https://postmarketos.org/deviceinfo>
        # Please use double quotes only. You can source this file in shell scripts.

        deviceinfo_format_version="0"
        deviceinfo_name=\"""" + name + """\"
        deviceinfo_manufacturer=\"""" + manufacturer + """\"
        deviceinfo_date=""
        deviceinfo_dtb=""
        deviceinfo_modules_initfs=""
        deviceinfo_external_disk_install="false"
        deviceinfo_arch=\"""" + arch + """\"

        # Device related
        deviceinfo_keyboard=\"""" + ("true" if has_keyboard else "false") + """\"
        deviceinfo_external_disk=\"""" + ("true" if has_external_storage else "false") + """\"
        deviceinfo_screen_width="800"
        deviceinfo_screen_height="600"
        deviceinfo_dev_touchscreen=""
        deviceinfo_dev_keyboard=""

        # Bootloader related
        deviceinfo_kernel_cmdline=""
        deviceinfo_generate_bootimg="true"
        deviceinfo_flash_methods=""
        deviceinfo_flash_offset_base=""
        deviceinfo_flash_offset_kernel=""
        deviceinfo_flash_offset_ramdisk=""
        deviceinfo_flash_offset_second=""
        deviceinfo_flash_offset_tags=""
        deviceinfo_flash_pagesize="2048"
        """

    # Write to file
    pmb.helpers.run.user(args, ["mkdir", "-p", args.work + "/aportgen"])
    with open(args.work + "/aportgen/deviceinfo", "w", encoding="utf-8") as handle:
        for line in content.split("\n"):
            handle.write(line[8:] + "\n")


def generate_apkbuild(args, pkgname, name, arch):
    device = "-".join(pkgname.split("-")[1:])
    content = """\
        pkgname=\"""" + pkgname + """\"
        pkgdesc=\"""" + name + """\"
        pkgver=0.1
        pkgrel=0
        url="https://postmarketos.org"
        license="MIT"
        arch="noarch"
        options="!check"
        depends="linux-""" + device + """\"
        source="deviceinfo"

        package() {
            install -Dm644 "$srcdir"/deviceinfo \\
                "$pkgdir"/etc/deviceinfo
        }

        sha512sums="(run 'pmbootstrap checksum """ + pkgname + """' to fill)"
        """

    # Write the file
    pmb.helpers.run.user(args, ["mkdir", "-p", args.work + "/aportgen"])
    with open(args.work + "/aportgen/APKBUILD", "w", encoding="utf-8") as handle:
        for line in content.split("\n"):
            handle.write(line[8:].replace(" " * 4, "\t") + "\n")


def generate(args, pkgname):
    arch = ask_for_architecture(args)
    manufacturer = ask_for_manufacturer(args)
    name = ask_for_name(args)
    has_keyboard = ask_for_keyboard(args)
    has_external_storage = ask_for_external_storage(args)

    generate_deviceinfo(args, pkgname, name, manufacturer, arch, has_keyboard,
                        has_external_storage)
    generate_apkbuild(args, pkgname, name, arch)
