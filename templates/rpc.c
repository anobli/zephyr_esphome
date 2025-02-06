{
#templates / rpc.c #
}

/*
 * Copyright (c) 2024 Alexandre Bailon
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#include "{{ pb_header }}"
#include "{{ function_prefix }}rpc.h"

#include <zephyr/kernel.h>
#include <zephyr/net/socket.h>

#include <zephyr/logging/log.h>
LOG_MODULE_REGISTER(
	{
		{
			function_prefix
		}
	} rpc,
	CONFIG_ {
		{
			PROJECT
		}
	} _RPC_LOG_LEVEL);

static int varint_encode(uint64_t val, uint8_t *out);
static int
{
	{
		function_prefix
	}
}
header_size(uint32_t rpc_id, size_t len);
static int
{
	{
		function_prefix
	}
}
encode_header(uint32_t rpc_id, size_t len, uint8_t *out);
static int
{
	{
		function_prefix
	}
}
rpc_send(const struct device *dev, void *out, size_t len);
static void *zephyr_alloc(void *allocator_data, size_t size);
static void zephyr_free(void *allocator_data, void *pointer);

ProtobufCAllocator{{protobuf_c_allocator_name}} = {
	.alloc = zephyr_alloc,
	.free = zephyr_free,
	.allocator_data = NULL,
};

#ifdef HAS_PROTO_MESSAGE_DUMP
{% for msg in messages %
}
{
	% if msg.field %
}
static void{{msg.msg_dump_function_name}}({{msg.msg_data_def}})
{
	LOG_PRINTK("{{ msg.name }}: {\n");
	{% for field in msg.field %
	}
	{
		% if field.type == 1 %
	}
	LOG_PRINTK("\t{{ field.name }}: %g\n", {{field.value}});
	{ % elif field.type == 2 % } LOG_PRINTK("\t{{ field.name }}: %f\n", {{field.value}});
	{ % elif field.type == 3 or field.type == 16 or
	  field.type == 18 % } LOG_PRINTK("\t{{ field.name }}: %ld\n", {{field.value}});
	{ % elif field.type == 4 or field.type == 6 % } LOG_PRINTK("\t{{ field.name }}: %lu\n",
								   {{field.value}});
	{ % elif field.type == 5 or field.type == 15 or
	  field.type == 17 % } LOG_PRINTK("\t{{ field.name }}: %d\n", {{field.value}});
	{ % elif field.type == 7 or field.type == 13 % } LOG_PRINTK("\t{{ field.name }}: %u\n",
								    {{field.value}});
	{ % elif field.type == 8 % } LOG_PRINTK("\t{{ field.name }}: %s\n",
						{{field.value}} ? "True" : "False");
	{ % elif field.type == 9 % } LOG_PRINTK("\t{{ field.name }}: %s\n", {{field.value}});
	{
		% elif field.type == 11 %
	}
	// TODO: {{ field.name }}
	{ % elif field.type == 12 % } LOG_HEXDUMP_INF({{field.value}}.data, {{field.value}}.len,
						      "{{ field.name }}:");
	{ % elif field.type == 14 % } LOG_PRINTK("\t{{ field.name }}: %s\n", {
		{
			field.type_name
		}
	} _enum_to_string({{field.value}}));
	{
		% else %
	}
	// Not supported type for {{ field.name }}
	{
		% endif %
	}
	{ % endfor % } LOG_PRINTK("}\n");
}
{
	% else %
}
static void{{msg.msg_dump_function_name}}(void)
{
	LOG_PRINTK("{{ msg.name }}: {\n");
	LOG_PRINTK("}\n");
}
{
	% endif %
}
{
	% endfor %
}
#endif /* HAS_PROTO_MESSAGE_DUMP */

{% for msg in messages %
}
{
	% if msg.field %
}
__weak int{{msg.msg_cb_function_name}}({{user_data_def}}, {{msg.msg_data_def}})
{
	ARG_UNUSED({{user_data_name}});
	ARG_UNUSED({{msg.msg_data_name}});

	return -1;
}
{ % else % } __weak int{{msg.msg_cb_function_name}}({{user_data_def}})
{
	ARG_UNUSED({{user_data_name}});

	return -1;
}
{
	% endif %
}
{
	% endfor %
}

