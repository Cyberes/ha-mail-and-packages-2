USPS packages can be tracked via parcelsapp or using the official USPS tracking API. Controlled via the `--usps-mode`
arg and defaults to using parcelsapp.

The USPS tracking API requires a business account with valid `TRACKING` API scope access. In order to be eligible for
this scope, you must send 20 tracked packages then email `APISUPPORT@usps.gov` with your CRID
(found [here](https://developers.usps.com/user)) and list of tracking numbers. You are building an online platform and
need access as part of the technology development phase (as long as you are shipping with USPS your use case is valid).
If you use Ground Advantage with a 3.5x5 package this should cost about $85.

Visit [developers.usps.com](https://developers.usps.com) and create a new app. You will need the `Consumer Key` and
`Consumer Secret` values.

You'll also access info via the [Business Customer Gateway](https://gateway.usps.com/eAdmin/view/signin).

Depending on the backlog, it can take a few weeks to a few months to get granted access.

The native USPS API may serve more up to date data versus parcelsapp. But parcelsapp is good enough.
