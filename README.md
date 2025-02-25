# ha-mail-and-packages-2

_Home Assistant integration giving you a quick summary of what is being delivered today._

An improved and simplified version
of [moralmunky/Home-Assistant-Mail-And-Packages](https://github.com/moralmunky/Home-Assistant-Mail-And-Packages). I was
having endless issues, so I wrote my own package summary addon.

### Amazon

Uses [alexdlaird/amazon-orders](https://github.com/alexdlaird/amazon-orders) to fetch order delivery dates instead of
parsing an IMAP inbox. It runs on an external server (it's not a Home Assistant integration) and sends data via MQTT
because the dependencies require a specific version of Pillow.

Two-Step verification will interfere with the automated login to Amazon.

See `README.md` in `feeder/`.

### USPS

Set up Informed Delivery according
to [these instructions](https://github.com/moralmunky/Home-Assistant-Mail-And-Packages/wiki/Supported-Shipper-Requirements).
All package emails should go into one folder. The subject line of all USPS emails is parsed for delivery status and
arrival date.

## Install

1. `pip install -r requirements.txt`
2. `sudo apt-get install redis-server xvfb`
3. `sudo systemctl enable --now redis-server`
4. Start the systemd services. Examples are provided in `systemd/`

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