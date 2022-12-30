# External Interactions

## External System Integrations

### From the App to Other Systems

### From Other Systems to the App

## Nautobot REST API endpoints

### Hardware Lifecycle Management API Examples

![](../images/lcm_hardware_api_view.png)

#### REST API Example 1

Gather hardware notices that will be end of support by the end of 2021

```shell
curl "http://$NBHOST/api/plugins/device-lifecycle/hardware/?end_of_support__lte=2021-12-31" \
-X GET \
-H  "accept: application/json" \
-H  "Authorization: Token $TOKEN" | json_pp
```

#### REST API Example 2

Gather hardware notices that are currently expired.

!!! note
    The `expired` flag will honor `end_of_support` if the field exist for the record. If the field does not exist, `end_of_sale` will be used as the expired field.

```shell
curl "http://$NBHOST/api/plugins/device-lifecycle/hardware/?expired=true" \
-X GET \
-H  "accept: application/json" \
-H  "Authorization: Token $TOKEN" | json_pp
```

### GraphQL Examples

![](../images/lcm_hardware_graphql.png)
