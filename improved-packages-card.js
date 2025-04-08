class PackageTrackerCard extends HTMLElement {
    set hass(hass) {
        const amazonDeliveredCount = parseInt(hass.states['sensor.amazon_delivered_count']?.state) || 0;
        const amazonTotalCount = (parseInt(hass.states['sensor.amazon_arriving_count']?.state) || 0)
            // Add the number of arriving packages to the delivered ones so we get a correct n/N number.
            + amazonDeliveredCount;
        const amazonItems = (hass.states['sensor.amazon_arriving_count']?.attributes.items || []).join(', ');
        let amazonPackageStr;
        let amazonPackageItemsHtml = "";
        if (amazonTotalCount === 0) {
            amazonPackageStr = `no packages`;
        } else {
            amazonPackageStr = `${amazonDeliveredCount}/${amazonTotalCount}`;
            amazonPackageItemsHtml = `
                <div class="improved-packages-amazon-items">
                    <button class="improved-packages-toggle-items-btn${this.amazonCollapseOpen ? ' open' : ''}">Incoming Items</button>
                    <div class="improved-packages-amazon-items-list${this.amazonCollapseOpen ? ' show' : ''}">${amazonItems}</div>
                </div>
            `;
        }

        const uspsDeliveredCount = parseInt(hass.states['sensor.usps_delivered_count']?.state) || 0;
        const uspsTotalCount = (parseInt(hass.states['sensor.usps_arriving_count']?.state) || 0) + uspsDeliveredCount;
        const uspsTrackingIds = (hass.states['sensor.usps_arriving_count']?.attributes.tracking_ids || []);
        let uspsTrackingUrl, uspsTrackingStr;
        if (uspsTotalCount === 0) {
            uspsTrackingUrl = 'https://informeddelivery.usps.com/box/pages/secure/DashboardAction_input.action';
            uspsTrackingStr = `no packages`
        } else {
            const baseUrl = 'https://tools.usps.com/go/TrackConfirmAction?tLabels=';
            const trackingParam = uspsTrackingIds.join('%2C') + '%2C';
            uspsTrackingUrl = `${baseUrl}${trackingParam}`;
            uspsTrackingStr = `${uspsDeliveredCount}/${uspsTotalCount}`;
        }

        const fedexDeliveredCount = parseInt(hass.states['sensor.mail_fedex_delivered_count']?.state) || 0;
        const fedexTotalCount = (parseInt(hass.states['sensor.mail_fedex_arriving_count']?.state) || 0) + fedexDeliveredCount;
        const fedexTrackingIds = (hass.states['sensor.mail_fedex_arriving_count']?.attributes.tracking_ids || []);
        let fedexTrackingUrl, fedexTrackingStr;
        if (fedexTotalCount === 0) {
            fedexTrackingUrl = 'https://www.fedex.com/fedextracking/'
            fedexTrackingStr = `no packages`;
        } else {
            const baseUrl = 'https://www.fedex.com/fedextrack/?trknbr=';
            const trackingParam = fedexTrackingIds.join(',');
            fedexTrackingUrl = `${baseUrl}${trackingParam}`;
            fedexTrackingStr = `${fedexDeliveredCount}/${fedexTotalCount}`;
        }

        const upsDelivered = parseInt(hass.states['sensor.mail_ups_delivered']?.state) || 0;
        const upsTotalCount = (parseInt(hass.states['sensor.mail_ups_delivering']?.state) || 0) + upsDelivered;
        let upsPackageStr
        if (upsTotalCount === 0) {
            upsPackageStr = `no packages`
        } else {
            upsPackageStr = `${upsDelivered}/${upsTotalCount}`
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

            @media (min-width: 600px) {
                .improved-packages-service-container {
                    flex-wrap: nowrap;
                }
            }
            
            .improved-packages-service {
                flex: 1 1 0;
                text-align: center;
                min-width: 100px;
            }
            
            .improved-packages-service-name {
              font-weight: 600;
              margin-bottom: 8px;
              font-size: 13pt;
            }

            .improved-packages-no-packages-str {
              font-style: italic;
              color: var(--secondary-text-color);
            }

            .improved-packages-status-link {
              color: var(--primary-text-color);
              text-decoration: none;
              font-size: 16px;
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
          </style>
          <ha-card>
              <div class="improved-packages-card">
                  ${
            this.config.title != null && this.config.title !== "undefined" && this.config.title !== "null"
                ? `<div class="improved-packages-header">${this.config.title}</div>`
                : ""
        }
                  <div class="improved-packages-service-container" style="margin-bottom:16px">
                    <div class="improved-packages-service">
                      <div class="improved-packages-service-name">Amazon</div>
                      <a href="https://www.amazon.com/gp/css/order-history" target="_blank" class="improved-packages-status-link ${amazonTotalCount === 0 ? 'improved-packages-no-packages-str' : ''}">${amazonPackageStr}</a>
                      ${amazonPackageItemsHtml}
                    </div>
                  </div>
                  <div class="improved-packages-service-container">
                    <div class="improved-packages-service">
                      <div class="improved-packages-service-name">USPS</div>
                      <a href="${uspsTrackingUrl}" target="_blank" class="improved-packages-status-link ${uspsTotalCount === 0 ? 'improved-packages-no-packages-str' : ''}">${uspsTrackingStr}</a>
                    </div>
              
                    <div class="improved-packages-service">
                      <div class="improved-packages-service-name">FedEx</div>
                      <a href="${fedexTrackingUrl}" target="_blank" class="improved-packages-status-link ${fedexTotalCount === 0 ? 'improved-packages-no-packages-str' : ''}">${fedexTrackingStr}</a>
                    </div>
              
                    <div class="improved-packages-service">
                      <div class="improved-packages-service-name">UPS</div>
                      ${upsPackageStr}
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

    setConfig(config) {
        this.config = config;

        // Variable that is hopefully outside the card refresh
        // scope to prevent the collapse from closing when it's refreshed.
        this.amazonCollapseOpen = false;
    }

    getCardSize() {
        return 3;
    }
}

customElements.define("improved-package-card", PackageTrackerCard);
