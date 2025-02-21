## Install

1. `pip install -r requirements.txt`
2. `sudo apt-get install redis-server`
3. `sudo systemctl enable --now redis-server`
4. Start the systemd services. Examples are provided in `systemd/`

Add this to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name:                  "Amazon Arriving Count"
      state_topic:           "amazon-packages/amazon-arriving-count"
      json_attributes_topic: "amazon-packages/amazon-arriving-count/attributes"
      state_class:           measurement
      unique_id:             amazon_arriving_count
      unit_of_measurement:   "packages"

sensor:
  - name:                  "Amazon Delivered Count"
    state_topic:           "amazon-packages/amazon-delivered-count"
    json_attributes_topic: "amazon-packages/amazon-delivered-count/attributes"
    state_class:           measurement
    unique_id:             amazon_delivered_count
    unit_of_measurement:   "packages"
  - platform: template
    sensors:
      amazon_packages_items:
        friendly_name: "Amazon Package Details"
        unique_id: amazon_package_items
        value_template: >
          {% set attrs = state_attr('sensor.amazon_arriving_count', 'items') %}
          {{ attrs | join(', ') if attrs else 'No packages' }}

```
