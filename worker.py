import json
import random
import string

_IMAGE = open("image.txt", "r").read().strip()

def generate_config(context):
    zone = context.properties["zone"]
    region = zone.rsplit("-", 1)[0]
    controller_deployment = context.properties["controller-deployment-name"]
    deployment = context.env["deployment"]
    network_name = controller_deployment + "-network"
    instance_template_id = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    instance_template_name = deployment + "-template-" + instance_template_id
    instance_group_manager_name = deployment + "-group"
    return {
        "resources": [
            # Worker Group Instance Template
            {
                "name": instance_template_name,
                "type": "compute.v1.instanceTemplate",
                "properties": {
                    "properties": {
                        "zone": zone,
                        "machineType": context.properties["virtual-machine-size"],
                        "disks": [
                            {
                                "deviceName": "boot",
                                "type": "PERSISTENT",
                                "boot": True,
                                "autoDelete": True,
                                "initializeParams": {
                                    "diskType": "pd-ssd",
                                    "sourceImage": _IMAGE,
                                },
                            },
                        ],
                        "tags": {
                            "items": [
                                "lgtm-worker",
                            ],
                        },
                        "networkInterfaces": [
                            {
                                "network": "projects/" + context.env["project"] + "/global/networks/" + network_name,
                                "accessConfigs": [
                                    {
                                        "type": "ONE_TO_ONE_NAT",
                                    },
                                ],
                            },
                        ],
                        "metadata": {
                            "items": [
                                {
                                    "key": "controller-hostname",
                                    "value": controller_deployment + "." + zone + ".c." + context.env["project"] + ".internal",
                                },
                                {
                                    "key": "worker-credentials",
                                    "value": context.properties["worker-credentials"],
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
            },
            # Worker Group Instance Group Manager
            {
                "name": instance_group_manager_name,
                "type": "compute.v1.instanceGroupManager",
                "properties": {
                    "zone": zone,
                    "baseInstanceName": deployment,
                    "instanceTemplate": "$(ref." + instance_template_name + ".selfLink)",
                    "targetSize": context.properties["copies"],
                },
            },
        ],
    }
