# SPDX-License-Identifier: Apache-2.0

include({{ project }}.cmake OPTIONAL)

zephyr_library({{ project }}_rpc)
zephyr_library_include_directories(.)

FILE(GLOB {{ project }}_src *.c)
zephyr_library_sources({{ '${'  }}{{ project }}{{ '_src}' }})

add_compile_definitions_ifdef(CONFIG_{{ PREFIX }}RPC_DUMP HAS_PROTO_MESSAGE_DUMP)
zephyr_library_compile_options(-Wno-deprecated-declarations)
