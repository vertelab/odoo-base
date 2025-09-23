/** @odoo-module **/
/* global MarkerClusterer, google */

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { loadGoogleMapLibWithApi } from "./google_api_services";
import { _t } from "@web/core/l10n/translation";

const { useRef, useEffect, useState, onMounted, onWillStart, onWillUnmount } = owl;

export class GoogleMapField extends CharField {
    static template = "boat_booking.GoogleMapField";
    static components = { ...CharField.components };
    static props = {
        ...standardFieldProps,
        autocomplete: { type: String, optional: true },
        isPassword: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
        dynamicPlaceholder: { type: Boolean, optional: true },
        default_lt: { type: Number, optional: true },
        default_lg: { type: Number, optional: true },
    };

    setup() {
        super.setup();
        this.mapPinRef = useRef("map_pin_ref");
        this.mapPopupRef = useRef("map_popup_ref");
        this.mapRef = useRef("geomap_ref");
        this.inputRef = useRef("input");
        this.mapAddressInputRef = useRef("map_address_input");
        this.apiInputRef = useRef("api_input");
        this.notificationService = useService("notification");
        this.orm = useService("orm");
        const { default_lt: lat, default_lg: long } = this.props;

        this.state = useState({
            isGeoMapShowing: false,
            lat: lat || 10.8231,
            long: long || 106.6297,
        });

        useEffect(
            (ref) => {
                if (!ref) return;
                function toggleMap(event) {
                    const pinEl = this.mapPinRef.el;
                    const mapAddressInputEl = this.mapAddressInputRef.el;
                    const { el } = this.mapRef;
                    const { target } = event;

                    if (!this.state.isGeoMapShowing && target === pinEl) {
                        this.mapPopupRef.el.classList.add("active");
                        this.state.isGeoMapShowing = true;
                        return;
                    }

                    if (!el?.contains(target) && target !== mapAddressInputEl) {
                        this.mapPopupRef.el?.classList.remove("active");
                        this.state.isGeoMapShowing = false;
                    }
                }

                document.addEventListener("click", toggleMap.bind(this));
                return () => {
                    document.removeEventListener("click", toggleMap.bind(this));
                };
            },
            () => [this.mapPinRef]
        );

        onWillStart(() => this.ensureGoogleMapLibLoaded());
        onMounted(() => {
            if (!this.googleMapLoaded) return;

            this.initMapComponents();
        });

        onWillUnmount(() => {
            if (!this.googleMapLoaded) return;

            this.removeMapEvents();
        });
    }

    showApiInput() {
        this.state.isShowingApiInput = true;
    }

    hideApiInput() {
        this.state.isShowingApiInput = false;
    }

    inputApiKey(event) {
        event.preventDefault();
        this.apiKey = this.apiInputRef.el.value;
        this.hideApiInput();

        // reload google map lib after input api key
        this.loadGoogleMapLib(true);
    }

    saveApiKey() {
        try {
            this.orm.call("google.api.key.manager", "set_google_api_key", [this.apiKey]);
        } catch (error) {
            this.notificationService.add(
                _t("Could not save Google Map API key in System Parameters"),
                {
                    title: _t("API KEY not saved!"),
                    sticky: true,
                }
            );
        }
    }

    closePopup(event) {
        event.preventDefault();
        this.hideApiInput();
    }

    ensureGoogleMapLibLoaded() {
        if (typeof google !== "undefined" && google.maps) {
            console.info("Google Maps library is already loaded");
            this.googleMapLoaded = true;
        } else {
            console.info("Google Maps library is not loaded, loading now...");
            this.loadGoogleMapLib();
        }
    }

    async getGoogleMapApiKey() {
        try {
            const apiKey = await this.orm.call("google.api.key.manager", "get_google_api_key", []);
            if (!apiKey) throw new Error("No GoogleMap API Key found");

            return apiKey;
        } catch (error) {
            this.showApiInput();
            this.notificationService.add(
                _t("Could not found Google Map API key in System Parameters"),
                {
                    title: _t("API KEY not found!"),
                    sticky: true,
                }
            );
            return false;
        }
    }