{% for msg in messages %
}
{
	% if msg.field %
}
static int{{msg.msg_read_function_name}}({{user_data_def}}, {{rpc_data_def}}, {{rpc_len_def}})
{
	int ret;
	{
		{
			msg.msg_data_type
		}
	}
	msg;

	msg = {{msg.pb_c_unpack_function_name}}(&{{protobuf_c_allocator_name}}, {{rpc_len_name}},
						{{rpc_data_name}});
	if (!msg) {
		LOG_ERR("{{ msg.name }}: Decode failed\n");
		return -EIO;
	}
#ifdef HAS_PROTO_MESSAGE_DUMP
	{{msg.msg_dump_function_name}}(msg);
#endif
	ret = {{msg.msg_cb_function_name}}({{user_data_name}}, msg);
	{{msg.pb_c_free_unpacked_function_name}}(msg, &{{protobuf_c_allocator_name}});
	return ret;
}
{
	% else %
}
static int{{msg.msg_read_function_name}}({{user_data_def}})
{
#ifdef HAS_PROTO_MESSAGE_DUMP
	{{msg.msg_dump_function_name}}();
#endif
	return {{msg.msg_cb_function_name}}({{user_data_name}});
}
{
	% endif %
}
{
	% endfor %
}

{% for msg in messages %
}
{
	% if msg.field %
}
int{{msg.msg_write_function_name}}({{user_data_def}}, {{msg.msg_data_def}})
{
	int ret;
	{
		{
			rpc_len_type
		}
	}
	{{rpc_len_name}};
	{
		{
			rpc_len_type
		}
	}
	hdr_len;
	uint8_t *out;

#ifdef HAS_PROTO_MESSAGE_DUMP
	{{msg.msg_dump_function_name}}({{msg_data_name}});
#endif
	{{rpc_len_name}} = {{msg.pb_c_get_size_function_name}}({{msg_data_name}});
	hdr_len = { {function_prefix} } header_size({{msg.id}}, {{rpc_len_name}});
	out = {{protobuf_c_allocator_name}}.alloc(NULL, {{rpc_len_name}} + hdr_len);
	if (!out) {
		return -ENOMEM;
	}
	{
		{
			function_prefix
		}
	}
	encode_header({{msg.id}}, {{rpc_len_name}}, out);
	{{msg.pb_c_pack_function_name}}({{msg_data_name}}, out + hdr_len);
	ret = {{platform_send_name}}({{user_data_name}}, out, {{rpc_len_name}} + hdr_len);
	{{protobuf_c_allocator_name}}.free(NULL, out);
	return ret;
}
{
	% else %
}
int{{msg.msg_write_function_name}}({{user_data_def}})
{
	{
		{
			rpc_len_type
		}
	}
	hdr_len;
	uint8_t out[8];

#ifdef HAS_PROTO_MESSAGE_DUMP
	{{msg.msg_dump_function_name}}();
#endif

	hdr_len = { {function_prefix} } header_size({{msg.id}}, 0);
	{
		{
			function_prefix
		}
	}
	encode_header({{msg.id}}, 0, out);
	return {{platform_send_name}}({{user_data_name}}, out, hdr_len);
}
{
	% endif %
}
{
	% endfor %
}

static void *zephyr_alloc(void *allocator_data, size_t size)
{
	return k_malloc(size);
}

static void zephyr_free(void *allocator_data, void *pointer)
{
	k_free(pointer);
}

static int varint_encode(uint64_t val, uint8_t *out)
{
	int i = 0;

	if (val <= 0x7F) {
		if (out) {
			*out = (uint8_t)val;
		}
		return 1;
	}
	while (val) {
		uint8_t temp = val & 0x7F;
		val >>= 7;
		if (val) {
			if (out) {
				out[i] = (temp | 0x80);
			}
		} else {
			if (out) {
				out[i] = temp;
			}
		}
		i++;
	}
	return i;
}

