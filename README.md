# ha-mail-and-packages-2

_Home Assistant integration giving you a quick summary of what is being delivered today._

An improved and simplified version
of [moralmunky/Home-Assistant-Mail-And-Packages](https://github.com/moralmunky/Home-Assistant-Mail-And-Packages). I was
having endless issues, so I wrote my own package summary addon.

Runs on an external server (it's not a Home Assistant integration) and sends data via MQTT
because the dependencies require a very specific setup.

### Amazon

Uses [alexdlaird/amazon-orders](https://github.com/alexdlaird/amazon-orders) to fetch order delivery dates instead of
parsing an IMAP inbox.

Two-Step verification will interfere with the automated login to Amazon. Amazon seems to be pretty lenient regarding
bots.

### parcelsapp.com

[parcelsapp.com](https://parcelsapp.com) is used to track all other package providers. Create an account and subscribe
at [parcelsapp.com/dashboard](https://parcelsapp.com/dashboard).

### USPS

Set up Informed Delivery according
to [these instructions](https://github.com/moralmunky/Home-Assistant-Mail-And-Packages/wiki/Supported-Shipper-Requirements).
All package emails should go into one folder. The subject line of all USPS emails is parsed for tracking numbers.

USPS packages can be tracked via parcelsapp or using the official USPS tracking API. Controlled via the `--usps-mode`
arg and defaults to using parcelsapp.

The USPS tracking API requires a business account with valid `TRACKING` API scope access. In order to be eligible for
this scope, you must send 20 tracked packages then email `APISUPPORT@usps.gov` with your CRID 
(found [here](https://developers.usps.com/user)) and list of tracking numbers. You are building an online platform and
need access as part of the technology development phase (as long as you are shipping with USPS your use case is valid).
If you use Ground Advantage with a 3.5x5 package this should cost about $85.

Visit [developers.usps.com](https://developers.usps.com) and create a new app. You will need the `Consumer Key` and
`Consumer Secret` values.

Depending on the backlog, it can take a few weeks to a few months to get granted access.

## Install

1. `pip install -r requirements.txt`
2. `sudo apt-get install redis-server`
3. `sudo systemctl enable --now redis-server`
4. Enter your environment variables in `/etc/secrets/mail-and-packages`.
5. Start the systemd services.

Add this to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Amazon Arriving Count"
      state_topic: "mail-and-packages-2/amazon-arriving-count"
      json_attributes_topic: "mail-and-packages-2/amazon-arriving-count/attributes"
      state_class: measurement
      unique_id: amazon_arriving_count
      unit_of_measurement: "packages"
    - name: "Amazon Delivered Count"
      state_topic: "mail-and-packages-2/amazon-delivered-count"
      state_class: measurement
      unique_id: amazon_delivered_count
      unit_of_measurement: "packages"
    - name: "USPS Arriving Count"
      state_topic: "mail-and-packages-2/usps-arriving-count"
      json_attributes_topic: "mail-and-packages-2/usps-arriving-count/attributes"
      state_class: measurement
      unique_id: usps_arriving_count
      unit_of_measurement: "packages"
    - name: "USPS Delivered Count"
      state_topic: "mail-and-packages-2/usps-delivered-count"
      state_class: measurement
      unique_id: usps_delivered_count
      unit_of_measurement: "packages"
```

### Dashboard Card

An improved dashboard card is included.

```yaml
type: custom:improved-package-card
```

To add a title:

```yaml
title: Incoming Packages
```