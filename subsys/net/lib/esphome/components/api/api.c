/*
 * Copyright (c) 2024 Alexandre Bailon
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <errno.h>
#include <stdio.h>

#include <rpc/esphome_rpc.h>
#include <esphome/esphome.h>
#include <esphome/components/components.h>

#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(ESPHome, CONFIG_ESPHOME_LOG_LEVEL);

void _esphome_get_version(const struct esphome_config *config, char *version, size_t len)
{
	int ret;

	ret = snprintf(version, len, "%d.%d", config->api_version_major, config->api_version_minor);
	if ((size_t)ret > len) {
		LOG_WRN("%s: the string has been troncated\n", __func__);
	}
}

int HelloRequestCb(const struct device *dev, HelloRequest *request)
{
	const struct esphome_config *config = dev->config;

	ARG_UNUSED(request);

	/* TODO: negotiate API version  */
	HelloResponse response = HELLO_RESPONSE__INIT;
	response.name = (char *)config->name;
	response.server_info = (char *)config->server_info;
	response.api_version_major = config->api_version_major;
	response.api_version_minor = config->api_version_minor;

	return HelloResponseWrite(dev, &response);
}

int ConnectRequestCb(const struct device *dev, ConnectRequest *request)
{
	const struct esphome_config *config = dev->config;
	ConnectResponse response = CONNECT_RESPONSE__INIT;

	if (config->password) {
		response.invalid_password = strcmp(config->password, request->password);
	}
	return ConnectResponseWrite(dev, &response);
}

int DeviceInfoRequestCb(const struct device *dev)
{
	char version[32];
	const struct esphome_config *config = dev->config;
	DeviceInfoResponse response = DEVICE_INFO_RESPONSE__INIT;

	if (config->password && strlen(config->password)) {
		response.uses_password = true;
	}
	response.name = (char *)config->name;
	_esphome_get_version(config, version, ARRAY_SIZE(version));
	response.esphome_version = version;
	response.compilation_time = (char *)config->compilation_time;
	response.project_name = (char *)config->project_name;
	response.project_version = (char *)config->project_version;
	response.model = (char *)config->model;
	response.manufacturer = (char *)config->manufacturer;

	return DeviceInfoResponseWrite(dev, &response);
}

int ListEntitiesRequestCb(const struct device *dev)
{
	STRUCT_SECTION_FOREACH(esphome_entity, entity) {
		entity->list_entity(dev, entity);
	}

	return ListEntitiesDoneResponseWrite(dev);
}

#ifdef CONFIG_ESPHOME_COMPONENT_SWITCH
int SwitchCommandRequestCb(const struct device *dev, SwitchCommandRequest *request)
{
	const struct device *switch_dev;
	SwitchStateResponse response = SWITCH_STATE_RESPONSE__INIT;

	switch_dev = find_device_entity_by_key(request->key);
	if (!switch_dev) {
		return -ENODEV;
	}

	esphome_switch_set_state(switch_dev, request->state);
	esphome_switch_get_state(switch_dev, &response.state);
	response.key = request->key;

	return SwitchStateResponseWrite(dev, &response);
}
#endif

#ifdef CONFIG_ESPHOME_COMPONENT_BUTTON
int ButtonCommandRequestCb(const struct device *dev, ButtonCommandRequest *request)
{
	const struct device *button_dev;

	button_dev = find_device_entity_by_key(request->key);
	if (!button_dev) {
		return -ENODEV;
	}

	return esphome_button_on_press(button_dev);
}
#endif

int LightCommandRequestCb(const struct device *dev, LightCommandRequest *request)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(request);

	return -ENOTSUP;
}

int SubscribeStatesRequestCb(const struct device *dev)
{
	ARG_UNUSED(dev);

	return 0;
}

int SubscribeHomeassistantServicesRequestCb(const struct device *dev)
{
	ARG_UNUSED(dev);

	return 0;
}

int SubscribeHomeAssistantStatesRequestCb(const struct device *dev)
{
	ARG_UNUSED(dev);

	return 0;
}

int PingRequestCb(const struct device *dev)
{
	return PingResponseWrite(dev);
}

int DisconnectRequestCb(const struct device *dev)
{
	DisconnectResponseWrite(dev);

	/* Error will force connection to close */
	return -ENOTCONN;
}
