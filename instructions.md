# Installing LGTM Enterprise on Google Cloud
## Preparation
Throughout this setup guide a few variables are used that are useful to set in advance. Specify an existing Google Cloud project that you want to deploy to, the zone to create any zonal resources in and a unique name of your choice for this deployment. If you are upgrading an existing installation, set these values to the same values used when LGTM was first set up.

Using the Cloud Shell command line, set values for the `project`, `zone` and `deployment` variables. For example:
```console
project="my-project"
zone="us-central1-a"
deployment="lgtm"
```

After you have done this, click _Start_ to to find out how to create or upgrade a control pool (step 1), or create or upgrade a worker group (step 2).

## Control pool
### Creating a new LGTM Enterprise control pool
You can create a new LGTM Enterprise control pool machine by using the `controller.py` template.
```console
gcloud deployment-manager deployments create --project "$project" --template=controller.py "$deployment" \
	--properties "zone:$zone,administrator-email:email@example.com,administrator-password:MySuperSecretPassword"
```

You can use the above command by copying and pasting it, editing the values for the initial administrator email and password. If you want to further customize your deployment, additional options can be added to the `--properties` flag:
* `zone` - The Google Cloud zone to create resources in.
* `virtual-machine-size` - The type of virtual machine to use. For information about the recommended size, see the [LGTM Enterprise installation guide](https://help.semmle.com/lgtm-enterprise/ops/lgtm-enterprise-LATEST-installation-guide.pdf).
* `data-disk-size-gb` - The data disk size for your LGTM Enterprise instance in gigabytes.
* `administrator-email` - The email address for the initial LGTM Enterprise administrator account.
* `administrator-password` - The password for the initial LGTM Enterprise administrator account. You should change this when you log in to LGTM Enterprise.
* `general-workers` - The number of general workers to run on the control pool.
* `on-demand-workers` - The number of on-demand workers to run on the control pool.
* `query-workers` - The number of query workers to run on the control pool.
* `worker-environment` - A JSON dictionary of environment variables to use for the workers.
* `manifest-password` - A password used to encrypt the LGTM manifest. If you don't specify one a password will be generated and stored in `/data/lgtm-releases/.manifest-password`.

You can obtain the IP address of the created LGTM Enterprise instance by running:
```
gcloud compute instances list --project "$project" --filter "name=$deployment"
```

### Upgrading the LGTM Enterprise control pool
When upgrading, you must use the same properties you used when you first deployed LGTM. You can see the properties you used previously by running:
```
gcloud deployment-manager manifests describe --project "$project" --deployment "$deployment" --format "value(config.content)" "$(gcloud deployment-manager deployments list --project "$project" --filter "name=$deployment" --format "value(manifest)")"
```

To update an existing LGTM Enterprise control pool the old virtual machine and OS disk must be removed.
```
gcloud compute instances delete --project "$project" --zone "$zone" "$deployment" --keep-disks data
```

Next the deployment must be removed, abandoning, but not removing the old resources.
```
gcloud deployment-manager deployments delete --project "$project" --delete-policy abandon "$deployment"
```

You can now upgrade the control pool by redeploying the template. If you specified any properties when the instance was first created, provide them again here.
```console
gcloud deployment-manager deployments create --project "$project" --template controller.py --properties zone:$zone "$deployment"
```

## Workers
Workers are managed as instance groups. All workers in an instance group are provisioned identically and groups can be scaled up and down depending on your needs. Decide a name for your worker group, or if you are upgrading an existing group use the same name you used to create the group.

Set the worker_credentials value by copying and pasting from the _Infrastructure > Worker management_ tab of the LGTM administration interface.

```console
worker_group="workers"
worker_credentials='worker-credentials: "H4sIAAAAAAAAAI...=="'
```

### Creating a new LGTM Enterprise worker group
You can create a new LGTM Enterprise worker group by using the `worker.py` template.
```console
gcloud deployment-manager deployments create --project "$project" --template=worker.py "$deployment-$worker_group" \
	--properties "zone:$zone,controller-deployment-name:$deployment,$worker_credentials"
```

You can use the above command by copying and pasting it. If you want to customize your deployment, you can add more settings to the `--properties` flag:
* `controller-deployment-name` - The deployment name for the LGTM Enterprise control pool that this worker group should connect to.
* `worker-credentials` - This should be copied from the administrator interface of the LGTM Enterprise control pool.
* `zone` - The Google Cloud zone to create resources in.
* `virtual-machine-size` - The type of virtual machine to use. For information about the recommended size, see the [LGTM Enterprise installation guide](https://help.semmle.com/lgtm-enterprise/ops/lgtm-enterprise-LATEST-installation-guide.pdf).
* `copies` - The number of copies of this worker to create.
* `general-workers` - The number of general workers to run on each machine in the group.
* `on-demand-workers` - The number of on-demand workers to run on each machine in the group.
* `query-workers` - The number of query workers to run on each machine in the group.
* `worker-environment` - A dictionary of environment variables to use for the workers.
* `manifest-password` - A password used to encrypt the LGTM manifest. If you don't specify one a password will be generated and stored in `/data/lgtm-releases/.manifest-password`.

### Upgrading an LGTM Enterprise worker group
When upgrading, you will probably want to use the same properties as when you first deployed LGTM. You can see the properties you used previously by running:
```
gcloud deployment-manager manifests describe --project "$project" --deployment "$deployment-$worker_group" --format "value(config.content)" "$(gcloud deployment-manager deployments list --project "$project" --filter "name=$deployment-$worker_group" --format "value(manifest)")"
```

You can now upgrade the worker group by redeploying the template and recreating the instances. If you specified any properties when the instance was first created, provide them again here.
```console
gcloud deployment-manager deployments update --project "$project" --template worker.py "$deployment-$worker_group" \
	--properties "zone:$zone,controller-deployment-name:$deployment,$worker_credentials"
gcloud compute instance-groups managed rolling-action replace --project "$project" --zone "$zone" "$deployment-$worker_group-group" --max-surge 0 --max-unavailable 100%
```

## Finish
That's it. LGTM Enterprise should now be installed or upgraded. Click _Finish_ below to close this tutorial.

If you need to open it again, you can always find the link to do so on the [LGTM Enterprise releases page](https://github.com/Semmle/lgtm-enterprise/releases/).