    async loadGoogleMapLib(isReload = false) {
        try {
            if (!this.apiKey) this.apiKey = await this.getGoogleMapApiKey();
            if (!this.apiKey) return;

            await loadGoogleMapLibWithApi(this.apiKey);
            this.saveApiKey();
            this.googleMapLoaded = true;
            if (isReload)
                this.notificationService.add(_t("Google Map API loaded successfully."), {
                    title: _t("Google Map API loaded, please reload the page."),
                    type: "success",
                });
        } catch (error) {
            this.googleMapLoaded = false;
            this.notificationService.add(_t("Failed Loading Google Map API."), {
                title: _t("Loading Google Map Error", error),
                type: "danger",
                sticky: true,
            });
        }
    }

    async initMapComponents() {
        if (!this.googleMapLoaded) return;

        this.initMap();
        this.initAutocomplete();
        await this.initMarkerAndInfoWindow();
        this.handleInputAddressChanged(this.inputRef.el?.value);
    }

    initMap() {
        if (!this.inputRef.el || !this.mapAddressInputRef.el) return;

        this.geocoder = new google.maps.Geocoder();
        const center = new google.maps.LatLng(this.state.lat, this.state.long);
        const myOptions = {
            zoom: 14,
            center,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapId: "DEMO_MAP_ID",
        };
        this.map = new google.maps.Map(this.mapRef.el, myOptions);
    }

    initAutocomplete() {
        if (!this.map) this.initMap();

        const setElementAutocomplete = (element) => {
            element.setAttribute("autocomplete", "off");
            const autocomplete = new google.maps.places.Autocomplete(element, {
                types: ["geocode"],
            });

            autocomplete.bindTo("bounds", this.map);

            autocomplete.setFields([
                "address_component",
                "geometry",
                "icon",
                "name",
                "formatted_address",
            ]);

            return autocomplete.addListener("place_changed", () => {
                const place = autocomplete.getPlace();
                this.handleInputAddressChanged(place?.formatted_address);
            });
        };
        if (this.inputRef.el) setElementAutocomplete(this.inputRef.el);
        if (this.mapAddressInputRef.el) setElementAutocomplete(this.mapAddressInputRef.el);
    }

    removeAutocomplete() {
        if (this.inputRef?.el) google.maps.event.clearInstanceListeners(this.inputRef.el);
    }

    async initMarkerAndInfoWindow() {
        const position = new google.maps.LatLng(this.state.lat, this.state.long);
        const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

        this.marker = new AdvancedMarkerElement({
            map: this.map,
            position,
            gmpDraggable: true,
            title: "Position",
        });

        this.infoWindow = new google.maps.InfoWindow({
            content: "",
            size: new google.maps.Size(150, 50),
        });

        this.marker.addListener("dragend", (_) => {
            const position = this.marker.position;
            this.updateAddressFromLocation(position);
            this.updateStatePosition();
        });
    }

    removeMapEvents() {
        if (!this.googleMapLoaded) return;

        this.removeAutocomplete();
    }

    handleInputAddressChanged(address) {
        if (!address) return;

        this.geocoder.geocode({ address }, (results, status) => {
            if (status !== google.maps.GeocoderStatus.OK) return;

            const { geometry, formatted_address } = results[0];
            this.marker.position = geometry.location;
            this.updateCurrentAddress(formatted_address);
            this.updateStatePosition();
        });
    }

    updateAddressFromLocation(latLng) {
        this.geocoder.geocode({ latLng }, (results, status) => {
            let address = "Unable to determine the location for the provided address.";
            if (status === google.maps.GeocoderStatus.OK) {
                address = results[0].formatted_address;
            }

            this.updateCurrentAddress(address);
        });
    }

    updateStatePosition() {
        this.state.lat = this.marker.position.lat;
        this.state.long = this.marker.position.lng;
        this.map.setCenter({ lat: this.state.lat, lng: this.state.long });
    }

    async updateCurrentAddress(formatted_address) {
        this.props.record.data[this.props.name] = formatted_address;
        await this.updateAddressFieldValue(formatted_address);

        if (!this.marker) return;

        this.marker.formatted_address = formatted_address;
        this.infoWindow.setContent(formatted_address);
        this.infoWindow.open(this.map, this.marker);
    }

    async updateAddressFieldValue(value) {
        const record = this.props.record;
        await record.update({ [this.props.name]: value });
        return record.save();
    }
}

export const googleMapField = {
    ...CharField,
    component: GoogleMapField,
    extractProps: ({ attrs, options }) => ({
        default_lt: options.default_lt,
        default_lg: options.default_lg,
    }),
};

registry.category("fields").add("google_map_field", googleMapField);
