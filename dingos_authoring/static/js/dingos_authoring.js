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


    $.fn.serializeObject = function()
    {
	var o = {};
	var a = this.serializeArray();
	$.each(a, function() {
	    if (o[this.name]) {
		if (!o[this.name].push) {
		    o[this.name] = [o[this.name]];
		}
		o[this.name].push(this.value || '');
	    } else {
		o[this.name] = this.value || '';
	    }
	});
	return o;
    };


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
	    var _oi = _pc_el.find('#id_indicator_id');
	    //Prepend namespace and append guid; TODO: namespace?
	    _oi.val('siemens_cert' + _oi.val() + guid);
	    div.append(_pc_el);
	    instance.indicator_list.prepend(div);

	    instance.indicator_registry[guid] = {
		template: $(v),
		element: _pc_el,
		pool_element: div,
		title: guid,
		description: $(v).data('description'),
		observables: []
	    };

	    if(!auto_gen){
		//instance.renderPackage();
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
	    var _oi = new_elem.find('#id_object_id');
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
	    div.find('button').button();
	    instance.pool_list.prepend(div);

	    
	    instance.element_registry[guid] = {
		object_id: guid,
		relations: [],
	    	template: $(element),
		element: _pc_el,
		pool_element: div,
		title: title,
		description: description,
		type: $(element).find('#id_xsi_type').val()
	    };
	};

	this.removeElementFromPool = function(guid){
	    instance.element_registry[guid].pool_element.remove();
	    delete instance.element_registry[guid];
	};
	
	this.getElementName = function(v, def){
	    desc = '';
	    if(v.type == 'FileObj:FileObjectType')
		desc = $(v.element).find('#id_file_name').val();
	    else if(v.type == 'EmailMessageObj:EmailMessageObjectType')
		desc = $(v.element).find('#id_subject').val();
	    else if(v.type == 'DNSRecordObj:DNSRecordObjectType')
		desc = $(v.element).find('#id_domain_name').val();

	    if(desc=='')
		desc = def;

	    return desc	    
	};

	this.init_observable_pool = function(){
	    instance.observable_pool.html('');
	    $.each(instance.element_registry, function(i,v){
		var div = $('<div class="dda-add-element clearfix" ></div>').data('id', i);
		div.append('<h3>'+v.title+'</h3>');
		desc = instance.getElementName(v, i);
		div.append('<p>'+desc+'</p>');

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
	    instance.package_indicators.append($('<div><p>Drop here to create new indicator</p></div>').addClass('dda-package-indicators_dropzone dda-package_top_drop'));

	    // Iterate over the registred indicators
	    $.each(instance.indicator_registry, function(indicator_guid, indicator_element){
		var div = $('<div class="dda-add-element"></div>');
		
		// Put the indicator title, use the 'title' input, or if empty, the guid
		title = $('#id_indicator_title', indicator_element.element).val();
		if(title=='')
		    title = 'Indicator: ' + indicator_element.title
		div.append('<h3>'+title+'</h3>');

		// Add the indicator-guid to the dropzone so we know it when dropping onto
		var refs = $('<div></div>').addClass('dda-package-indicators_dropzone').data('id', indicator_guid);
		$.each(indicator_element.observables, function(i,v){
		    desc = instance.getElementName(instance.element_registry[v], v);
		    refs.append($('<div></div>').html(desc));
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

	    //Register generate button handler
	    $('#dda-stix-generate').off('click').on('click', function(){
		//generated-time
		$('input[name="stix_produced_time"]', '#dda-stix-meta').val(Date.now());
		var stix_base = {
		    'stix_header': $('#dda-stix-meta').find('input, select, textarea').serializeObject(),
		    'incidents': [],
		    'indicators': [],
		    'observables': []
		}
		$.each(instance.indicator_registry, function(i,v){
		    //stix_base.indicators[i] = $(v.element).find('input, select, textarea').serializeObject();
		    //stix_base.indicators[i].observables = v.observables;
		    var tmp = $(v.element).find('input, select, textarea').serializeObject();
		    tmp.related_observables = v.observables;
		    tmp.related_observables_condition = 'AND';
		    stix_base.indicators.push(tmp);
		});

		$.each(instance.element_registry, function(i,v){
		    //stix_base.observables[i] = $(v.element).find('input, select, textarea').serializeObject();
		    var tmp = {
			'observable_id': i,
			'observable_description': '',
			'related_observables': {},
			'observable_properties': $(v.element).find('input, select, textarea').serializeObject()
		    }
		    stix_base.observables.push(tmp);
		});

		result = JSON.stringify(stix_base, null, "    ");
		console.log(result);
		alert(result);

		return false;
	    });

	};


	// this.draw_d3 = function(){
	//     $('#relation-pane').html('');
	//     var width = $('#relation-pane').width();
	//     height = $('#relation-pane').height();

	//     var data_set = [];
	//     $.each(instance.element_registry, function(i,v){
	//     	data_set.push(v);
	//     });
	    

	//     var layout = d3.layout.force()
	// 	.charge(-100)
	// 	.linkDistance(function(link, index){
	// 	    //TODO: dynamic distance?
	// 	    return 100;
	// 	})
	// 	.size([width, height]);

	//     var svg = d3.select("#relation-pane").append("svg")
	// 	.attr("width", width)
	// 	.attr("height", height);

	//     var drag = d3.behavior.drag()
	// 	.on("dragstart", function( d, i) {
	// 	    //console.log(d);
	// 	})
	// 	.on("dragend", function(d) {
	// 	    var source = d;
	// 	    var target = d3.select( 'circle.node.node-hover');
	// 	    var rel = {label: '', target: target.data()[0].object_id};
	// 	    console.log(source.relations);
	// 	    source.relations.push(rel);
	// 	    console.log(source.relations);
	// 	    instance.draw_d3();
	// 	});


	//     var transitions = function() {
	// 	return data_set.reduce( function( initial, element) {
	// 	    return initial.concat( 
	// 		element.relations.map( function( relation) {
	// 		    var src, tgt;
	// 		    $.each(data_set, function(i,v){
	// 			if(v.object_id == relation.target)
	// 			    tgt=i;

	// 			if(v.object_id == element.object_id)
	// 			    src = i;
	// 		    });
	// 		    return { source : src, target : tgt};
	// 		})
	// 	    );
	// 	}, []);
	//     };
	//     links = transitions();

	//     layout
	//     	.nodes(data_set)
	//     	.links(links)
	//     	.start();

	//     var link = svg.selectAll(".link")
	//     	.data(links)
	//     	.enter().append("line")
	//     	.attr("class", "link")
	//     	.style("stroke-width", 3);
	    
	//     var node = svg.selectAll(".node")
	// 	.data(data_set)
	// 	.enter().append("circle")
	// 	.attr("class", "node")
	// 	.attr("r", 10)
	// 	.on("mouseover", function(){
	// 	    d3.select(this).classed( "node-hover", true);
	// 	})
	// 	.on("mouseout", function() { 
	// 	    d3.select(this).classed( "node-hover", false);
	// 	})
	// 	.call(drag);

	//     node.append("title")
	// 	.text(function(d) { return d.title; });

	//     layout.on("tick", function() {
	//     	link.attr("x1", function(d) { return d.source.x; })
	//     	    .attr("y1", function(d) { return d.source.y; })
	//     	    .attr("x2", function(d) { return d.target.x; })
	//     	    .attr("y2", function(d) { return d.target.y; });

	//     	node.attr("cx", function(d) { return d.x; })
	//     	    .attr("cy", function(d) { return d.y; });
	//     });
	// }
	this.init_d3 = function(){
	    // This is basically a version of http://bl.ocks.org/benzguo/4370043



            var getData = function(){
		var data_set = [];
		$.each(instance.element_registry, function(i,v){
                    data_set.push(v);
		});
		return data_set;
            };

            var getLinks = function() {
		var data_set = getData();
		return data_set.reduce( function( initial, element) {
                    return initial.concat( 
			element.relations.map( function( relation) {
                            var src, tgt;
                            $.each(data_set, function(i,v){
				if(v.object_id == relation.target)
                                    tgt=i;
				if(v.object_id == element.object_id)
                                    src = i;
                            });
                            return { source : src, target : tgt};
			})
                    );
		}, []);
            };




	    var width = $('#relation-pane').width(),
	    height = $('#relation-pane').height(),
	    fill = d3.scale.category20();


	    var selected_node = null,
	    selected_link = null,
	    mousedown_link = null,
	    mousedown_node = null,
	    mouseup_node = null;

	    var outer = d3.select("#relation-pane")
		.append("svg:svg")
		.attr("width", width)
		.attr("height", height)
		.attr("pointer-events", "all");


	    var vis = outer
		.append('svg:g')
		.call(d3.behavior.zoom().on("zoom", rescale))
		.on("dblclick.zoom", null)
		.append('svg:g')
		.on("mousemove", mousemove)
		.on("mousedown", mousedown)
		.on("mouseup", mouseup);

	    vis.append('svg:rect')
		.attr('width', width)
		.attr('height', height)
		.attr('fill', 'white');

	    // init force layout
	    var force = d3.layout.force()
		.size([width, height])
		.nodes(getData()) // initialize with a single node
		.links(getLinks())
		.linkDistance(200)
		.charge(-2000)

		.on("tick", tick);

	    // line displayed when dragging new nodes
	    var drag_line = vis.append("line")
		.attr("class", "drag_line")
		.attr("x1", 0)
		.attr("y1", 0)
		.attr("x2", 0)
		.attr("y2", 0);

	    // get layout properties
	    var nodes = force.nodes();
	    var links = force.links(),

	    node = vis.selectAll(".node"),
	    link = vis.selectAll(".link");



	    // add keyboard callback
	    d3.select(window)
		.on("keydown", keydown);

	    



	    function mousedown() {
		if (!mousedown_node && !mousedown_link) {
		    // allow panning if nothing is selected
		    vis.call(d3.behavior.zoom().on("zoom", rescale));
		    return;
		}

	    }

	    function mousemove() {
		if (!mousedown_node) return;

		coordinates = d3.mouse(this);
		var x = coordinates[0];
		var y = coordinates[1];
		// update drag line
		drag_line
		    .attr("x1", mousedown_node.x)
		    .attr("y1", mousedown_node.y)
		    .attr("x2", x)
		    .attr("y2", y);

	    }

	    function mouseup() {
		if (mousedown_node) {
		    // hide drag line
		    drag_line
			.attr("class", "drag_line_hidden")

		    if (!mouseup_node) {
			// // add node
			// var point = d3.mouse(this),
			// node = {x: point[0], y: point[1]},
			// n = nodes.push(node);

			// // select new node
			// selected_node = node;
			// selected_link = null;
			
			// // add link to mousedown node
			// links.push({source: mousedown_node, target: node});
		    }

		    instance._d3_redraw();
		}
		// clear mouse event vars
		resetMouseVars();
	    }

	    function resetMouseVars() {
		mousedown_node = null;
		mouseup_node = null;
		mousedown_link = null;
	    }

	    function tick() {
		link.attr("x1", function(d) { return d.source.x; })
		    .attr("y1", function(d) { return d.source.y; })
		    .attr("x2", function(d) { return d.target.x; })
		    .attr("y2", function(d) { return d.target.y; });

		 // node.attr("cx", function(d) { return d.x; })
		 //     .attr("cy", function(d) { return d.y; });
node.attr("transform", function(d) {
    return "translate(" + d.x + "," + d.y + ")"; 
});

	    }

	    // rescale g
	    function rescale() {
		trans=d3.event.translate;
		scale=d3.event.scale;

		vis.attr("transform",
			 "translate(" + trans + ")"
			 + " scale(" + scale + ")");
	    }

	    // redraw force layout
	    instance._d3_redraw = function(load=false){
		if(load){
		    force.nodes(getData());
		    force.links(getLinks());
		}
		nodes = force.nodes();
		links = force.links();

		link = link.data(links);

		link.enter().insert("line", ".node")
		    .attr("class", "link")
		    .on("mousedown", 
			function(d) { 
			    mousedown_link = d; 
			    if (mousedown_link == selected_link) selected_link = null;
			    else selected_link = mousedown_link; 
			    selected_node = null; 
			    instance._d3_redraw(); 
			})

		link.exit().remove();

		link
		    .classed("link_selected", function(d) { return d === selected_link; });

		node = node.data(nodes);

		node.enter()
//		    .insert("circle").attr("class", "node").attr("r", 5)
		    .insert("g").attr("class", "node").append('circle').attr('r', 30)
		    .on("mousedown", 
			function(d) { 

			    // disable zoom
			    vis.call(d3.behavior.zoom().on("zoom", null));

			    mousedown_node = d;
			    if (mousedown_node == selected_node) selected_node = null;
			    else selected_node = mousedown_node; 
			    selected_link = null; 

			    // reposition drag line
			    drag_line
				.attr("class", "link")
				.attr("x1", mousedown_node.x)
				.attr("y1", mousedown_node.y)
				.attr("x2", mousedown_node.x)
				.attr("y2", mousedown_node.y);

			    instance._d3_redraw(); 
			})
		    .on("mousedrag",
			function(d) {
			    // instance._d3_redraw();
			})
		    .on("mouseup", 
			function(d) { 
			    if (mousedown_node) {
				mouseup_node = d; 
				if (mouseup_node == mousedown_node) { resetMouseVars(); return; }

				// add link
				var link = {source: mousedown_node, target: mouseup_node};

				//check if relation already exists
				var rel = instance.element_registry[mousedown_node.object_id].relations;
				rel_exists=false;
				$.each(rel, function(i,v){
				    if(v.target==mouseup_node.object_id){
					rel_exists = true;
					return false;
				    }
				});

				if(!rel_exists){

				    instance.element_registry[mousedown_node.object_id].relations.push({
					label: 'todo',
					target: mouseup_node.object_id
				    });
				}

				// select new link
				selected_link = link;
				selected_node = null;

				// enable zoom
				vis.call(d3.behavior.zoom().on("zoom", rescale));

				resetMouseVars();
				drag_line.attr("class", "drag_line_hidden");
				instance._d3_redraw(true);
				return;
			    } 
			})
		    .transition()
		    .duration(750)
		    .ease("elastic");
		    
		//insert text label
		node.select('text').remove();
		node.insert('text').attr("text-anchor", "middle").text(function(d) { return d.title; })

		node.exit().transition()
		    .attr("r", 0)
		    .remove();

		node
		    .classed("node_selected", function(d) { return d === selected_node; });


		

		if (d3.event) {
		    // prevent browser's default behavior
		    d3.event.stopPropagation();
		    d3.event.preventDefault();
		}

		force.start();

	    }

	    function spliceLinksForNode(node) {
		toSplice = links.filter(
		    function(l) { 
			return (l.source === node) || (l.target === node); });
		toSplice.map(
		    function(l) {
			links.splice(links.indexOf(l), 1); });
	    }

	    function keydown() {
		if (!selected_node && !selected_link) return;
		switch (d3.event.keyCode) {
		case 8: // backspace
		case 46: { // delete
		    if (selected_node) {
			nodes.splice(nodes.indexOf(selected_node), 1);
			spliceLinksForNode(selected_node);
		    }
		    else if (selected_link) {
			links.splice(links.indexOf(selected_link), 1);
		    }
		    selected_link = null;
		    selected_node = null;
		    instance._d3_redraw();
		    break;
		}
		}
	    }


	    instance._d3_redraw();
	};
	init_d3();




	return instance;
    };
    var b = builder();

    $('#dda-container-tabs').tabs({
	active: 3,
	activate:function(event,ui){
	    if(ui.newTab.index()==0){
		b.init_observable_pool();
	    }
	    if(ui.newTab.index()==3){
		b._d3_redraw(true);
	    }
        }
    });

    $('button').button();



});

