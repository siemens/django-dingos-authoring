/**
 * This is the MANTIS Rerference field for Alpaca. It inherits functionality
 * from MantisRefField which adds the possibility to query existing
 * object references
 */

(function($) {

    var Alpaca = $.alpaca;

    Alpaca.Fields.MantisRefField = Alpaca.Fields.ArrayField.extend(
    /**
     * @lends Alpaca.Fields.MantisRefField.prototype
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

	    // Override the sticky toolbar
	    this.options.toolbarSticky = true;
	    // Override the collapsible feature
	    this.options.collapsible = false;

	    
	    
	    
	    // This is where we save the states of the toggable elements
	    this.states = {};

	    
        },
	/**
	 * Moves child up or down
	 * @param {String} fromId Id of the child to be moved.
	 * @param {Boolean} isUp true if the moving is upwards
	 */
        moveItem: function(fromId, isUp) {
            var _this = this;
            if (this.childrenById[fromId]) {
                // do the loop
                $.each(this.children, function(index, val) {
                    if (val.getId() == fromId) {
                        var toIndex;
                        if (isUp === true) {
                            toIndex = index - 1;
                            if (toIndex < 0) {
                                toIndex = _this.children.length - 1;
                            }
                        } else {
                            toIndex = index + 1;
                            if (toIndex >= _this.children.length) {
                                toIndex = 0;
                            }
                        }
                        if (_this.children[toIndex]) {
			    var toId = _this.children[toIndex].getId();
                            var fromContainer = $('#' + fromId + '-item-container');
                            var toContainer = $('#' + toId + '-item-container');
			    // Swap in dom -- this only workds because elements are next to each other
			    if(isUp == true)
				toContainer.before(fromContainer);
			    else
				fromContainer.before(toContainer);
			    

			    // Swap in the children array
                            var tmp = _this.children[index];
                            _this.children[index] = _this.children[toIndex];
                            _this.children[toIndex] = tmp;
			    
			    // Regenerate names
                            _this.updatePathAndName();
                            return false;
                            // var toId = _this.children[toIndex].getId();
                            // var fromContainer = $('#' + fromId + '-item-container');
                            // var toContainer = $('#' + toId + '-item-container');
                            // _this.reRenderItem(_this.children[index], toContainer);
                            // _this.reRenderItem(_this.children[toIndex], fromContainer);
                            // var tmp = _this.children[index];
                            // _this.children[index] = _this.children[toIndex];
                            // _this.children[toIndex] = tmp;
                            // _this.updatePathAndName();
                            // return false;
                        }
                    }
                });
            }
        },
	/**
	 * Renders array item toolbar.
	 *
	 * @param {Object} containerElem Toolbar container.
	 */
        renderToolbar: function(containerElem) {
            var _this = this;

            if (!this.options.readonly) {
                var id = containerElem.attr('alpaca-id');
                var fieldControl = this.childrenById[id];
                var itemToolbarTemplateDescriptor = this.view.getTemplateDescriptor("arrayItemToolbar");
                if (itemToolbarTemplateDescriptor) {

                    // Base buttons : add & remove
                    var buttonsDef = [
                        {
                            feature: "add",
                            icon: _this.addIcon,
                            label: (_this.options.items && _this.options.items.addItemLabel) ? _this.options.items.addItemLabel : "Add Item",
                            clickCallback: function(id, arrayField) {

                                _this.resolveItemSchemaOptions(function(schema, options) {

                                    var newContainerElem = arrayField.addItem(containerElem.index() + 1, schema, options, null, id, true);
                                    arrayField.enrichElements(newContainerElem);

                                });

                                return false;
                            }
                        },
                        {
                            feature: "remove",
                            icon: _this.removeIcon,
                            label: (_this.options.items && _this.options.items.removeItemLabel) ? _this.options.items.removeItemLabel : "Remove Item",
                            clickCallback: function(id, arrayField) {
                                arrayField.removeItem(id);
                            }
                        }
                    ];

                    // Optional buttons : up & down
                    if ((_this.options.items && _this.options.items.showMoveUpItemButton)) {
                        buttonsDef.push({
                            feature: "up",
                            icon: _this.upIcon,
                            label: (_this.options.items && _this.options.items.moveUpItemLabel) ? _this.options.items.moveUpItemLabel : "Move Up",
                            clickCallback: function(id, arrayField) {
                                arrayField.moveItem(id, true);
                            }
                        });
                    }

                    if ((_this.options.items && _this.options.items.showMoveDownItemButton)) {
                        buttonsDef.push({
                            feature: "down",
                            icon: _this.downIcon,
                            label: (_this.options.items && _this.options.items.moveDownItemLabel) ? _this.options.items.moveDownItemLabel : "Move Down",
                            clickCallback: function(id, arrayField) {
                                arrayField.moveItem(id, false);
                            }
                        });
                    }

                    // Extra buttons : user-defined
                    if (_this.options.items && _this.options.items.extraToolbarButtons) {
                        buttonsDef = $.merge(buttonsDef,_this.options.items.extraToolbarButtons);
                    }

                    var toolbarElem = _this.view.tmpl(itemToolbarTemplateDescriptor, {
                        "id": id,
                        "buttons": buttonsDef
                    });
                    if (toolbarElem.attr("id") === null) {
                        toolbarElem.attr("id", id + "-item-toolbar");
                    }

                    // Process all buttons
                    for (var i in buttonsDef) {
                        (function(def) { // closure to prevent "def" leaking
                            var el = toolbarElem.find('.alpaca-fieldset-array-item-toolbar-'+def.feature);
                            el.click(function(e) {return def.clickCallback(id, _this, e);});
                            if (_this.buttonBeautifier) {
                                _this.buttonBeautifier.call(_this,el, def.icon);
                            }
                        })(buttonsDef[i]);
                    }
		    
		    // Beautify toggles
		    $('.dda-ref-toggles', toolbarElem).buttonset();

		    // Register toggle handlers
		    $('.dda-ref-toggles input', toolbarElem).click(function(){
			_this.toggle_state(id);
		    });
		    

		    toolbarElem.prependTo(containerElem);
                }
            }
        },
	create_ref_element: function(id, parent){
	    ref_template = '<div id="dda-ref-input-'+id+'"></div>';

	    var ap = $(ref_template).alpaca({
		"schema": {"type" : "string"},
		"render": function(fc, cb){ /* fieldControl, Callback */
		    //console.log(fc);
		    // fc.id = id;
		    // fc.parent = parent
		    // fc.path = parent.path + '['+ id +']';
		    if (cb){
                        cb();
                    }
		}
	    });

	    return ap;
	},
	toggle_state: function(id){
	    var _this = this;

	    if(!(id in _this.states)){
		//Init the element for toggling
		console.log(_this.create_ref_element(id, _this).alpaca())
	    }
	    
	    //TODO: toggle me!
	},
    });
    Alpaca.registerTemplate("arrayItemToolbar", '<div class="ui-widget-header ui-corner-all alpaca-fieldset-array-item-toolbar">{{each(k,v) buttons}}<button class="alpaca-fieldset-array-item-toolbar-icon alpaca-fieldset-array-item-toolbar-${v.feature}">${v.label}</button>{{/each}}<div class="dda-array-toolbar-container-right"><div class="dda-ref-toggles"><input id="dda-ref-tgl1-${id}" type="radio" name="radio-${id}" value="dda-ref-regular" checked="checked"><label for="dda-ref-tgl1-${id}">Regular</label><input id="dda-ref-tgl2-${id}" type="radio" name="radio-${id}" value="dda-ref-reference"><label for="dda-ref-tgl2-${id}">Reference</label></div></div></div>');

})(jQuery);

