$(function() {


    $('#template_selector').change(function(){
        $(this).closest('form').trigger('submit');
    });


    $.dingos_authoring = {
        init: function(schema, options){
            instance = this;
            this.schema = schema;
	    this.options = options;
            this.template_head = $('#dda-template-head');
            this.template_body = $('#dda-template-body');
            this.export_btn = $('#dda-export-btn');

            if($.isEmptyObject(schema))
                return;

            // Let it render
            this.render(function(elem){
                // We're done rendering. Enable export button
                instance.export_btn.css('background', '').removeAttr('disabled');
                instance.export_btn.click(function(){
                    instance.export(elem);
                    return false; // Prevent form submission
                });

            });

        },
        render: function(callback){
            this.template_head.text(this.schema.title);
            this.template_body.html('');
            var elem = this.template_body.alpaca({
		data: '',
                schema: this.schema,
                options: this.options,
                postRender: function(form) {
                    callback(form);
                },
                "ui": "jquery-ui"
            });

        },
        export: function(form){
            //TODO: Check data in form (validate?)
            //TODO: Prepare export; print?; submit?; ajax?; download?
            console.log(form.validate());
            json = form.getValue();
            alert(JSON.stringify(json));
        }
    }



    $('.dda-add-element').draggable({
        helper: "clone"
    });



});
