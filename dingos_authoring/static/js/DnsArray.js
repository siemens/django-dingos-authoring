/**
 * This is the MANTIS DNS field for Alpaca. It inherits functionality
 * from MantisRefField which adds the possibility to query existing
 * object references
 */

(function($) {

    var Alpaca = $.alpaca;

    Alpaca.Fields.MantisDnsArray = Alpaca.Fields.MantisRefField.extend(
    //Alpaca.Fields.MantisDnsArray = Alpaca.Fields.ArrayField.extend(
    /**
     * @lends Alpaca.Fields.MantisDnsArray.prototype
     */
    {
        /**
         * @constructs
         * @augments Alpaca.Fields.TextAreaField
         *
         * @class JSON control for chunk of text.
         *
         * @param {Object} container Field container.
         * @param {Any} data Field data.
         * @param {Object} options Field options.
         * @param {Object} schema Field schema.
         * @param {Object|String} view Field view.
         * @param {Alpaca.Connector} connector Field connector.
         * @param {Function} errorCallback Error callback.
         */
        constructor: function(container, data, options, schema, view, connector, errorCallback) {
            this.base(container, data, options, schema, view, connector, errorCallback);
        },

        setup: function() {
            this.base();

            // Default object type we are trying to complete
            this.ref_type='dns';
            // Define our DNS schema

            this.schema.items = {
                "title": "Some weird indicator",
                "type": "object",
                "properties": {
                    "name1": {
                        "title": "name1"
                    },
                    "name2": {
                        "title": "name2"
                    }
                }
            }

        },

    });

    Alpaca.registerFieldClass("mantis_dns_array", Alpaca.Fields.MantisDnsArray);
    Alpaca.registerDefaultSchemaFieldMapping("mantis_dns_array", "mantis_dns_array");
})(jQuery);

