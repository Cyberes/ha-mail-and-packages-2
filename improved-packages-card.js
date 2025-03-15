class PackageTrackerCard extends HTMLElement {
    setConfig(config) {
        this.config = config;

        // Variable that is hopefully outside the card refresh
        // scope to prevent the collapse from closing when it's refreshed.
        this.amazonCollapseOpen = false;
    }

    getCardSize() {
        return 3;
    }

    set hass(hass) {
        const amazonDelivered = parseInt(hass.states['sensor.amazon_delivered_count']?.state) || 0;
        const amazonArriving = (parseInt(hass.states['sensor.amazon_arriving_count']?.state) || 0)
            // Add the number of arriving packages to the delivered ones so we get a correct n/N number.
            + amazonDelivered;
        const amazonItems = (hass.states['sensor.amazon_arriving_count']?.attributes.items || []).join(', ');
        let amazonPackageStr;
        let amazonPackageItemsStr = "";
        if (amazonArriving === 0) {
            amazonPackageStr = `<div class="improved-packages-counts">no packages</div>`;
        } else {
            amazonPackageStr = `<div class="improved-packages-counts">${amazonDelivered}/${amazonArriving}</div>`;
            amazonPackageItemsStr = `
                <div class="improved-packages-amazon-items">
                    <button class="improved-packages-toggle-items-btn${this.amazonCollapseOpen ? ' open' : ''}">Incoming Items</button>
                    <div class="improved-packages-amazon-items-list${this.amazonCollapseOpen ? ' show' : ''}">${amazonItems}</div>
                </div>
            `;
        }

        const uspsDelivered = parseInt(hass.states['sensor.usps_delivered_count']?.state) || 0;
        const uspsArriving = (parseInt(hass.states['sensor.usps_arriving_count']?.state) || 0) + uspsDelivered;
        const uspsItems = (hass.states['sensor.usps_arriving_count']?.attributes.tracking_ids || []);
        let uspsTrackingUrl;
        if (uspsArriving === 0) {
            uspsTrackingUrl = 'https://informeddelivery.usps.com/box/pages/secure/DashboardAction_input.action';
        } else {
            const baseUrl = 'https://tools.usps.com/go/TrackConfirmAction?tLabels=';
            const trackingParam = uspsItems.join('%2C') + '%2C';
            uspsTrackingUrl = `${baseUrl}${trackingParam}`;
        }
        let uspsPackageStr
        if (uspsArriving === 0) {
            uspsPackageStr = `<div class="improved-packages-counts">no packages</div>`
        } else {
            uspsPackageStr = `<div class="improved-packages-counts">${uspsDelivered}/${uspsArriving}</div>`
        }

        const fedexDelivered = parseInt(hass.states['sensor.mail_fedex_delivered']?.state) || 0;
        const fedexArriving = (parseInt(hass.states['sensor.mail_fedex_delivering']?.state) || 0) + fedexDelivered;
        let fedexPackageStr
        if (fedexArriving === 0) {
            fedexPackageStr = `<div class="improved-packages-counts improved-packages-no-packages-str">no packages</div>`
        } else {
            fedexPackageStr = `<div class="improved-packages-counts">${fedexDelivered}/${fedexArriving}</div>`
        }

        const upsDelivered = parseInt(hass.states['sensor.mail_ups_delivered']?.state) || 0;
        const upsArriving = (parseInt(hass.states['sensor.mail_ups_delivering']?.state) || 0) + upsDelivered;
        let upsPackageStr
        if (upsArriving === 0) {
            upsPackageStr = `<div class="improved-packages-counts improved-packages-no-packages-str">no packages</div>`
        } else {
            upsPackageStr = `<div class="improved-packages-counts">${upsDelivered}/${upsArriving}</div>`
        }

        this.innerHTML = `
          <style>
            .improved-packages-card {
              padding: 16px;
              box-sizing: border-box;
            }

            .improved-packages-header {
              font-size: 20px;
              font-weight: 500;
              margin-bottom: 2px;
              text-align: center;
            }

            .improved-packages-service-container {
              display: flex;
              justify-content: space-around;
              flex-wrap: wrap;
              gap: 16px;
            }

            .improved-packages-service {
              flex: 1 1 100px;
              text-align: center;
            }

            .improved-packages-service-name {
              font-weight: 600;
              margin-bottom: 8px;
              font-size: 13pt;
            }

            .improved-packages-counts {
              font-size: 16px;
            }

            .improved-packages-no-packages-str {
              font-style: italic;
              color: var(--secondary-text-color);
            }

            .improved-packages-status-link {
              color: var(--primary-text-color);
              text-decoration: none;
            }

            .improved-packages-status-link.improved-packages-no-packages-str {
              color: var(--secondary-text-color);
            }

            .improved-packages-status-link:hover {
              color: var(--primary-color);
              text-decoration: underline;
              font-weight: bold;
            }

            .improved-packages-amazon-items {
              position: relative;
              display: block;
              width: 100%;
            }

            .improved-packages-amazon-items-list {
              position: absolute;
              top: 100%;
              left: 0;
              right: 0;
              transform: scaleY(0);
              transform-origin: top;
              background-color: var(--card-background-color);
              border: 1px solid var(--divider-color);
              border-radius: 4px;
              padding: 8px;
              width: 100%;
              overflow: hidden;
              transition: transform 0.1s ease, visibility 0.1s ease;
              visibility: hidden;
              text-align: center;
              box-sizing: border-box;
            }

            .improved-packages-amazon-items-list.show {
              transform: scaleY(1);
              visibility: visible;
            }

            .improved-packages-toggle-items-btn {
              background: none;
              border: none;
              color: var(--primary-color);
              cursor: pointer;
              font-size: 12px;
              padding: 0;
              text-decoration: underline;
              display: inline-flex;
              align-items: center;
            }

            .improved-packages-toggle-items-btn::after {
              content: "";
              display: inline-block;
              width: 0;
              height: 0;
              margin-left: 4px;
              vertical-align: middle;
              border-top: 4px solid;
              border-right: 4px solid transparent;
              border-left: 4px solid transparent;
              transition: transform 0.1s ease;
            }

            .improved-packages-toggle-items-btn.open::after {
              transform: rotate(180deg);
            }

            @media (min-width: 600px) {
              .improved-packages-service-container {
                flex-wrap: nowrap;
              }
            }
          </style>
            <ha-card>
                <div class="improved-packages-card">
                    ${
            this.config.title != null && this.config.title !== "undefined" && this.config.title !== "null"
                ? `<div class="improved-packages-header">${this.config.title}</div>`
                : ""
        }
                    <div style="margin-bottom:16px">
                        <div class="improved-packages-service">
                            <div class="improved-packages-service-name">Amazon</div>
                            <a href="https://www.amazon.com/gp/css/order-history" target="_blank" class="improved-packages-status-link ${amazonArriving === 0 ? 'improved-packages-no-packages-str' : ''}">${amazonPackageStr}</a>
                            ${amazonPackageItemsStr}
                        </div>
                    </div>
                    <div>
                        <div class="improved-packages-service-container">
                            <div class="improved-packages-service">
                                <div class="improved-packages-service-name">USPS</div>
                            <a href="${uspsTrackingUrl}" target="_blank" class="improved-packages-status-link ${uspsArriving === 0 ? 'improved-packages-no-packages-str' : ''}">${uspsPackageStr}</a>
                            </div>

                            <div class="improved-packages-service">
                                <div class="improved-packages-service-name">FedEx</div>
                                ${fedexPackageStr}
                            </div>

                            <div class="improved-packages-service">
                                <div class="improved-packages-service-name">UPS</div>
                                ${upsPackageStr}
                            </div>
                        </div>
                    </div>
                </div>
            </ha-card>
        `;

        const toggleItemsBtn = this.querySelector('.improved-packages-toggle-items-btn');
        const amazonItemsList = this.querySelector('.improved-packages-amazon-items-list');
        if (toggleItemsBtn && amazonItemsList) {
            toggleItemsBtn.addEventListener('click', () => {
                this.amazonCollapseOpen = !this.amazonCollapseOpen;
                amazonItemsList.classList.toggle('show', this.amazonCollapseOpen);
                toggleItemsBtn.classList.toggle('open', this.amazonCollapseOpen);
            });
        }
    }
}

customElements.define("improved-package-card", PackageTrackerCard);
