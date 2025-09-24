/** @odoo-module **/
/* global google */

import publicWidget from "@web/legacy/js/public/public_widget";
import { renderToFragment } from "@web/core/utils/render";
import { rpc } from "@web/core/network/rpc";
const { DateTime } = luxon;

// Utility functions from the original map widget
function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = String(value == null ? '' : value);
    return div.innerHTML;
}

function formatPrice(amount, symbol, position) {
    if (typeof amount !== 'number') {
        return '';
    }
    const formatted = amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const sym = escapeHtml(symbol || '');
    return position === 'after' ? `${formatted} ${sym}` : `${sym}${sym ? ' ' : ''}${formatted}`;
}

// Complete consolidated booking widget with integrated map
publicWidget.registry.bookingSlotSelect = publicWidget.registry.bookingSlotSelect.extend({

    events: Object.assign({}, publicWidget.registry.bookingSlotSelect.prototype.events, {
        'input #bb-length, #bb-width, #bb-depth': '_onResourceAttributeChange',
        'blur #bb-length, #bb-width, #bb-depth': '_onResourceAttributeChange',
    }),

    /**
     * @override
     */
    async start() {
        await this._super(...arguments);

        // Initialize map-related properties
        this.currentSlotData = null;
        this.map = null;
        this.mapMarkers = [];
        this.infoWindow = null;
        this.availableResourceIds = [];

        // Initialize map for boat bookings
        await this._initializeMapIfNeeded();

        return Promise.resolve();
    },

    /**
     * Initialize map if this is a boat booking
     */
    _initializeMapIfNeeded: async function() {
        const bookingType = this._getBookingType();
        const mapContainer = document.querySelector('section.s_booking_map .map_container');

        if (bookingType === 'boat' && mapContainer && !this.map) {
            console.log("Initializing map for boat booking");
            await this._ensureGoogleMapsLoaded();
            await this._initializeMap();
        }
    },

    /**
     * Ensure Google Maps API is loaded
     */
    _ensureGoogleMapsLoaded: async function() {
        if (typeof google !== 'object' || typeof google.maps !== 'object') {
            await new Promise(resolve => {
                this.trigger_up('gmap_api_request', {
                    editableMode: this.editableMode,
                    onSuccess: () => resolve(),
                });
            });
            if (typeof google !== 'object' || typeof google.maps !== 'object') {
                console.warn('Google Maps API still unavailable (no key configured or network issue).');
                return;
            }
        }
    },

    /**
     * Initialize the Google Map
     */
    _initializeMap: async function() {
        const mapContainer = document.querySelector('section.s_booking_map .map_container');
        if (!mapContainer) {
            console.log("Map container not found");
            return;
        }

        try {
            // Initialize map with default center (Brussels)
            const mapOptions = {
                center: new google.maps.LatLng(50.854975, 4.3753899),
                zoom: 10,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
            };

            // Check for advanced markers map ID
            const mapSection = document.querySelector('section.s_booking_map');
            const mapId = mapSection?.dataset.mapId;
            if (mapId) {
                mapOptions.mapId = mapId;
            }

            this.map = new google.maps.Map(mapContainer, mapOptions);
            this.mapMarkers = [];
            this.infoWindow = new google.maps.InfoWindow();

            console.log("Map initialized successfully");

            // Set initial overlay
            this._setMapOverlay(true, 'Enter boat dimensions to see available locations');

            // Set up dimension input listeners for map updates
            this._setupMapInputListeners();

        } catch (error) {
            console.error("Error initializing map:", error);
        }
    },

    /**
     * Set up listeners for dimension inputs to update map
     */
    _setupMapInputListeners: function() {
        const lengthEl = document.getElementById('bb-length');
        const widthEl = document.getElementById('bb-width');
        const depthEl = document.getElementById('bb-depth');

        if (lengthEl && widthEl && depthEl) {
            ['input', 'change'].forEach(evt => {
                lengthEl.addEventListener(evt, () => this._updateMapWithCurrentData());
                widthEl.addEventListener(evt, () => this._updateMapWithCurrentData());
                depthEl.addEventListener(evt, () => this._updateMapWithCurrentData());
            });
        }
    },

    _onClickHoursSlot: function (ev) {
        console.log("----------- Custom hours slot click");

        this.el
            .querySelector(".o_slot_hours.o_slot_hours_selected")
            ?.classList.remove("o_slot_hours_selected", "active");
        ev.currentTarget.classList.add("o_slot_hours_selected", "active");

        const assignMethod = this.el.querySelector("input[name='assign_method']").value;
        const scheduleBasedOn = this.el.querySelector("input[name='schedule_based_on']").value;

        // If not in 'time_resource' we directly go to the url for the slot
        if (assignMethod !== "time_resource") {
            const bookingTypeID = this.el.querySelector("input[name='booking_type_id']").value;
            const urlParameters = decodeURIComponent(
                this.el.querySelector(".o_slot_hours_selected").dataset.urlParameters
            );
            const url = new URL(
                `/booking/${encodeURIComponent(bookingTypeID)}/info?${urlParameters}`,
                location.origin);
            document.location = encodeURI(url.href);
            return;
        }

        // Store the slot data for later use
        this.currentSlotData = {
            availableResources: ev.currentTarget.dataset.availableResources
                ? JSON.parse(ev.currentTarget.dataset.availableResources)
                : undefined,
            availableStaffUsers: ev.currentTarget.dataset.availableStaffUsers
                ? JSON.parse(ev.currentTarget.dataset.availableStaffUsers)
                : undefined,
            scheduleBasedOn: scheduleBasedOn
        };

        // Check booking type to determine flow
        const bookingType = this._getBookingType();
        console.log("Booking type detected:", bookingType);

        if (bookingType === 'boat') {
            // For boat bookings, show attributes form first
            this._showResourceAttributesForm();
        } else {
            // For other bookings, show resources list directly (original behavior)
            this._showResourcesListDirectly();
        }
    },

    /**
     * Get the booking type from the form data
     */
    _getBookingType: function() {
        const bookingTypeInput = this.el.querySelector("input[name='booking_type']");
        if (bookingTypeInput) {
            return bookingTypeInput.value;
        }
        console.warn("Booking type input field not found, defaulting to 'other'");
        return 'other';
    },

    /**
     * Show resources list directly (original Odoo behavior for non-boat bookings)
     */
    _showResourcesListDirectly: function() {
        console.log("Showing resources list directly (non-boat booking)");
        if (this._getBookingType() === 'boat') {
            // For boat bookings, keep the attribute + map flow
            this._showResourceAttributesForm();
            return;
        }
        const previousResourceIdSelected = this.el.querySelector("select[name='resource_id']")?.value;

        this.resourceSelectionEl.replaceChildren(
            renderToFragment("base_booking.resources_list", {
                availableResources: this.currentSlotData.availableResources,
                availableStaffUsers: this.currentSlotData.availableStaffUsers,
                scheduleBasedOn: this.currentSlotData.scheduleBasedOn,
            })
        );

        const availableEntity = this.currentSlotData.scheduleBasedOn === "resources"
            ? this.currentSlotData.availableResources
            : this.currentSlotData.availableStaffUsers;

        const resourceIdEl = this.el.querySelector("select[name='resource_id']");

        if (availableEntity && availableEntity.length === 1) {
            resourceIdEl?.setAttribute("disabled", true);
        }

        if (previousResourceIdSelected &&
            this.el.querySelector(`select[name='resource_id'] > option[value='${previousResourceIdSelected}']`)) {
            resourceIdEl.value = previousResourceIdSelected;
        }

        this.resourceSelectionEl.classList.remove("d-none");
    },

    /**
     * Show the resource attributes form
     */
    _showResourceAttributesForm: function() {
        console.log("Showing resource attributes form");

        this.resourceSelectionEl.replaceChildren();

        const attributesFragment = renderToFragment("boat_booking.resources_attributes", {});
        this.resourceSelectionEl.appendChild(attributesFragment);

        this.resourceSelectionEl.classList.remove("d-none");

        const resourcesListContainer = document.createElement('div');
        resourcesListContainer.className = 'd-none';
        resourcesListContainer.id = 'resources-list-container';
        this.resourceSelectionEl.appendChild(resourcesListContainer);

        setTimeout(() => {
            const lengthInput = this.el.querySelector('#bb-length');
            if (lengthInput) {
                lengthInput.focus();
            }
            // Hide base confirm button for boat flow
            if (this._getBookingType() === 'boat') {
                const confirmBtn = this.el.querySelector('button[name="submitSlotInfoSelected"]');
                confirmBtn?.classList.add('d-none');
            }
        }, 100);
    },

    /**
     * Handle resource attribute changes and validate form
     */
    _onResourceAttributeChange: function(ev) {
        console.log("Resource attribute changed:", ev.currentTarget.id, ev.currentTarget.value);

        this._addValidationFeedback();

        if (this._validateResourceAttributes()) {
            this._showResourcesList();
        } else {
            this._hideResourcesList();
        }
    },

    /**
     * Validate that all required resource attributes are filled
     */
    _validateResourceAttributes: function() {
        const lengthInput = this.el.querySelector('#bb-length');
        const widthInput = this.el.querySelector('#bb-width');
        const depthInput = this.el.querySelector('#bb-depth');

        const length = lengthInput?.value.trim();
        const width = widthInput?.value.trim();
        const depth = depthInput?.value.trim();

        const isValid = length && width && depth &&
                       parseFloat(length) > 0 &&
                       parseFloat(width) > 0 &&
                       parseFloat(depth) > 0;

        console.log("Resource attributes validation:", { length, width, depth, isValid });

        return isValid;
    },

    /**
     * Show the resources list after attributes are validated
     */
    _showResourcesList: async function() {
        console.log("Showing resources list");

        const resourcesListContainer = this.el.querySelector('#resources-list-container');
        if (!resourcesListContainer) return;

        const previousResourceIdSelected = this.el.querySelector("select[name='resource_id']")?.value;

        // Apply client-side dimension filtering using booking.resource dimensions
        let availableResources = this.currentSlotData.availableResources || [];
        try {
            const filters = this._getDimensionFilterValues();
            if (filters && availableResources.length) {
                const ids = availableResources.map(r => r.id).filter(Boolean);
                const dims = await rpc('/web/dataset/call_kw', {
                    model: 'booking.resource',
                    method: 'read',
                    args: [ids, ['id', 'length', 'width', 'depth']],
                    kwargs: {},
                });
                const allowedIds = new Set(dims.filter(d =>
                    (Number(d.length || 0) >= filters.length) &&
                    (Number(d.width || 0) >= filters.width) &&
                    (Number(d.depth || 0) >= filters.depth)
                ).map(d => d.id));
                availableResources = availableResources.filter(r => allowedIds.has(r.id));
            }
        } catch (e) {
            console.warn('Dimension filtering failed, falling back to unfiltered resources', e);
        }

        // If boat booking, do not render the base resources dropdown; only update the map
        if (this._getBookingType() === 'boat') {
            try {
                const locations = await this._buildLocationsFromResources(availableResources);
                const availableIds = availableResources.map(r => r.id);
                await this._updateMapMarkers(locations, availableIds);
                if (availableIds.length === 0) {
                    this._setMapOverlay(true, 'No available locations for the selected time and boat size');
                } else {
                    this._setMapOverlay(false);
                }
            } catch (e) {
                console.warn('Map update failed', e);
            }
            return;
        }

        const resourcesFragment = renderToFragment("base_booking.resources_list", {
            availableResources: availableResources,
            availableStaffUsers: this.currentSlotData.availableStaffUsers,
            scheduleBasedOn: this.currentSlotData.scheduleBasedOn,
        });

        resourcesListContainer.replaceChildren(resourcesFragment);
        resourcesListContainer.classList.remove('d-none');

        const availableEntity = this.currentSlotData.scheduleBasedOn === "resources"
            ? availableResources
            : this.currentSlotData.availableStaffUsers;

        const resourceIdEl = this.el.querySelector("select[name='resource_id']");

        if (availableEntity && availableEntity.length === 1) {
            resourceIdEl?.setAttribute("disabled", true);
        }

        if (previousResourceIdSelected &&
            this.el.querySelector(`select[name='resource_id'] > option[value='${previousResourceIdSelected}']`)) {
            resourceIdEl.value = previousResourceIdSelected;
        }

        // Update map with newly filtered resources
        try {
            const locations = await this._buildLocationsFromResources(availableResources);
            const availableIds = availableResources.map(r => r.id);
            await this._updateMapMarkers(locations, availableIds);
            this._setMapOverlay(false);
        } catch (e) {
            console.warn('Map update failed', e);
        }
    },

    /**
     * Get numeric dimension filters from inputs
     */
    _getDimensionFilterValues: function() {
        const lengthEl = this.el.querySelector('#bb-length');
        const widthEl = this.el.querySelector('#bb-width');
        const depthEl = this.el.querySelector('#bb-depth');
        const length = parseFloat(lengthEl?.value || '0');
        const width = parseFloat(widthEl?.value || '0');
        const depth = parseFloat(depthEl?.value || '0');
        if (length > 0 && width > 0 && depth > 0) {
            return { length, width, depth };
        }
        return null;
    },

    /**
     * Update map with current booking data
     */
    _updateMapWithCurrentData: async function() {
        if (!this.map) return;

        const lengthEl = this.el.querySelector('#bb-length');
        const widthEl = this.el.querySelector('#bb-width');
        const depthEl = this.el.querySelector('#bb-depth');

        const length = parseFloat(lengthEl?.value || '0');
        const width = parseFloat(widthEl?.value || '0');
        const depth = parseFloat(depthEl?.value || '0');

        const dimensionsValid = length > 0 && width > 0 && depth > 0;

        if (!dimensionsValid) {
            this._setMapOverlay(true, 'Enter boat dimensions to see available locations');
            this._clearMapMarkers();
            return;
        }

        const availableResourceIds = this._getAvailableResourceIds();

        try {
            const locations = await this._fetchLocations({
                min_length: length,
                min_width: width,
                min_depth: depth
            });

            if (!locations || locations.length === 0) {
                this._setMapOverlay(true, 'No locations found that fit your boat dimensions');
                this._clearMapMarkers();
                return;
            }

            await this._updateMapMarkers(locations, availableResourceIds);
            this._setMapOverlay(false);

        } catch (error) {
            console.error("Error updating map:", error);
            this._setMapOverlay(true, 'Error loading locations');
        }
    },

    /**
     * Fetch locations from server
     */
    _fetchLocations: async function(filters) {
        // Not used anymore; replaced by _buildLocationsFromResources
        return [];
    },

    /**
     * Build map locations from a list of available resources.
     */
    _buildLocationsFromResources: async function(availableResources) {
        if (!Array.isArray(availableResources) || availableResources.length === 0) return [];

        const ids = availableResources.map(r => r.id).filter(Boolean);
        const records = await rpc('/web/dataset/call_kw', {
            model: 'booking.resource',
            method: 'read',
            args: [ids, ['id', 'name', 'capacity', 'latitude', 'longitude', 'address', 'city', 'length', 'width', 'depth', 'product_id']],
            kwargs: {},
        });

        // Read product pricing info if any
        let productInfo = {};
        const productIds = records.map(r => Array.isArray(r.product_id) ? r.product_id[0] : null).filter(Boolean);
        if (productIds.length) {
            const products = await rpc('/web/dataset/call_kw', {
                model: 'product.product',
                method: 'read',
                args: [productIds, ['id', 'lst_price', 'currency_id']],
                kwargs: {},
            });
            const currencyIds = products.map(p => Array.isArray(p.currency_id) ? p.currency_id[0] : null).filter(Boolean);
            let currencies = [];
            if (currencyIds.length) {
                currencies = await rpc('/web/dataset/call_kw', {
                    model: 'res.currency',
                    method: 'read',
                    args: [currencyIds, ['id', 'symbol', 'position']],
                    kwargs: {},
                });
            }
            const currencyMap = Object.fromEntries(currencies.map(c => [c.id, c]));
            productInfo = Object.fromEntries(products.map(p => [p.id, {
                price: typeof p.lst_price === 'number' ? p.lst_price : null,
                currency: currencyMap[Array.isArray(p.currency_id) ? p.currency_id[0] : p.currency_id] || null,
            }]));
        }

        const locationsMap = {};
        const round6 = (v) => {
            const n = Number(v);
            return Number.isFinite(n) ? Math.round(n * 1e6) / 1e6 : null;
        };

        records.forEach(r => {
            const lat = round6(r.latitude);
            const lng = round6(r.longitude);
            if (lat == null || lng == null) return;

            const key = `${lat}:${lng}`;
            if (!locationsMap[key]) {
                locationsMap[key] = {
                    location_name: r.address || r.city || r.name || `${lat}, ${lng}`,
                    lat,
                    lng,
                    resources: [],
                };
            }
            const prodId = Array.isArray(r.product_id) ? r.product_id[0] : null;
            const p = prodId ? productInfo[prodId] : null;
            locationsMap[key].resources.push({
                id: r.id,
                name: r.name,
                capacity: r.capacity,
                length: Number(r.length || 0) || null,
                width: Number(r.width || 0) || null,
                depth: Number(r.depth || 0) || null,
                price: p ? p.price : null,
                currency_symbol: p && p.currency ? p.currency.symbol : null,
                currency_position: p && p.currency ? p.currency.position : null,
            });
        });

        return Object.values(locationsMap);
    },

    /**
     * Update map markers with locations (using BoatBookingMap style)
     */
    _updateMapMarkers: async function(locations, availableResourceIds) {
        console.log("Updating map markers with", locations.length, "locations");

        this._clearMapMarkers();

        const bounds = new google.maps.LatLngBounds();
        let hasVisibleMarkers = false;

        // Check for advanced markers
        let AdvancedMarkerElement = null;
        const mapSection = document.querySelector('section.s_booking_map');
        const mapId = mapSection?.dataset.mapId;
        if (mapId && google.maps.importLibrary) {
            try {
                const markerLib = await google.maps.importLibrary('marker');
                AdvancedMarkerElement = markerLib?.AdvancedMarkerElement;
                console.log("Advanced markers available");
            } catch (e) {
                console.log("Advanced markers not available, using standard markers");
            }
        }

        locations.forEach((location, index) => {
            console.log(`Creating marker ${index + 1} for location:`, location.location_name);

            const pos = new google.maps.LatLng(location.lat, location.lng);
            bounds.extend(pos);

            // Check if location has available resources
            const hasAvailableResources = availableResourceIds.length === 0 ||
                (location.resources || []).some(r => availableResourceIds.includes(r.id));

            let marker;
            if (AdvancedMarkerElement) {
                const content = document.createElement('div');
                const count = (location.resources || []).length;
                content.className = 'bb-adv-marker';
                content.innerHTML = `
                    <div class="bb-pin"></div>
                    <div class="bb-bubble">${escapeHtml(location.location_name)}
                        <span class="bb-count">${count}</span>
                    </div>
                `;
                marker = new AdvancedMarkerElement({
                    map: this.map,
                    position: pos,
                    content,
                    title: location.location_name
                });

                marker.addListener('gmp-click', () => {
                    console.log("Advanced marker clicked for:", location.location_name);
                    this._openInfoWindow(location);
                });
            } else {
                marker = new google.maps.Marker({
                    map: this.map,
                    position: pos,
                    title: location.location_name
                });

                marker.addListener('click', () => {
                    console.log("Standard marker clicked for:", location.location_name);
                    this._openInfoWindow(location);
                });
            }

            // Set marker visibility
            const isVisible = hasAvailableResources;
            if (marker.setVisible) {
                marker.setVisible(isVisible);
            }

            if (isVisible) {
                hasVisibleMarkers = true;
            }

            this.mapMarkers.push({
                marker,
                location: { ...location, id: location.id || index },
                visible: isVisible
            });

            console.log(`Marker ${index + 1} created, visible: ${isVisible}`);
        });

        console.log(`Created ${this.mapMarkers.length} markers, ${hasVisibleMarkers ? 'some' : 'none'} visible`);

        // Fit map to visible markers
        if (hasVisibleMarkers && locations.length > 0) {
            this.map.fitBounds(bounds);
        }

        // Update overlay based on results
        if (availableResourceIds.length > 0 && !hasVisibleMarkers) {
            this._setMapOverlay(true, 'No available locations for the selected time and boat size');
        } else if (availableResourceIds.length === 0 && locations.length > 0) {
            this._setMapOverlay(true, 'Select a time slot to see available locations');
        }
    },

    /**
     * Open info window for location (using BoatBookingMap style)
     */
    _openInfoWindow: function(location) {
        console.log("Opening info window for location:", location.location_name);

        if (!this.infoWindow || !this.map) {
            console.error("Info window or map not available");
            return;
        }

        const primary = location.resources && location.resources[0] ? location.resources[0] : {};
        console.log("Resource data:", primary);

        // Use BoatBookingMap styling
        const priceStr = formatPrice(primary.price, primary.currency_symbol, primary.currency_position);
        const length = (primary.length != null) ? primary.length.toFixed(2) + ' m' : '-';
        const width = (primary.width != null) ? primary.width.toFixed(2) + ' m' : '-';
        const depth = (primary.depth != null) ? primary.depth.toFixed(2) + ' m' : '-';
        const resourceId = primary.id;

        const body = ''+
            '<div class="bb-entry">'
            +   '<ul class="bb-list">'
            +       (priceStr ? '<li><span class="bb-label">Price</span><span class="bb-val bb-price">' + priceStr + '</span></li>' : '')
            +       '<li><span class="bb-label">Length</span><span class="bb-val">' + length + '</span></li>'
            +       '<li><span class="bb-label">Width</span><span class="bb-val">' + width + '</span></li>'
            +       '<li><span class="bb-label">Depth</span><span class="bb-val">' + depth + '</span></li>'
            +   '</ul>'
            + '</div>';

        const header = '<div class="bb-card-header"><span class="bb-header-title">' + escapeHtml(location.location_name) + '</span></div>';
        const footer = '<div class="bb-card-footer"><a id="bb-book-btn" class="btn btn-primary bb-btn bb-btn-full" href="#">Book this Spot</a></div>';
        const content = '<div class="bb-card">' + header + '<div class="bb-card-body">' + body + '</div>' + footer + '</div>';

        console.log("Setting info window content");
        this.infoWindow.setContent(content);

        const markerData = this.mapMarkers.find(m =>
            m.location.id === location.id ||
            m.location.location_name === location.location_name
        );

        if (markerData && markerData.marker) {
            console.log("Opening info window anchored to marker");
            this.infoWindow.open({ map: this.map, anchor: markerData.marker });
        } else {
            console.log("Opening info window at position:", location.lat, location.lng);
            this.infoWindow.setPosition(new google.maps.LatLng(location.lat, location.lng));
            this.infoWindow.open(this.map);
        }

        // Bind click after DOM is ready
        google.maps.event.addListenerOnce(this.infoWindow, 'domready', () => {
            const btn = document.getElementById('bb-book-btn');
            if (!btn) return;
            btn.addEventListener('click', (ev) => {
                ev.preventDefault();
                if (!resourceId) return;
                console.log("Info window button clicked, selecting resource:", resourceId);
                this._selectResourceFromMap(resourceId);
                this.infoWindow.close();
            });
        });

        console.log("Info window setup complete");
    },

    /**
     * Handle resource selection from map (directly proceed to booking)
     */
    _selectResourceFromMap: function(resourceId) {
        console.log("Resource selected from map:", resourceId);

        // For boat bookings, we want to bypass the dropdown and go directly to booking
        const bookingType = this._getBookingType();

        if (bookingType === 'boat') {
            // Set the resource behind the scenes and proceed directly to booking URL
            this._proceedToBookingWithResource(resourceId);
        } else {
            // For other booking types, use the dropdown selection method
            const resourceSelect = this.el.querySelector("select[name='resource_id']");
            if (resourceSelect) {
                resourceSelect.value = resourceId;
                resourceSelect.dispatchEvent(new Event('change'));

                const confirmButton = this.el.querySelector('button[name="submitSlotInfoSelected"]');
                if (confirmButton) {
                    confirmButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        }
    },

    /**
     * Proceed directly to booking with selected resource (bypass dropdown)
     */
    _proceedToBookingWithResource: function(resourceId) {
        console.log("Proceeding directly to booking with resource:", resourceId);

        try {
            const bookingTypeID = this.el.querySelector("input[name='booking_type_id']").value;
            const selectedSlot = this.el.querySelector('.o_slot_hours.o_slot_hours_selected');

            if (!bookingTypeID || !selectedSlot) {
                console.error("Missing booking type or selected slot");
                return;
            }

            const urlParameters = decodeURIComponent(selectedSlot.dataset.urlParameters || '');
            const url = new URL(`/booking/${encodeURIComponent(bookingTypeID)}/info?${urlParameters}`, location.origin);

            const resourceCapacity = parseInt(this.el.querySelector("select[name='resourceCapacity']")?.value) || 1;
            const assignMethod = this.el.querySelector("input[name='assign_method']")?.value;
            const scheduleBasedOn = this.el.querySelector("input[name='schedule_based_on']")?.value;

            if (scheduleBasedOn === 'resources') {
                url.searchParams.set('resource_selected_id', encodeURIComponent(resourceId));
                url.searchParams.set('available_resource_ids', JSON.stringify([resourceId]));
                url.searchParams.set('asked_capacity', encodeURIComponent(resourceCapacity));
            } else {
                url.searchParams.set('staff_user_id', encodeURIComponent(resourceId));
            }

            // Include boat dimensions
            const lengthEl = this.el.querySelector('#bb-length');
            const widthEl = this.el.querySelector('#bb-width');
            const depthEl = this.el.querySelector('#bb-depth');

            if (lengthEl?.value) url.searchParams.set('length', lengthEl.value);
            if (widthEl?.value) url.searchParams.set('width', widthEl.value);
            if (depthEl?.value) url.searchParams.set('depth', depthEl.value);

            console.log("Navigating to booking URL:", url.href);

            // Navigate directly to the booking page
            document.location = encodeURI(url.href);

        } catch (error) {
            console.error("Error proceeding to booking:", error);
        }
    },

    /**
     * Get available resource IDs from current slot data
     */
    _getAvailableResourceIds: function() {
        if (!this.currentSlotData) return [];

        const resourceIds = [];
        if (this.currentSlotData.scheduleBasedOn === "resources" && this.currentSlotData.availableResources) {
            this.currentSlotData.availableResources.forEach(resource => {
                if (resource.id) resourceIds.push(resource.id);
            });
        } else if (this.currentSlotData.scheduleBasedOn === "users" && this.currentSlotData.availableStaffUsers) {
            this.currentSlotData.availableStaffUsers.forEach(user => {
                if (user.id) resourceIds.push(user.id);
            });
        }
        return resourceIds;
    },

    /**
     * Clear all map markers
     */
    _clearMapMarkers: function() {
        if (this.mapMarkers) {
            this.mapMarkers.forEach(({ marker }) => {
                if (marker.setMap) marker.setMap(null);
            });
            this.mapMarkers = [];
        }
    },

    /**
     * Set map overlay message
     */
    _setMapOverlay: function(show, message = '') {
        const mapSection = document.querySelector('section.s_booking_map');
        if (!mapSection) return;

        let overlay = mapSection.querySelector('.bb-map-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'bb-map-overlay';
            overlay.setAttribute('role', 'status');
            overlay.style.position = 'absolute';
            overlay.style.inset = '0';
            overlay.style.zIndex = '3';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.background = 'rgba(255,255,255,0.6)';
            overlay.style.backdropFilter = 'saturate(180%) blur(2px)';
            overlay.innerHTML = '<div class="alert alert-info mb-0">Loading map...</div>';

            const section = mapSection;
            if (getComputedStyle(section).position === 'static') {
                section.style.position = 'relative';
            }
            section.appendChild(overlay);
        }

        const alertDiv = overlay.querySelector('.alert');
        if (show) {
            alertDiv.textContent = message || 'Loading map...';
            overlay.style.display = 'flex';
        } else {
            overlay.style.display = 'none';
        }
    },

    /**
     * Hide the resources list when attributes are not valid
     */
    _hideResourcesList: function() {
        const resourcesListContainer = this.el.querySelector('#resources-list-container');
        if (resourcesListContainer) {
            resourcesListContainer.classList.add('d-none');
        }
    },

    /**
     * Add visual feedback for validation state
     */
    _addValidationFeedback: function() {
        const inputs = this.el.querySelectorAll('#bb-length, #bb-width, #bb-depth');

        inputs.forEach(input => {
            input.classList.remove('is-valid', 'is-invalid');

            if (input.value.trim()) {
                if (parseFloat(input.value) > 0) {
                    input.classList.add('is-valid');
                } else {
                    input.classList.add('is-invalid');
                }
            }
        });
    }
});