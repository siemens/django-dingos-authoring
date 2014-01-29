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

	    // Default ref type
	    this.ref_type = 'any'; 
	    
	    // This is where we save the states of the toggable elements
	    this.states = {};

	    //TODO: init this.data? ;; Alpaca.isArray(this.data) Alpaca.isObject(this.data) ?
	    
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
			    // Swap elements in dom 
			    // Only works because elements are next to each other
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
                var itemToolbarTemplateDescriptor = this.view.getTemplateDescriptor("arrayItemToolbarTgl");
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
		    $('.dda-ref-toggles input', toolbarElem).change(function(){
			_this.toggle_state(id);
		    });
		    

		    toolbarElem.prependTo(containerElem);
                }
            }
        },
	_bind_ac: function(el, id){
	    var _this = this;

	    //TODO: on type "any" we should render a category for results. http://jqueryui.com/autocomplete/#categories

	    var ac_trigger = function(event, ui){
		if(ui.item){
		    $('#dda-input-ref-span_'+id).html(ui.item.label);
		}else{
		    $('#dda-input-ref-span_'+id).html('');
		    $(this).val('');
		}
		_this.renderValidationState(true);
	    }

	    /* bind the autocomplete to el */
	    el.autocomplete({
		source: function( request, response ) {
		    $.ajax({
			url: "ref/",
			dataType: "json",
			data: {
			    type: _this.ref_type,
			    q: request.term
			},
			success: function( data ) {
			    //TODO: test for data.success
			    response( $.map( data.result, function( item ) {
				return {
				    label: item.title,
				    value: item.value
				}
			    }));
			}
		    });
		},
		autoFocus: true,
		select: function(event, ui){
		    ac_trigger.call(this, event, ui);
		},
		change: function(event, ui){
		    ac_trigger.call(this, event, ui);
		}
	    });
	},
	create_ref_element: function(id, parent){
	    var _this = this;

	    var ap = $('<div></div>').alpaca({
		"schema": {},
		"options": {
		    "name": parent.preName + '_ref',
		    "placeholder": "Object Reference",
		    // We are not gonna use the internal typeahead helper...
		}
	    });

	    ap.find('input').after('<span id="dda-input-ref-span_'+id+'"></span>');

	    return ap;
	},
	toggle_state: function(id){
	    var _this = this;
	    var itm = _this.childrenById[id];

	    if(!(id in _this.states)){
		//Init the element for toggling
		var _tmp = _this.create_ref_element(id, itm);
		var _tmp_a = _tmp.alpaca();
		_tmp_a.propertyId = 'ref';
		_tmp_a.parent = _this;

		_this.states[id] = {
		    'elem': _tmp,
		    'field': _tmp_a.field,
		    'fieldContainer': _tmp_a.fieldContainer,
		    'fieldContainerJQ': $(_tmp_a.fieldContainer),
		    'children': [],
		    'childrenById': {},
		    'childrenByPropertyId': {},
		    'ref_visible': false
		};
		_this.states[id]['children'].push(_tmp_a);
		_this.states[id]['childrenById'][_tmp_a.id] = _tmp_a;
		_this.states[id]['childrenByPropertyId']['ref'] = _tmp_a;
	    }
	    
	    var old_field = itm.field;
	    var old_fieldContainer = itm.fieldContainer;
	    var old_children = itm.children;
	    var old_childrenById = itm.childrenById;
	    var old_childrenByPropertyId = itm.childrenByPropertyId;

	    var ns = _this.states[id];

	    itm.field = ns.field; 
	    
	    // Remove the old elements (in the fieldContainer) from the DOM and keep attached events
	    // detachAndReplaceWith is a custom jQuery plugin which is pretty much the same as the 
	    // source of stock-replaceWith but with detach() instead of remove()
	    var old_fieldContainerJQ = itm.fieldContainer.detachAndReplaceWith(ns.fieldContainerJQ);
	    itm.fieldContainer = ns.fieldContainer;	    
	    itm.children = ns.children;
	    itm.childrenById = ns.childrenById;
	    itm.childrenByPropertyId = ns.childrenByPropertyId;

	    ns.field = old_field;
	    ns.fieldContainer = old_fieldContainer;
	    ns.fieldContainerJQ = old_fieldContainerJQ;
	    ns.children = old_children;
	    ns.childrenById = old_childrenById;
	    ns.childrenByPropertyId = old_childrenByPropertyId;
	    
	    ns.ref_visible = !ns.ref_visible;
	    if(ns.ref_visible){
		_this._bind_ac(itm.fieldContainer.find('input'), id);
	    }

	    _this.renderValidationState(true);
	    _this.updateChildrenPathAndName(_this);
	},
    });
    Alpaca.registerTemplate("arrayItemToolbarTgl", '<div class="ui-widget-header ui-corner-all alpaca-fieldset-array-item-toolbar">{{each(k,v) buttons}}<button class="alpaca-fieldset-array-item-toolbar-icon alpaca-fieldset-array-item-toolbar-${v.feature}">${v.label}</button>{{/each}}<div class="dda-array-toolbar-container-right"><div class="dda-ref-toggles"><input id="dda-ref-tgl1-${id}" type="radio" name="radio-${id}" value="dda-ref-regular" checked="checked"><label for="dda-ref-tgl1-${id}">Regular</label><input id="dda-ref-tgl2-${id}" type="radio" name="radio-${id}" value="dda-ref-reference"><label for="dda-ref-tgl2-${id}">Reference</label></div></div></div>');

})(jQuery);

