# ha-amazon-packages

_Home Assistant integration giving you a quick summary of what Amazon is delivering today._

Uses [alexdlaird/amazon-orders](https://github.com/alexdlaird/amazon-orders) to fetch order delivery dates instead of
parsing an IMAP inbox. It runs on an external server (it's not a Home Assistant integration) and sends data via MQTT
rather than as a because the dependencies require a specific version of Pillow.

Two-Step verification will interfere with the automated login to Amazon.

See `README.md` in `feeder/`.

## Install

1. `pip install -r requirements.txt`
2. `sudo apt-get install redis-server`
3. `sudo systemctl enable --now redis-server`
4. Start the systemd services. Examples are provided in `systemd/`

Add this to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Amazon Arriving Count"
      state_topic: "amazon-packages/amazon-arriving-count"
      json_attributes_topic: "amazon-packages/amazon-arriving-count/attributes"
      state_class: measurement
      unique_id: amazon_arriving_count
      unit_of_measurement: "packages"
    - name: "Amazon Delivered Count"
      state_topic: "amazon-packages/amazon-delivered-count"
      json_attributes_topic: "amazon-packages/amazon-delivered-count/attributes"
      state_class: measurement
      unique_id: amazon_delivered_count
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
