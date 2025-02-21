# ha-amazon-packages

_Home Assistant integration giving you a quick summary of what Amazon is delivering today. _

Uses [alexdlaird/amazon-orders](https://github.com/alexdlaird/amazon-orders) to fetch order delivery dates instead of
parsing an IMAP inbox. It runs on an external server (it's not a Home Assistant integration) and sends data via MQTT
rather than as a because the dependencies require a specific version of Pillow.

Two-Step verification will interfere with the automated login to Amazon.

See `README.md` in `feeder/`.

Dashboard card:

```yaml
type: markdown
content: >
  **Delivered:** {{ states('sensor.amazon_delivered_count') | int }}/{{
  states('sensor.amazon_arriving_count') | int }}


  **Items:** {{ states('sensor.amazon_packages_items') }}


  [Orders Page](https://www.amazon.com/gp/css/order-history)
```

#### Supported Senders:

- [x] Amazon
- [ ] USPS
- [ ] UPS
- [ ] Fedex