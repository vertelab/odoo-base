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

        // Ensure Google Maps API is loaded via website root
        if (typeof google !== 'object' || typeof google.maps !== 'object') {
            await new Promise(resolve => {
                this.trigger_up('gmap_api_request', {
                    editableMode: this.editableMode,
                    onSuccess: () => resolve(),
                });
            });
            // Continue: our snippet isn't auto-restarted by the website callback
            if (typeof google !== 'object' || typeof google.maps !== 'object') {
                console.warn('Google Maps API still unavailable (no key configured or network issue).');
                return;
            }
        }

        const bookingTypeId = this.el.dataset.bookingTypeId;
        this.bookingTypeId = bookingTypeId;
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

        const reloadWithFilters = async () => {
            const minL = parseFloat(lengthEl?.value || '0');
            const minW = parseFloat(widthEl?.value || '0');
            const minD = parseFloat(depthEl?.value || '0');
            const allProvided = [minL, minW, minD].every(n => Number.isFinite(n) && n > 0);
            await ensureMap();
            if (!allProvided) {
                this.setOverlay(true);
                this.setEmptyState(false);
                // Hide markers until ready
                this.filterMarkers({ minL: Number.POSITIVE_INFINITY, minW: Number.POSITIVE_INFINITY, minD: Number.POSITIVE_INFINITY });
                return;
            }
            const locations = await fetchLocations({ min_length: minL, min_width: minW, min_depth: minD });
            const hasAny = Array.isArray(locations) && locations.length > 0;
            if (!hasAny) {
                this.setOverlay(true, 'Fully booked — We found no locations that fit your boat, check the dates and size.');
            } else {
                this.setOverlay(false);
            }
            this.setEmptyState(false);
            await this.setMarkers(locations || []);
            this.filterMarkers({ minL: minL, minW: minW, minD: minD });
        };

        // Initial boot
        await ensureMap();
        await reloadWithFilters();

        // Wire up dimension inputs to filter markers and gate map interactions
        if (lengthEl && widthEl && depthEl) {
            ['input', 'change'].forEach(evt => {
                lengthEl.addEventListener(evt, reloadWithFilters);
                widthEl.addEventListener(evt, reloadWithFilters);
                depthEl.addEventListener(evt, reloadWithFilters);
            });
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
        if (mapId) {
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

    filterMarkers({ minL, minW, minD }) {
        if (!this._markers) return;
        const meets = (r) => (
            (r.length == null || r.length >= minL) &&
            (r.width == null || r.width >= minW) &&
            (r.depth == null || r.depth >= minD)
        );
        this._markers.forEach(({ marker, loc }) => {
            const ok = (loc.resources || []).some(meets);
            if (marker.map) {
                marker.map.setVisible ? marker.map.setVisible(ok) : null;
            }
            if (marker.setVisible) marker.setVisible(ok);
        });
    },

    _openInfo(infoWindow, map, marker, loc) {
        const primary = loc.resources[0] || {};
        const priceStr = formatPrice(primary.price, primary.currency_symbol, primary.currency_position);
        const length = (primary.length != null) ? primary.length.toFixed(2) + ' m' : '-';
        const width = (primary.width != null) ? primary.width.toFixed(2) + ' m' : '-';
        const depth = (primary.depth != null) ? primary.depth.toFixed(2) + ' m' : '-';
        const url = primary.book_url || (primary.id ? ('/booking?filter_resource_ids=' + encodeURIComponent('[' + primary.id + ']')) : '#');

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
        const footer = '<div class="bb-card-footer"><a class="btn btn-primary bb-btn bb-btn-full" href="' + url + '">Book this Spot</a></div>';
        const content = '<div class="bb-card">' + header + '<div class="bb-card-body">' + body + '</div>' + footer + '</div>';
        infoWindow.setContent(content);
        infoWindow.open({ map, anchor: marker });
    },
});


