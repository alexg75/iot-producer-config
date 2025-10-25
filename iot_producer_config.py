from kasa import Credentials, Device, DeviceConfig, DeviceFamily, DeviceType, Discover
from kasa.iot import IotDevice
import asyncio
import json
import logger
import tapo_device
from tapo import ApiClient
import genericMessageProducer

log = logger.setup_logger("iot_producer_config")

TOPIC_NAME = "config"

async def scan_devices():
    log.info("15 CB25 9DX IOT")
    log.info("Scanning devices for config")
    alias_to_ip = {} 
    found_devices = await Discover.discover()    
    log.info(found_devices)
    for device in  found_devices.values():
        log.info(f"{device}-{device.model}")
        if device.model == 'H100':
            log.info("TAPO HUB")
            client = tapo_device.get_client()
            hub = await client.h100(device.host)
            device_info = await hub.get_device_info()
            log.info(f"{device.host}: {device_info.nickname}")
            alias_to_ip[device_info.nickname] = device.host
        elif device.model == 'HS110':            
            # log.info(f"device.alias: {device.alias}-{DeviceType.Plug.value}")
            if device.alias is not None:
                log.info("TP-LINK PLUG")
                log.info(f"{device.host}: {device.alias}")
                alias_to_ip[device.alias] = device.host
        elif device.model == 'P100':
            log.info("TAPO PLUG")
            client = tapo_device.get_client()
            plug = await client.p100(device.host)
            device_info = await plug.get_device_info()
            log.info(f"{device.host}: {device_info.nickname}")
            alias_to_ip[device_info.nickname] = device.host            
        else:
            alias_to_ip[device.alias] = device.host
            log.error(f"Uknown device. Model: {device.model}, Alias: {device.alias}, Host: {device.host}")

    log.info("Configuration generated")    
    try:
      genericMessageProducer.publish(TOPIC_NAME, alias_to_ip)
    except Exception as e:
        log.error(e)
    log.info(f"Configuration pushed to {TOPIC_NAME}")    

asyncio.run(scan_devices())


