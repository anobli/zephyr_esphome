# Copyright (c) 2025 Alexandre Bailon
# SPDX-License-Identifier: Apache-2.0
#
zephyr_include_directories(include)

add_subdirectory(drivers/)
add_subdirectory_ifdef(CONFIG_ESPHOME subsys/net/lib/esphome)
