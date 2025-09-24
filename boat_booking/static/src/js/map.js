/** @odoo-module **/
/* global google */

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

// Minimal HTML escape to avoid XSS in marker bubble
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

publicWidget.registry.BoatBookingMap = publicWidget.Widget.extend({
    selector: 'section.s_booking_map',
    disabledInEditableMode: false,

    /**
     * @override
     */
    async start() {
        await this._super(...arguments);

        // Store widget reference for other widgets to access
        this.el.__widget = this;

        // Ensure Google Maps API is loaded via website root
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

        const bookingTypeId = this.el.dataset.bookingTypeId;
        this.bookingTypeId = bookingTypeId;
        
        // Track available resources from the booking widget
        this.availableResourceIds = [];
        
        // Listen for resource updates from booking widget
        this._setupResourceUpdateListeners();
        
        // Defer map rendering until we know whether inputs are set
        const lengthEl = document.getElementById('bb-length');
        const widthEl = document.getElementById('bb-width');
        const depthEl = document.getElementById('bb-depth');

        const fetchLocations = async (filters) => {
            try {
                return await rpc('/boat_booking/locations', Object.assign({ booking_type_id: bookingTypeId }, filters || {}));
            } catch (err) {
                console.warn('Failed to load locations:', err);
                return [];
            }
        };

        const ensureMap = async () => {
            if (!this._map) {
                await this.initMap([]);
            }
        };

        this.reloadWithFilters = async () => {
            const minL = parseFloat(lengthEl?.value || '0');
            const minW = parseFloat(widthEl?.value || '0');
            const minD = parseFloat(depthEl?.value || '0');
            const allProvided = [minL, minW, minD].every(n => Number.isFinite(n) && n > 0);
            
            await ensureMap();
            
            if (!allProvided) {
                this.setOverlay(true);
                this.setEmptyState(false);
                // Hide all markers until dimensions are provided
                this.filterMarkers({ 
                    minL: Number.POSITIVE_INFINITY, 
                    minW: Number.POSITIVE_INFINITY, 
                    minD: Number.POSITIVE_INFINITY,
                    availableResourceIds: []
                });
                return;
            }
            
            const locations = await fetchLocations({ 
                min_length: minL, 
                min_width: minW, 
                min_depth: minD
            });
            
            const hasAny = Array.isArray(locations) && locations.length > 0;
            if (!hasAny) {
                this.setOverlay(true, 'No locations found that fit your boat dimensions.');
            } else {
                this.setOverlay(false);
            }
            this.setEmptyState(false);
            await this.setMarkers(locations || []);
            
            // Apply current filters (dimensions + available resources)
            this.filterMarkers({ 
                minL: minL, 
                minW: minW, 
                minD: minD,
                availableResourceIds: this.availableResourceIds
            });
        };

        // Initial boot
        await ensureMap();
        await this.reloadWithFilters();

        // Wire up dimension inputs
        if (lengthEl && widthEl && depthEl) {
            ['input', 'change'].forEach(evt => {
                lengthEl.addEventListener(evt, this.reloadWithFilters);
                widthEl.addEventListener(evt, this.reloadWithFilters);
                depthEl.addEventListener(evt, this.reloadWithFilters);
            });
        }
    },

    /**
     * Setup listeners for resource updates from booking widget
     */
    _setupResourceUpdateListeners: function() {
        // Listen for custom event from booking widget
        document.addEventListener('bookingResourcesUpdated', (event) => {
            console.log('Map received resource update:', event.detail);
            this.updateAvailableResources(event.detail.availableResourceIds);
        });
    },

    /**
     * Update available resources and refresh map display
     */
    updateAvailableResources: function(resourceIds) {
        console.log('Updating map with available resource IDs:', resourceIds);
        this.availableResourceIds = resourceIds || [];
        
        // Re-filter markers based on new available resources
        if (this._markers && this._markers.length > 0) {
            const lengthEl = document.getElementById('bb-length');
            const widthEl = document.getElementById('bb-width');
            const depthEl = document.getElementById('bb-depth');
            
            const minL = parseFloat(lengthEl?.value || '0');
            const minW = parseFloat(widthEl?.value || '0');
            const minD = parseFloat(depthEl?.value || '0');
            
            this.filterMarkers({
                minL: minL,
                minW: minW,
                minD: minD,
                availableResourceIds: this.availableResourceIds
            });
            
            // Update overlay message if no resources are available
            const hasVisibleMarkers = this._markers.some(({ marker }) => {
                return marker.getVisible && marker.getVisible();
            });
            
            if (this.availableResourceIds.length === 0) {
                this.setOverlay(true, 'Please select a time slot to see available locations on the map.');
            } else if (!hasVisibleMarkers) {
                this.setOverlay(true, 'No available locations for the selected time and boat size.');
            } else {
                this.setOverlay(false);
            }
        }
    },

    /**
     * Initializes the Google Map, adds markers, and sets up info windows.
     * @param {Array} locations - The location data from the controller.
     */
    async initMap(locations) {
        // Choose a center: average of points or default Brussels fallback
        let centerLat = 50.854975;
        let centerLng = 4.3753899;
        if (locations.length) {
            const sum = locations.reduce((acc, l) => ({ lat: acc.lat + Number(l.lat || 0), lng: acc.lng + Number(l.lng || 0) }), { lat: 0, lng: 0 });
            centerLat = sum.lat / locations.length;
            centerLng = sum.lng / locations.length;
        }
        const container = this.el.querySelector('.map_container') || this.el;
        const mapOptions = {
            center: new google.maps.LatLng(centerLat, centerLng),
            zoom: locations.length ? 10 : 5,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        };
        const mapId = this.el.dataset.mapId;
        if (mapId) {
            mapOptions.mapId = mapId;
        }
        const map = new google.maps.Map(container, mapOptions);
        this._map = map;

        const infoWindow = new google.maps.InfoWindow();
        const bounds = new google.maps.LatLngBounds();

        // Prefer AdvancedMarkerElement if available
        let AdvancedMarkerElement = null;
        if (mapId) {
            try {
                const markerLib = await google.maps.importLibrary('marker');
                AdvancedMarkerElement = markerLib && markerLib.AdvancedMarkerElement;
            } catch (e) {
                // library may not be available; fall back silently
            }
        }

        this._markers = [];
        this._markerData = locations;
        locations.forEach((loc) => {
            const pos = new google.maps.LatLng(loc.lat, loc.lng);
            bounds.extend(pos);
            let marker;
            if (AdvancedMarkerElement) {
                const content = document.createElement('div');
                const count = (loc.resources || []).length;
                content.className = 'bb-adv-marker';
                content.innerHTML = '<div class="bb-pin"></div>'+
                    '<div class="bb-bubble">'+ escapeHtml(loc.location_name) +
                    '<span class="bb-count">'+ count +'</span></div>';
                marker = new AdvancedMarkerElement({ map, position: pos, content, title: loc.location_name });
                marker.addListener('gmp-click', () => this._openInfo(infoWindow, map, marker, loc));
            } else {
                marker = new google.maps.Marker({ map, position: pos, title: loc.location_name });
                marker.addListener('click', () => this._openInfo(infoWindow, map, marker, loc));
            }
            this._markers.push({ marker, loc });
        });

        // Fit view to markers
        if (locations.length > 1) {
            map.fitBounds(bounds);
        } else if (locations.length === 1) {
            map.setZoom(14);
        }
    },

    async setMarkers(locations) {
        // Clear existing markers
        if (this._markers && this._markers.length) {
            this._markers.forEach(({ marker }) => {
                if (marker.setMap) marker.setMap(null);
            });
        }
        this._markers = [];
        this._markerData = locations || [];

        const map = this._map;
        if (!map) return;
        const bounds = new google.maps.LatLngBounds();
        const infoWindow = new google.maps.InfoWindow();

        let AdvancedMarkerElement = null;
        const mapId = this.el.dataset.mapId;
        if (mapId && google.maps.importLibrary) {
            try {
                const markerLib = await google.maps.importLibrary('marker');
                AdvancedMarkerElement = markerLib && markerLib.AdvancedMarkerElement;
            } catch (e) { /* ignore */ }
        }

        (locations || []).forEach((loc) => {
            const pos = new google.maps.LatLng(loc.lat, loc.lng);
            bounds.extend(pos);
            let marker;
            if (AdvancedMarkerElement) {
                const content = document.createElement('div');
                const count = (loc.resources || []).length;
                content.className = 'bb-adv-marker';
                content.innerHTML = '<div class="bb-pin"></div>'+
                    '<div class="bb-bubble">'+ escapeHtml(loc.location_name) +
                    '<span class="bb-count">'+ count +'</span></div>';
                marker = new AdvancedMarkerElement({ map, position: pos, content, title: loc.location_name });
                marker.addListener('gmp-click', () => this._openInfo(infoWindow, map, marker, loc));
            } else {
                marker = new google.maps.Marker({ map, position: pos, title: loc.location_name });
                marker.addListener('click', () => this._openInfo(infoWindow, map, marker, loc));
            }
            this._markers.push({ marker, loc });
        });

        if ((locations || []).length > 1) {
            map.fitBounds(bounds);
        } else if ((locations || []).length === 1) {
            map.setZoom(14);
            const only = locations[0];
            if (only && only.lat != null && only.lng != null) {
                map.setCenter(new google.maps.LatLng(only.lat, only.lng));
            }
        }
    },

    setOverlay(enable, message) {
        // Create the overlay once and toggle its visibility
        let overlay = this.el.querySelector('.bb-map-overlay');
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
            overlay.innerHTML = '<div class="alert alert-info mb-0">Enter length, width, and depth to enable the map.</div>';

            // Ensure section is positioned to host the absolute overlay
            const section = this.el;
            if (getComputedStyle(section).position === 'static') {
                section.style.position = 'relative';
            }
            section.appendChild(overlay);
        }
        if (enable) {
            const text = (typeof message === 'string' && message) ? message : 'Enter length, width, and depth to enable the map.';
            const body = overlay.querySelector('.alert');
            if (body) body.textContent = text;
            overlay.style.display = 'flex';
        } else {
            overlay.style.display = 'none';
        }
    },

    setEmptyState(show) {
        // Show a message card on the map when no locations are available
        let empty = this.el.querySelector('.bb-empty-state');
        if (!empty) {
            empty = document.createElement('div');
            empty.className = 'bb-empty-state';
            empty.style.position = 'absolute';
            empty.style.top = '16px';
            empty.style.left = '16px';
            empty.style.zIndex = '4';
            empty.style.maxWidth = '520px';
            empty.style.pointerEvents = 'none';
            empty.innerHTML = '<div class="card shadow-sm" style="pointer-events:auto">\
                <div class="card-body">\
                    <div class="h5 mb-2">Fully booked</div>\
                    <div>We found no locations that fit your boat, check the dates and size.</div>\
                </div>\
            </div>';
            const section = this.el;
            if (getComputedStyle(section).position === 'static') {
                section.style.position = 'relative';
            }
            section.appendChild(empty);
        }
        empty.style.display = show ? 'block' : 'none';
    },

    filterMarkers({ minL, minW, minD, availableResourceIds = [] }) {
        if (!this._markers) return;
        
        console.log('Filtering markers with:', { minL, minW, minD, availableResourceIds });
        
        this._markers.forEach(({ marker, loc }) => {
            let isVisible = false;
            
            // Check if location has resources that meet dimensional requirements
            const dimensionMatches = (loc.resources || []).filter(r => (
                (r.length == null || r.length >= minL) &&
                (r.width == null || r.width >= minW) &&
                (r.depth == null || r.depth >= minD)
            ));
            
            if (dimensionMatches.length > 0) {
                // If no available resources specified, show all that meet dimensions
                if (availableResourceIds.length === 0) {
                    isVisible = true;
                } else {
                    // Only show if at least one resource is in available list AND meets dimensions
                    isVisible = dimensionMatches.some(r => availableResourceIds.includes(r.id));
                }
            }
            
            // Apply visibility to marker
            if (marker.setVisible) {
                marker.setVisible(isVisible);
            } else if (marker.map) {
                marker.map.setVisible ? marker.map.setVisible(isVisible) : null;
            }
        });
    },

    _openInfo(infoWindow, map, marker, loc) {
        const primary = loc.resources[0] || {};
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

        const header = '<div class="bb-card-header"><span class="bb-header-title">' + escapeHtml(loc.location_name) + '</span></div>';
        const footer = '<div class="bb-card-footer"><a id="bb-book-btn" class="btn btn-primary bb-btn bb-btn-full" href="#">Book this Spot</a></div>';
        const content = '<div class="bb-card">' + header + '<div class="bb-card-body">' + body + '</div>' + footer + '</div>';
        infoWindow.setContent(content);
        infoWindow.open({ map, anchor: marker });

        // Bind click after DOM is ready in the info window
        google.maps.event.addListenerOnce(infoWindow, 'domready', () => {
            const btn = document.getElementById('bb-book-btn');
            if (!btn) return;
            btn.addEventListener('click', (ev) => {
                ev.preventDefault();
                if (!resourceId) return;
                const url = this._buildBookingUrlForResource(resourceId);
                if (url) {
                    document.location = encodeURI(url.href);
                } else {
                    // If no slot selected, hint the user
                    this.setOverlay(true, 'Please select a time first, then choose a spot on the map.');
                    setTimeout(() => this.setOverlay(false), 2500);
                }
            });
        });
    },

    _buildBookingUrlForResource(resourceId) {
        try {
            const bookingTypeID = this.el.closest('body').querySelector("input[name='booking_type_id']")?.value;
            const selectedSlot = this.el.closest('body').querySelector('.o_slot_hours.o_slot_hours_selected');
            if (!bookingTypeID || !selectedSlot) return null;
            const urlParameters = decodeURIComponent(selectedSlot.dataset.urlParameters || '');
            const url = new URL(`/booking/${encodeURIComponent(bookingTypeID)}/info?${urlParameters}`, location.origin);

            const resourceCapacity = parseInt(this.el.closest('body').querySelector("select[name='resourceCapacity']")?.value) || 1;
            const assignMethod = this.el.closest('body').querySelector("input[name='assign_method']")?.value;
            const scheduleBasedOn = this.el.closest('body').querySelector("input[name='schedule_based_on']")?.value;

            if (scheduleBasedOn === 'resources') {
                url.searchParams.set('resource_selected_id', encodeURIComponent(resourceId));
                url.searchParams.set('available_resource_ids', JSON.stringify([resourceId]));
                url.searchParams.set('asked_capacity', encodeURIComponent(resourceCapacity));
            } else {
                // Fallback: treat as staff user id if configured that way
                url.searchParams.set('staff_user_id', encodeURIComponent(resourceId));
            }
            // Include boat dimensions so they propagate to submit step
            const lengthEl = document.getElementById('bb-length');
            const widthEl = document.getElementById('bb-width');
            const depthEl = document.getElementById('bb-depth');
            if (lengthEl?.value) url.searchParams.set('length', lengthEl.value);
            if (widthEl?.value) url.searchParams.set('width', widthEl.value);
            if (depthEl?.value) url.searchParams.set('depth', depthEl.value);
            return url;
        } catch (e) {
            console.warn('Failed to build booking URL:', e);
            return null;
        }
    },
});