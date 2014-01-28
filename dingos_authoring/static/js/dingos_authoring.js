$(function() {

    $('#template_selector').change(function(){
        $(this).closest('form').trigger('submit');
    });


    $.dingos_authoring = {
        init: function(json){
            instance = this;
            this.json = json;
            this.template_head = $('#dda-template-head');
            this.template_body = $('#dda-template-body');
            this.export_btn = $('#dda-export-btn');

            // Check for json template is not empty
            if($.isEmptyObject(json))
                return;
            // TODO: more checks?

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
            this.template_head.text(this.json.title);
            this.template_body.html('');
            var elem; //the rendered alpaca element
            elem = this.template_body.alpaca({
                schema: this.json,
                options: {
                    "collapsible": false,
                    "fields":{
                        "indicator_title": {},
                        "indicator_alternative_id": {},
                        "indicator_description": {},
                        "indicator_confidence": {"emptySelectFirst": true},
                        "indicator_sighting": {"type": "select"},
                        "indicator_snort_rules": {"toolbarSticky": true, "collapsible": false},
                        "observed_dns_names": {"toolbarSticky": true, "collapsible": false},
                        "observed_ip_addresses": {"toolbarSticky": true, "collapsible": false},
                        "related_malware_samples_hash": {"toolbarSticky": true, "collapsible": false},
                        "custom_array": {}
                    }
                },
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