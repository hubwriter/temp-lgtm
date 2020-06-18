import json

_IMAGE = open("image.txt", "r").read().strip()

def generate_config(context):
    zone = context.properties["zone"]
    region = zone.rsplit("-", 1)[0]
    deployment = context.env["deployment"]
    network_name = deployment + "-network"
    ip_name = deployment + "-ip"
    os_disk_name = deployment + "-os"
    data_disk_name = deployment + "-data"
    return {
        "resources": [
            # Network
            {
                "name": deployment + "-network",
                "type": "compute.v1.network",
                "properties": {
                    "autoCreateSubnetworks": True,
                },
            },
            # Firewall Rules for Controller
            {
                "name": deployment + "-controller",
                "type": "compute.v1.firewall",
                "properties": {
                    "network": "$(ref." + network_name + ".selfLink)",
                    "targetTags": [
                        "lgtm-controller",
                    ],
                    "allowed": [
                        {
                            "IPProtocol": "tcp",
                            "ports": [
                                22, # Administrative SSH access to the virtual machine.
                                80, # HTTP access for LGTM Enterprise's web interface.
                                443, # HTTPS access for LGTM Enterprise's web interface.
                                8000, # HTTP access for LGTM Enterprise's startup log.
                            ],
                        },
                    ],
                },
            },
            # Firewall Rules for Workers
            {
                "name": deployment + "-workers",
                "type": "compute.v1.firewall",
                "properties": {
                    "network": "$(ref." + network_name + ".selfLink)",
                    "targetTags": [
                        "lgtm-worker",
                    ],
                    "allowed": [
                        {
                            "IPProtocol": "tcp",
                            "ports": [
                                22, # Administrative SSH access to the virtual machine.
                                8000, # HTTP access for LGTM Enterprise's startup log.
                            ],
                        },
                    ],
                },
            },
            # Firewall Rule for Internal Communication
            {
                "name": deployment + "-internal",
                "type": "compute.v1.firewall",
                "properties": {
                    "network": "$(ref." + network_name + ".selfLink)",
                    "allowed": [
                        {
                            "IPProtocol": "all",
                        },
                    ],
                    "sourceRanges": [
                        "10.128.0.0/9",
                    ],
                },
            },
            # Static IP for Controller
            {
                "name": ip_name,
                "type": "compute.v1.address",
                "properties": {
                    "region": region,
                },
            },
            # OS Disk for Controller
            {
                "name": os_disk_name,
                "type": "compute.v1.disk",
                "properties": {
                    "zone": zone,
                    "type": "zones/" + zone + "/diskTypes/pd-ssd",
                    "sourceImage": _IMAGE,
                },
            },
            # Data Disk for Controller
            {
                "name": deployment + "-data",
                "type": "compute.v1.disk",
                "properties": {
                    "zone": zone,
                    "type": "zones/" + zone + "/diskTypes/pd-ssd",
                    "sizeGb": context.properties["data-disk-size-gb"],
                },
            },
            # Controller Instance
            {
                "name": deployment,
                "type": "compute.v1.instance",
                "properties": {
                    "zone": zone,
                    "machineType": "zones/" + zone + "/machineTypes/" + context.properties["virtual-machine-size"],
                    "hostname": deployment + "." + zone + ".c.semmle-oss-testing.internal",
                    "disks": [
                        {
                            "deviceName": "boot",
                            "type": "PERSISTENT",
                            "boot": True,
                            "autoDelete": True,
                            "source": "$(ref." + os_disk_name + ".selfLink)",
                        },
                        {
                            "deviceName": "data",
                            "type": "PERSISTENT",
                            "autoDelete": False,
                            "source": "$(ref." + data_disk_name + ".selfLink)",
                        },
                    ],
                    "tags": {
                        "items": [
                            "lgtm-controller",
                        ],
                    },
                    "networkInterfaces": [
                        {
                            "network": "$(ref." + network_name + ".selfLink)",
                            "accessConfigs": [
                                {
                                    "natIP": "$(ref." + ip_name + ".address)",
                                },
                            ],
                        },
                    ],
                    "metadata": {
                        "items": [
                            {
                                "key": "admin-email",
                                "value": context.properties["administrator-email"],
                            },
                            {
                                "key": "admin-password",
                                "value": context.properties["administrator-password"],
                            },
                            {
                                "key": "n-general",
                                "value": context.properties["general-workers"],
                            },
                            {
                                "key": "n-on-demand",
                                "value": context.properties["on-demand-workers"],
                            },
                            {
                                "key": "n-query",
                                "value": context.properties["query-workers"],
                            },
                            {
                                "key": "environment",
                                "value": json.dumps(context.properties["worker-environment"]),
                            },
                            {
                                "key": "manifest-password",
                                "value": context.properties["manifest-password"],
                            },
                        ],
                    },
                },
            },
        ],
    }
