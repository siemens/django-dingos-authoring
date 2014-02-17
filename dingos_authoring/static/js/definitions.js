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
        }
    });
    Alpaca.registerFieldClass("mantis_array_dns", Alpaca.Fields.MantisDnsArray);
    Alpaca.registerDefaultSchemaFieldMapping("mantis_array_dns", "mantis_array_dns");





    /**
     * This field provides a 'related indicators' field
     */
    Alpaca.Fields.MantisRelatedIndicatorArray = Alpaca.Fields.MantisRefArray.extend({
        constructor: function(container, data, options, schema, view, connector, errorCallback) {
            this.base(container, data, options, schema, view, connector, errorCallback);
        },
        setup: function() {
            this.base();
            this.ref_type='related_indicator';
	    this.ref_only = true;
        }

    });
    Alpaca.registerFieldClass("mantis_array_rel_indicator", Alpaca.Fields.MantisRelatedIndicatorArray);
    Alpaca.registerDefaultSchemaFieldMapping("mantis_array_rel_indicator", "mantis_array_rel_indicator");






})(jQuery);