static int read_decode_varint(int fd, uint64_t *value)
{
	uint64_t result = 0;
	uint8_t bitpos = 0;
	uint8_t val;
	int ret;

	do {
		ret = zsock_recv(fd, &val, 1, ZSOCK_MSG_WAITALL);
		if (ret == 0) {
			return -EOF;
		}
		if (bitpos >= 63 && (val & 0xFE) != 0) {
			return -EOVERFLOW;
		}
		result |= (uint64_t)(val & 0x7F) << (uint64_t)bitpos;
		bitpos += 7;
	} while (val & 0x80);

	*value = result;
	return 0;
}

static int
{
	{
		function_prefix
	}
}
header_size(uint32_t rpc_id, size_t len)
{
	int header_size = 1;

	header_size += varint_encode(len, NULL);
	header_size += varint_encode(rpc_id, NULL);
	return header_size;
}

static int
{
	{
		function_prefix
	}
}
encode_header(uint32_t rpc_id, size_t len, uint8_t *out)
{
	int header_size = 1;

	out[0] = 0x00;
	header_size += varint_encode(len, out + header_size);
	header_size += varint_encode(rpc_id, out + header_size);

	return 0;
}

static int
{
	{
		function_prefix
	}
}
rpc_send(const struct device *dev, void *out, size_t len)
{
	struct {
		{
			function_prefix
		}
	} rpc_data *rpc_data = dev->data;

	zsock_send(rpc_data->socket, out, len, 0);

	return 0;
}

static int
{
	{
		function_prefix
	}
}
read_header(int fd, uint32_t *rpc_id, uint32_t *len)
{
	uint64_t val;
	uint8_t byte;
	int ret;

	do {
		ret = zsock_recv(fd, &byte, 1, ZSOCK_MSG_WAITALL);
	} while (ret == 0);

	if (ret < 0) {
		return ret;
	}

	if (byte != 0x00) {
		return -EIO;
	}

	ret = read_decode_varint(fd, &val);
	if (ret) {
		return ret;
	}
	*len = (uint32_t)val;

	ret = read_decode_varint(fd, &val);
	if (ret) {
		return ret;
	}
	*rpc_id = (uint32_t)val;

	return 0;
}

static int
{
	{
		function_prefix
	}
}
read_request({
	{
		user_data_type
	}
} {{user_data_name}})
{
	struct {
		{
			function_prefix
		}
	} rpc_data *rpc_data = { {user_data_name} } -> data;
	int ret;
	uint32_t msg_id;
	{
		{
			rpc_len_type
		}
	}
	{{rpc_len_name}};
	{
		{
			rpc_data_type
		}
	}
	{{rpc_data_name}} = NULL;

	LOG_DBG("Waiting for message");
	ret = { {function_prefix} } read_header(rpc_data->socket, &msg_id, &{{rpc_len_name}});
	if (ret) {
		LOG_ERR("Failed to read message header");
		return ret;
	}

	LOG_DBG("Reading message");
	if ({{rpc_len_name}}) {
		{{rpc_data_name}} = k_malloc({{rpc_len_name}});
		if (!{{rpc_data_name}}) {
			LOG_ERR("Failed to allocate message buffer");
			return -ENOMEM;
		}

		/* TODO: loop until we receive all the data */
		ret = zsock_recv(rpc_data->socket, {{rpc_data_name}}, {{rpc_len_name}},
				 ZSOCK_MSG_WAITALL);
		if (ret != {{rpc_len_name}}) {
			LOG_ERR("Failed to read message data");
			return -EIO;
		}
	}

	LOG_DBG("Handling message id %d", msg_id);
	switch (msg_id) {
		{% for msg in messages %
		}
	case {{ msg.id }}: {
		% if msg.field %
	}
		return {{msg.msg_read_function_name}}({{user_data_name}}, {{rpc_data_name}},
						      {{rpc_len_name}});
		{
			% else %
		}
		return {{msg.msg_read_function_name}}({{user_data_name}});
		{
			% endif %
		}
		{
			% endfor %
		}
	default:
		LOG_ERR("Unsupported message id %d", msg_id);
		return -ENOTSUP;
	}

	return 0;
}

