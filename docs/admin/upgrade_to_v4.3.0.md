## Version-Specific Steps

### Migrating to DLM App Version 4.3.0

The NIST CVE Search Job now sets a CVE's CVSS Base Score and Severity from the highest CVSS version in its NIST data, and records that version's vector in the new CVSS Vector field. The Job only updates an existing CVE when NIST has modified the CVE record, so existing CVEs keep their previous values and an empty CVSS Vector after upgrading.

After upgrading and restarting the Nautobot services, run the ``NIST - Software CVE Search`` Job once with **Force CVE Updates** checked. This updates every CVE that NIST returns for your Software Versions from its NIST record. Later runs can leave the option unchecked.

!!! note
    A forced run makes the same NIST API calls as a normal run, but it also saves every returned CVE, so it can take longer to complete.
