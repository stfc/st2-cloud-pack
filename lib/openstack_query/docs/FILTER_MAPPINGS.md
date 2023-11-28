# Filter Mappings
This document is a reference to the allowed preset-property pairs that `where()` filter method can take for each
Query type


# Filter Mappings Reference

## ServerQuery
valid server-side filters documented here:
[openstacsdk-ref](https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html), [openstack-api-ref](https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request)

### `QueryPresetsGeneric.EQUAL_TO` preset:

| Preset   | Property(ies)                                                        | server-side key-word args (if any) |
|----------|----------------------------------------------------------------------|------------------------------------|
| EQUAL_TO | ServerProperties.USER_ID                                             | `{"user_id": <value-given>}`       |
| EQUAL_TO | ServerProperties.SERVER_ID                                           | `{"uuid": <value-given>}`          |
| EQUAL_TO | ServerProperties.SERVER_NAME                                         | `{"hostname": <value-given>}`      |
| EQUAL_TO | ServerProperties.SERVER_DESCRIPTION                                  | `{"description": <value-given>}`   |
| EQUAL_TO | ServerProperties.SERVER_STATUS                                       | `{"status": <value-given>}`        |
| EQUAL_TO | ServerProperties.SERVER_CREATION_DATE                                | `{"created_at": <value-given>}`    |
| EQUAL_TO | ServerProperties.FLAVOR_ID                                           | `{"flavor": <value-given>}`        |
| EQUAL_TO | ServerProperties.IMAGE_ID                                            | `{"image": <value-given>}`         |
| EQUAL_TO | ServerProperties.PROJECT_ID                                          | `{"project_id": <value-given>}`    |
| EQUAL_TO | all other ServerProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |


### `QueryPresetsGeneric.ANY_IN` preset:

Same as `EQUAL_TO` - since it `ANY_IN` just runs multiple `EQUAL_TO` queries


### Other `QueryPresetsGeneric` presets:

| Preset       | Property(ies)                                                  | server-side key-word args (if any) |
|--------------|----------------------------------------------------------------|------------------------------------|
| NOT_EQUAL_TO | All ServerProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |
| NOT_ANY_IN   | All ServerProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |


### `QueryPresetsDateTime` presets:

*see `/openstack_query/time_utils.py` - for `convert-to-timestamp` method details*

| Preset                   | Property(ies)                             | server-side key-word args (if any)                                        |
|--------------------------|-------------------------------------------|---------------------------------------------------------------------------|
| YOUNGER_THAN_OR_EQUAL_TO | ServerProperties.SERVER_LAST_UPDATED_DATE | `{"changes-since": convert-to-timestamp(days, hours, minutes, seconds)}`  |
| YOUNGER_THAN_OR_EQUAL_TO | ServerProperties.SERVER_CREATION_DATE     | None                                                                      |
| OLDER_THAN_OR_EQUAL_TO   | ServerProperties.SERVER_LAST_UPDATED_DATE | `{"changes-before": convert-to-timestamp(days, hours, minutes, seconds)}` |
| OLDER_THAN_OR_EQUAL_TO   | ServerProperties.SERVER_CREATION_DATE     | None                                                                      |
| YOUNGER_THAN             | ServerProperties.SERVER_LAST_UPDATED_DATE | None                                                                      |
| YOUNGER_THAN             | ServerProperties.SERVER_CREATION_DATE     | None                                                                      |
| OLDER_THAN               | ServerProperties.SERVER_LAST_UPDATED_DATE | None                                                                      |
| OLDER_THAN               | ServerProperties.SERVER_CREATION_DATE     | None                                                                      |

### `QueryPresetsString` presets:

| Preset        | Property(ies)                | server-side key-word args (if any) |
|---------------|------------------------------|------------------------------------|
| MATCHES_REGEX | ServerProperties.SERVER_NAME | None                               |
| MATCHES_REGEX | ServerProperties.ADDRESSES   | None                               |


