# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

# Set variables
set(DTC_OVERLAY_FILE esphome.overlay)
{% for item in variables %}
set({{ item.name }} {{ item.value }})
{% endfor %}

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(esphome_{{ project_name }})

target_sources(app
    PRIVATE
        src/main.c
        src/action.c
)