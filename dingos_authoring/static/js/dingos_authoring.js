$(function() {


    function s4() {
	return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    };
    function guid_gen() {
	return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
    };
    function uniqueArray(array) {
	return $.grep(array, function(el, index) {
            return index == $.inArray(el, array);
	});
    }




    var builder = function(){
	var instance = this;

	this.pool_list = $('#dda-pool-list');
	this.pool_elements = $('#dda-pool-elements');
	this.pool_elements_templates = $('#dda-observable-template-pool > div');
	this.pool_indicator_templates = $('#dda-indicator-template-pool > div');
	this.observable_pool = $('#dda-observable-pool');
	this.indicator_list = $('#dda-indicator-list');
	this.package_indicators = $('#dda-package-indicators');

	this.element_registry = {};
	this.indicator_registry = {};


	// Initializes the pool elements
	this.init_pool_elements = function(){
	    $.each(instance.pool_elements_templates, function(i,v){
		var div = $('<div class="dda-add-element clearfix" ></div>');
		div.append(
			$('<button>').addClass('dda-obs-add pull-right').html('Add').click(function(){
			    instance.addElementToPool(v);
			})
		);

		var title = $('#id_xsi_type',v).val();
		var description = '';
		
		div.append('<h3>'+title+'</h3>');
		div.append('<p>'+description+'</p>');

		instance.pool_elements.append(div);
	    });

	};
	this.init_pool_elements();


	// Initializes the indicator tab.
	this.init_indicator_tab = function(){

	    // $.each(instance.pool_indicator_templates, function(i,v){
	    // 	$('#dda-indicator-add-btn-menu').append(
	    // 	    $('<li></li>').append(
	    // 		$('<a href="#"></a>').html($(v).data('title')).click(function(){
	    // 		    instance._add_indicator(v);
	    // 		})
	    // 	    )
	    // 	);		
	    // });	    
	    // $('#dda-indicator-add-btn-menu').menu();

	    $('#dda-indicator-add-btn').click(function(){
		//$('#dda-indicator-add-btn-menu').toggle();
		instance._add_indicator();
	    });

	};
	this.init_indicator_tab();

	// adds an indicator to the pool. gets passed the template of the indicator.
	// presented as function so we can add an indicator on demand if a user drops an observable in a package
	// if v is not passed, the function uses the first found template
	this._add_indicator = function(v){
	    var auto_gen = false;
	    if(!v){ // When user clicked the button
		v = instance.pool_indicator_templates.first();
		auto_gen = true;
	    }
	    var guid = guid_gen();
	    var div = $('<div class="dda-add-element"></div>');
	    div.append(
		$('<button></button>').html('Remove').addClass("dda-ind-remove pull-right").click(function(){
		    instance.removeIndicator(guid);
		})
	    );
	    div.append('<h3>' + guid + '</h3>');
	    var _pc_el = $(v).clone().attr('id', guid);
	    div.append(_pc_el);
	    instance.indicator_list.append(div);

	    instance.indicator_registry[guid] = {
		template_id: $(v).attr('id'),
		element: _pc_el,
		pool_element: div,
		title: guid,
		description: $(v).data('description'),
		observables: []
	    };

	    if(!auto_gen){
		instance.renderPackage();
		$('#dda-indicator-add-btn-menu').toggle();
	    }else{
		return guid;
	    }
	};
	this.removeIndicator = function(guid){
	    instance.indicator_registry[guid].pool_element.remove();
	    delete instance.indicator_registry[guid];
	    instance.renderPackage();
	};


	// Adds an element to the observable pool. Gets passed the template element
	this.addElementToPool = function(element){
	    //Some new id
	    guid = guid_gen();
	    var div = $('<div class="dda-add-element clearfix" ></div>').data('id', guid);
	    var new_elem = $(element).clone().attr('id', guid);
	    var _oi = new_elem.find('#id_object_id',new_elem);
	    //Prepend namespace and append guid; TODO: namespace?
	    _oi.val('siemens_cert' + _oi.val() + guid);
	    var _pc_el = $('<div class="dda-pool-element">').append(new_elem);

	    div.append(
		$('<button>').addClass('dda-obs-remove pull-right').html('Remove').click(function(){
		    instance.removeElementFromPool(guid);
		})
	    ).append(
		$('<button>').addClass('dda-obs-add pull-right').html('Toggle').click(function(){
		    _pc_el.toggle();
		})
	    );

	    var title = $('#id_xsi_type', element).val();
	    var description = '';

	    div.append('<h3>'+guid +'</h3><p>'+title+'</p>');
	    div.append( _pc_el );
	    instance.pool_list.prepend(div);

	    
	    instance.element_registry[guid] = {
	    	template_id: $(element).attr('id'),
		element: _pc_el,
		pool_element: div,
		title: title,
		description: description
	    };
	};

	this.removeElementFromPool = function(guid){
	    instance.element_registry[guid].pool_element.remove();
	    delete instance.element_registry[guid];
	};

	this.init_observable_pool = function(){
	    instance.observable_pool.html('');
	    $.each(instance.element_registry, function(i,v){
		var div = $('<div class="dda-add-element clearfix" ></div>').data('id', i);
		div.append('<h3>'+v.title+'</h3>');
		div.append('<p>'+i+'</p>');

		div.draggable({
		    "helper": "clone",
		    "zIndex": 300,
		    "refreshPositions": true,
		    "start": function(event, ui) {
			$(".dda-package-indicators_dropzone").addClass("dda-dropzone-highlight");
		    },
		    "stop": function(event, ui) {
			$(".dda-package-indicators_dropzone").removeClass("dda-dropzone-highlight");
		    }
		});

		instance.observable_pool.append(div);
	    });
	    instance.renderPackage();
	};



	// Renders the indicators on the package tab based on the object registries
	this.renderPackage = function(){
	    // First clear all entries
	    instance.package_indicators.html('');

	    // Add a dropzone element for dropping observables on non-indicators
	    instance.package_indicators.append($('<div></div>').addClass('dda-package-indicators_dropzone'));

	    // Iterate over the registred indicators
	    $.each(instance.indicator_registry, function(indicator_guid, indicator_element){
		var div = $('<div class="dda-add-element"></div>');
		
		// Put the indicator title, use the 'title' input, or if empty, the guid
		title = $('#id_title', indicator_element.element).val();
		if(title=='')
		    title = 'Indicator: ' + indicator_element.title
		div.append('<h3>'+title+'</h3>');

		// Add the indicator-guid to the dropzone so we know it when dropping onto
		var refs = $('<div></div>').addClass('dda-package-indicators_dropzone').data('id', indicator_guid);
		$.each(indicator_element.observables, function(i,v){
		    refs.append($('<div></div>').html(v));
		});
		div.append(refs);
		instance.package_indicators.append(div);
	    });

	    instance.package_indicators.find('.dda-package-indicators_dropzone').droppable({
                "tolerance": "touch",
                "drop": function( event, ui ) {
		    var draggable = $(ui.draggable);
		    var observable_id = $(draggable).data('id');
		    var indicator_id = $(this).data('id');
		    if(!indicator_id){ //if we drop on a non-indicator, we generate one
			indicator_id = instance._add_indicator();
		    }
		    instance.indicator_registry[indicator_id].observables.push(observable_id);
		    instance.indicator_registry[indicator_id].observables = uniqueArray(instance.indicator_registry[indicator_id].observables);
		    instance.renderPackage();
		},
                "over": function (event, ui ) {
		    $(event.target).addClass("dda-dropzone-hover");
                },
                "out": function (event, ui) {
		    $(event.target).removeClass("dda-dropzone-hover");
                }
	    });
	};


	return instance;
    };
    var b = builder();

    $('#dda-container-tabs').tabs({
	active: 1,
	activate:function(event,ui){
	    if(ui.newTab.index()==0){
		b.init_observable_pool();
	    }
        }
    });

});
