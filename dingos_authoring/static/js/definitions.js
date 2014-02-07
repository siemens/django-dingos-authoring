(function($) {
    var Alpaca = $.alpaca;



    /**
     * This field provides an 'DNS' type array
     */
    Alpaca.Fields.MantisDnsArray = Alpaca.Fields.MantisRefArray.extend({
        constructor: function(container, data, options, schema, view, connector, errorCallback) {
            this.base(container, data, options, schema, view, connector, errorCallback);
        },
        setup: function() {
            this.base();
            this.ref_type='dns';

            // Define our DNS schema; This just renders an input field
            // this.schema.items = {
            //     "title": "Domain Name Indicator",
            // }
        },

    });
    Alpaca.registerFieldClass("mantis_array_dns", Alpaca.Fields.MantisDnsArray);
    Alpaca.registerDefaultSchemaFieldMapping("mantis_array_dns", "mantis_array_dns");






    /**
     * This field provides a 'related indicators' field
     */
    Alpaca.Fields.MantisRelatedIndicatorField = Alpaca.Fields.MantisRefField.extend({
        constructor: function(container, data, options, schema, view, connector, errorCallback) {
            this.base(container, data, options, schema, view, connector, errorCallback);
        },
        setup: function() {
            this.base();
            this.ref_type='related_indicator';
	    this.ref_only = true;
        },

    });
    Alpaca.registerFieldClass("mantis_field_rel_indicator", Alpaca.Fields.MantisRelatedIndicatorField);
    Alpaca.registerDefaultSchemaFieldMapping("mantis_field_rel_indicator", "mantis_field_rel_indicator");






})(jQuery);