int
{
	{
		function_prefix
	}
}
rpc_service(void *arg1, void *arg2, void *arg3)
{
	const struct device *dev = arg1;
	struct esphome_rpc_data *rpc_data = dev->data;
	int port = (int)arg2;

	int opt;
	socklen_t optlen = sizeof(int);
	int server_fd, r, ret;
	static struct sockaddr server_addr;
	char addrstr[INET6_ADDRSTRLEN];

	void *addrp;
	uint16_t *portp;

	if (IS_ENABLED(CONFIG_NET_IPV6)) {
		net_sin6(&server_addr)->sin6_family = AF_INET6;
		net_sin6(&server_addr)->sin6_addr = in6addr_any;
		net_sin6(&server_addr)->sin6_port = sys_cpu_to_be16(port);
	} else if (IS_ENABLED(CONFIG_NET_IPV4)) {
		net_sin(&server_addr)->sin_family = AF_INET;
		net_sin(&server_addr)->sin_addr.s_addr = htonl(INADDR_ANY);
		net_sin(&server_addr)->sin_port = sys_cpu_to_be16(port);
	} else {
		__ASSERT(false, "Neither IPv6 nor IPv4 are enabled");
	}

	r = zsock_socket(server_addr.sa_family, SOCK_STREAM, 0);
	if (r == -1) {
		LOG_DBG("socket() failed (%d)", errno);
		return errno;
	}

	server_fd = r;
	LOG_DBG("server_fd is %d", server_fd);

	ret = zsock_getsockopt(server_fd, IPPROTO_IPV6, IPV6_V6ONLY, &opt, &optlen);
	if (ret == 0) {
		if (opt) {
			LOG_INF("IPV6_V6ONLY option is on, turning it off.\n");

			opt = 0;
			ret = zsock_setsockopt(server_fd, IPPROTO_IPV6, IPV6_V6ONLY, &opt, optlen);
			if (ret < 0) {
				LOG_WRN("Cannot turn off IPV6_V6ONLY option\n");
			} else {
				LOG_INF("Sharing same socket between IPv6 and IPv4\n");
			}
		}
	}

	r = zsock_bind(server_fd, &server_addr, sizeof(server_addr));
	if (r == -1) {
		LOG_DBG("bind() failed (%d)", errno);
		zsock_close(server_fd);
		return errno;
	}

	if (server_addr.sa_family == AF_INET6) {
		addrp = &net_sin6(&server_addr)->sin6_addr;
		portp = &net_sin6(&server_addr)->sin6_port;
	} else {
		addrp = &net_sin(&server_addr)->sin_addr;
		portp = &net_sin(&server_addr)->sin_port;
	}

	zsock_inet_ntop(server_addr.sa_family, addrp, addrstr, sizeof(addrstr));
	LOG_DBG("bound to [%s]:%u", addrstr, ntohs(*portp));

	r = zsock_listen(server_fd, 1);
	if (r == -1) {
		LOG_DBG("listen() failed (%d)", errno);
		zsock_close(server_fd);
		return errno;
	}

	LOG_INF("ESPHOME server waits for a connection on "
		"port %d...\n",
		port);

	while (1) {
		struct sockaddr_in6 client_addr;
		socklen_t client_addr_len = sizeof(client_addr);

		rpc_data->socket =
			zsock_accept(server_fd, (struct sockaddr *)&client_addr, &client_addr_len);
		if (rpc_data->socket == -1) {
			LOG_DBG("accept() failed (%d)", errno);
			continue;
		}

		zsock_inet_ntop(server_addr.sa_family, addrp, addrstr, sizeof(addrstr));
		LOG_DBG("accepted connection from [%s]:%u", addrstr, ntohs(*portp));

		while (1) {
			ret = esphome_read_request(dev);
			if (!ret) {
				continue;
			} else {
				goto error;
			}
		}

	error:
		zsock_close(rpc_data->socket);
		LOG_INF("Connection from %s closed\n", addrstr);
	}

	return 0;
}
