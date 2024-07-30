/*
 * Copyright (c) 2024 Alexandre Bailon
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(ESPHome);

#include <zephyr/net/openthread.h>
#include <openthread/thread.h>

#include "service.h"
#include "srp.h"

static void on_thread_state_changed(otChangedFlags flags, struct openthread_context *ctx,
				    void *data)
{
	const struct device *dev = data;

	if (flags & OT_CHANGED_THREAD_ROLE) {
		switch (otThreadGetDeviceRole(ctx->instance)) {
		case OT_DEVICE_ROLE_CHILD:
		case OT_DEVICE_ROLE_ROUTER:
		case OT_DEVICE_ROLE_LEADER:
			ot_srp_init(dev);
			break;
		default:
			break;
		}
	}
}

static struct openthread_state_changed_cb ot_state_changed_cb = {
	.state_changed_cb = on_thread_state_changed,
};

int esphome_ot_init(const struct device *dev)
{
	struct openthread_context *ctx;
	int ret;

	static const struct device *const radio_dev = DEVICE_DT_GET(DT_CHOSEN(zephyr_ieee802154));

	printk("DTC: %s: %d\n", __func__, __LINE__);
	ot_state_changed_cb.user_data = (void *)dev;
	ctx = openthread_get_default_context();
	if (!ctx || !device_is_ready(radio_dev)) {
		LOG_ERR("Failed to find OpenThread device");
		return -ENODEV;
	}
	ret = openthread_state_changed_cb_register(ctx, &ot_state_changed_cb);
	if (ret) {
		LOG_ERR("Failed to initialize OpenThread state callback");
	}

	return ret;
}
