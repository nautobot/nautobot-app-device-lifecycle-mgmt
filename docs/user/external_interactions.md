# External Interactions
There are various integrations that you may want to incorporate into the Device Lifecycle plug-in.  This page will rpvide references to officially supported external integrations.  This is not meant to limit what is supported, but rather is meant as a place to go for integration needs for external systems (such as NIST for example...).

## External System Integrations
* [NIST API Developer Documentation](https://nvd.nist.gov/developers/start-here#:~:text=Request%20an%20API%20Key%201%20On%20the%20API,above%20for%20an%20email%20from%20nvd-noreply%40nist.gov.%20More%20items)
* [NIST Request an API key](https://nvd.nist.gov/developers/request-an-api-key)
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