## UserQuery
valid server-side filters documented here:
[openstacsdk-ref](https://docs.openstack.org/openstacksdk/latest/user/proxies/identity_v3.html),
[openstack-api-ref](https://docs.openstack.org/api-ref/identity/v3/#list-users)

### `QueryPresetsGeneric.EQUAL_TO` preset:

| Preset   | Property(ies)                                                      | server-side key-word args (if any) |
|----------|--------------------------------------------------------------------|------------------------------------|
| EQUAL_TO | UserProperties.USER_DOMAIN_ID                                      | `{"domain_id": <value-given>}`     |
| EQUAL_TO | UserProperties.USER_NAME                                           | `{"name": <value-given>}`          |
| EQUAL_TO | UserProperties.USER_ID                                             | `{"id": <value-given>}`            |
| EQUAL_TO | all other UserProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |


### `QueryPresetsGeneric.ANY_IN` preset:

Same as `EQUAL_TO` - since it `ANY_IN` just runs multiple `EQUAL_TO` queries


### Other `QueryPresetsGeneric` presets:

| Preset       | Property(ies)                                                | server-side key-word args (if any) |
|--------------|--------------------------------------------------------------|------------------------------------|
| NOT_EQUAL_TO | All UserProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |
| NOT_ANY_IN   | All UserProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |


### `QueryPresetsString` presets:

| Preset        | Property(ies)             | server-side key-word args (if any) |
|---------------|---------------------------|------------------------------------|
| MATCHES_REGEX | UserProperties.USER_EMAIL | None                               |
| MATCHES_REGEX | UserProperties.USER_NAME  | None                               |


## ProjectQuery
valid server-side filters documented here:
[openstacsdk-ref](https://docs.openstack.org/openstacksdk/latest/user/proxies/identity_v3.html),
[openstack-api-ref](https://docs.openstack.org/api-ref/identity/v3/index.html#list-projects)

### `QueryPresetsGeneric.EQUAL_TO` preset:

| Preset   | Property(ies)                                                         | server-side key-word args (if any) |
|----------|-----------------------------------------------------------------------|------------------------------------|
| EQUAL_TO | ProjectProperties.PROJECT_ID                                          | `{"id": <value-given>}`            |
| EQUAL_TO | ProjectProperties.PROJECT_DOMAIN_ID                                   | `{"domain_id": <value-given>}`     |
| EQUAL_TO | ProjectProperties.PROJECT_IS_ENABLED                                  | `{"is_enabled": <value-given>}`    |
| EQUAL_TO | ProjectProperties.PROJECT_IS_DOMAIN                                   | `{"is_domain": <value-given>}`     |
| EQUAL_TO | ProjectProperties.PROJECT_NAME                                        | `{"name": <value-given>}`          |
| EQUAL_TO | ProjectProperties.PROJECT_PARENT_ID                                   | `{"parent_id": <value-given>}`     |
| EQUAL_TO | all other ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |

### `QueryPresetsGeneric.ANY_IN` preset:

Same as `EQUAL_TO` - since it `ANY_IN` just runs multiple `EQUAL_TO` queries

### `QueryPresetsGeneric.NOT_EQUAL_TO` presets:

| Preset       | Property(ies)                                                         | server-side key-word args (if any)  |
|--------------|-----------------------------------------------------------------------|-------------------------------------|
| NOT_EQUAL_TO | ProjectProperties.PROJECT_IS_ENABLED                                  | `{"is_enabled": not <value-given>}` |
| NOT_EQUAL_TO | ProjectProperties.PROJECT_IS_DOMAIN                                   | `{"is_domain": not <value-given>}`  |
| NOT_EQUAL_TO | all other ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                                |

### `QueryPresetsGeneric.NOT_ANY_IN` preset:

| Preset     | Property(ies)                                                         | server-side key-word args (if any) |
|------------|-----------------------------------------------------------------------|------------------------------------|
| NOT_ANY_IN | all other ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |


### `QueryPresetsString` presets:

| Preset        | Property(ies)                         | server-side key-word args (if any) |
|---------------|---------------------------------------|------------------------------------|
| MATCHES_REGEX | ProjectProperties.PROJECT_NAME        | None                               |
| MATCHES_REGEX | ProjectProperties.PROJECT_DESCRIPTION | None                               |

## FlavorQuery
valid server-side filters documented here:
[openstacsdk-ref](https://docs.openstack.org/openstacksdk/latest/user/proxies/compute.html),
[openstack-api-ref](https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#show-flavor-details)

### `QueryPresetsGeneric.EQUAL_TO` preset:

| Preset   | Property(ies)                                                         | server-side key-word args (if any) |
|----------|-----------------------------------------------------------------------|------------------------------------|
| EQUAL_TO | ProjectProperties.FLAVOR_IS_PUBLIC                                    | `{"id": <value-given>}`            |
| EQUAL_TO | all other ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |

### `QueryPresetsGeneric.ANY_IN` preset:

| Preset | Property(ies)                                                   | server-side key-word args (if any) |
|--------|-----------------------------------------------------------------|------------------------------------|
| ANY_IN | all ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |

### `QueryPresetsGeneric.NOT_EQUAL_TO` preset:

| Preset       | Property(ies)                                                         | server-side key-word args (if any) |
|--------------|-----------------------------------------------------------------------|------------------------------------|
| NOT_EQUAL_TO | ProjectProperties.FLAVOR_IS_PUBLIC                                    | `{"id": not <value-given>}`        |
| NOT_EQUAL_TO | all other ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |

### `QueryPresetsGeneric.NOT_ANY_IN` preset:

| Preset     | Property(ies)                                                   | server-side key-word args (if any) |
|------------|-----------------------------------------------------------------|------------------------------------|
| NOT_ANY_IN | all ProjectProperties <br/>(see [PROPERTIES.md](PROPERTIES.md)) | None                               |

### `QueryPresetsInteger.LESS_THAN_OR_EQUAL_TO`

| Preset                | Property(ies)                     | server-side key-word args (if any) |
|-----------------------|-----------------------------------|------------------------------------|
| LESS_THAN_OR_EQUAL_TO | ProjectProperties.FLAVOR_DISK     | `{"minDisk": int(<value-given>})`  |
| LESS_THAN_OR_EQUAL_TO | ProjectProperties.FLAVOR_RAM      | `{"minRam": int(<value-given>})`   |
| LESS_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_EPHEMERAL | None                               |
| LESS_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_SWAP      | None                               |
| LESS_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_VCPU      | None                               |


### Other `QueryPresetInteger` presets

| Preset                   | Property(ies)                     | server-side key-word args (if any) |
|--------------------------|-----------------------------------|------------------------------------|
| LESS_THAN                | FlavorProperties.FLAVOR_EPHEMERAL | None                               |
| LESS_THAN                | FlavorProperties.FLAVOR_SWAP      | None                               |
| LESS_THAN                | FlavorProperties.FLAVOR_VCPU      | None                               |
| GREATER_THAN             | FlavorProperties.FLAVOR_EPHEMERAL | None                               |
| GREATER_THAN             | FlavorProperties.FLAVOR_SWAP      | None                               |
| GREATER_THAN             | FlavorProperties.FLAVOR_VCPU      | None                               |
| GREATER_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_EPHEMERAL | None                               |
| GREATER_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_SWAP      | None                               |
| GREATER_THAN_OR_EQUAL_TO | FlavorProperties.FLAVOR_VCPU      | None                               |
