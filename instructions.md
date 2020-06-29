# Installing LGTM Enterprise on Google Cloud
## Preparation
Throughout this setup guide a few variables are used that are useful to set in advance. Set the Google Cloud project you want to deploy to, the zone to create any zonal resources in and a unique name for this deployment. If you are upgrading an existing installation, set these values to the same values used when LGTM was first set up.

```console
project="my-project"
zone="us-central1-a"
deployment="lgtm"
```

## Controller
### Creating a New LGTM Enterprise Controller
A new LGTM Enterprise controller machine can be created using the `controller.py` template.
```console
gcloud deployment-manager deployments create --project "$project" --template=controller.py "$deployment" \
	--properties "zone:$zone,administrator-email:email@example.com,administrator-password:MySuperSecretPassword"
```

The `--properties` flag can be used to provide a variety of options to customize your deployment:
* `zone` - The Google Cloud zone to create resources in.
* `virtual-machine-size` - The type of virtual machine to use.
* `data-disk-size-gb` - The data disk size for your LGTM Enterprise instance in gigabytes.
* `administrator-email` - The email address for the initial LGTM Enterprise administrator account.
* `administrator-password` - The password for the initial LGTM Enterprise administrator account. It is recommended that you change this after the instance has booted.
* `general-workers` - The number of general workers to run on the controller.
* `on-demand-workers` - The number of on-demand workers to run on the controller.
* `query-workers` - The number of query workers to run on the controller.
* `worker-environment` - A JSON dictionary of environment variables to use for the workers.
* `manifest-password` - A password used to encrypt the LGTM manifest. If not specified a password will be generated and stored in `/data/lgtm-releases/.manifest-password`.

### Upgrading an Existing LGTM Enterprise Controller
When upgrading, it is important that you use the same properties as when you first deployed LGTM. You can see the properties you used previously by running:
```
gcloud deployment-manager manifests describe --project "$project" --deployment "$deployment" --format "value(config.content)" "$(gcloud deployment-manager deployments list --project "$project" --filter "name=$deployment" --format "value(manifest)")"
```

To update an existing LGTM Enterprise controller the old virtual machine and OS disk must be removed.
```
gcloud compute instances delete --project "$project" --zone "$zone" "$deployment" --keep-disks data
```

Next the deployment must be removed, abandoning, but not removing the old resources.
```
gcloud deployment-manager deployments delete --project "$project" --delete-policy abandon "$deployment"
```

The controller can then be upgraded by re-deploying the template. If you specified any properties when the instance was first created, provide them again here.
```console
gcloud deployment-manager deployments create --project "$project" --template controller.py --properties zone:$zone "$deployment"
```

## Workers
Workers are managed as instance groups. All workers in an instance group are provisioned identically and groups can be scaled up and down depending on your needs. Decide a name for your worker group, or if you are upgrading an existing group use the same name you used to create the group.

```console
worker_group="workers"
worker_credentials='worker-credentials: "H4sIAAAAAAAAAI...=="'
```

### Creating a New LGTM Enterprise Worker Group
A new LGTM Enterprise worker group can be created using the `worker.py` template.
```console
gcloud deployment-manager deployments create --project "$project" --template=worker.py "$deployment-$worker_group" \
	--properties "zone:$zone,controller-deployment-name:$deployment,$worker_credentials"
```

The `--properties` flag can be used to provide a variety of options to customize your deployment:
* `controller-deployment-name` - The deployment name for the LGTM Enterprise controller deployment that this worker group should connect to.
* `worker-credentials` - This should be copied from the administrator interface of the LGTM Enterprise controller.
* `zone` - The Google Cloud zone to create resources in.
* `virtual-machine-size` - The type of virtual machine to use.
* `copies` - The number of copies of this worker to create.
* `general-workers` - The number of general workers to run on each machine in the group.
* `on-demand-workers` - The number of on-demand workers to run on each machine in the group.
* `query-workers` - The number of query workers to run on each machine in the group.
* `worker-environment` - A dictionary of environment variables to use for the workers.
* `manifest-password` - A password used to encrypt the LGTM manifest. If not specified a password will be generated and stored in `/data/lgtm-releases/.manifest-password`.

### Upgrading an Existing LGTM Enterprise Worker Group
When upgrading, you likely want to use the same properties as when you first deployed LGTM. You can see the properties you used previously by running:
```
gcloud deployment-manager manifests describe --project "$project" --deployment "$deployment-$worker_group" --format "value(config.content)" "$(gcloud deployment-manager deployments list --project "$project" --filter "name=$deployment-$worker_group" --format "value(manifest)")"
```

The controller can then be upgraded by re-deploying the template. If you specified any properties when the instance was first created, provide them again here.
```console
gcloud deployment-manager deployments update --project "$project" --template worker.py "$deployment-$worker_group" \
	--properties "zone:$zone,controller-deployment-name:$deployment,$worker_credentials"
```
