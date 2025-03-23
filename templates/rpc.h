
/*
 * Copyright (c) 2024 Alexandre Bailon
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef __ZEPHYR_{{PREFIX } } CLIENT_RPC_H__
#define __ZEPHYR_                                                                                  \
	{                                                                                          \
		{                                                                                  \
			PREFIX                                                                     \
		}                                                                                  \
	}                                                                                          \
	CLIENT_RPC_H__

#include <stdbool.h>
#include <stdlib.h>

#include <zephyr/device.h>
#include <zephyr/logging/log.h>

#include "{{ pb_header }}"

struct {
	{
		function_prefix
	}
} rpc_data
{
	int socket;
};

extern ProtobufCAllocator{{protobuf_c_allocator_name}};

{% for msg in messages %
}
{
	% if msg.field %
}
int{{msg.msg_cb_function_name}}({{user_data_def}}, {{msg.msg_data_def}});
int{{msg.msg_write_function_name}}({{user_data_def}}, {{msg.msg_data_def}});
{
	% else %
}
int{{msg.msg_cb_function_name}}({{user_data_def}});
int{{msg.msg_write_function_name}}({{user_data_def}});
{
	% endif %
}
{
	% endfor %
}

int
{
	{
		function_prefix
	}
}
rpc_service(void *arg1, void *arg2, void *arg3);

#endif /* __ZEPHYR_{{PREFIX}}CLIENT_RPC_H__ */
