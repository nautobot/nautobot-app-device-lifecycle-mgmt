# Frequently Asked Questions

## Can Device Lifecycle App integrate directly with Cisco End of Sale/Support `EoX` API?

Although not natively built in to the app at this time, this can be achieved by writing a Nautobot Job that interacts with the Cisco EoX API. 

## Does this app support integration with other vendor's hardware/software API's such as Juniper, Palo Alto, Aruba, Arista, etc...?

Not at this time, however, the maintainers would love to hear what you would like to see.  If you work at a networking vendor and would like to see your API's integrated to this app, please reach out to the maintainers.

## Why do I now see `Software Version (DLM)` in Devices and Inventory Items list views?

Previously, Devices and Inventory Items list views displayed duplicate Software Version columns one from Nautobot core and one provided by the Device Lifecycle Management (DLM) app.

To avoid confusion, the DLM-managed column is now explicitly labeled `Software Version (DLM)`.