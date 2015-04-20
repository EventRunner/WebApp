function assignPageChange(object, page, parameters) {
	object.click(function(){
		$.get(page, function(template) {
			try {
			  var fn = jinja.compile(template).render(parameters);
			} catch(e) {
			  //todo: update error panel
			  return;
			}
			src = fn.toString();
			$('#content-div').html(src);

		})
	})
}

$(".chosen-select").chosen({search_contains: true,
                            disable_search_threshold: 10,
                            width: "200px"})

$('.select-all').click(function(){
    var target = $(this).attr("target");
    $(target).children("option").prop('selected', true);
    $(target).trigger('chosen:updated');
});

$('.deselect-all').click(function(){
    var target = $(this).attr("target");
    $(target).children("option").prop('selected', false);
    $(target).trigger('chosen:updated');
});

$('.datepicker').pickadate({clear: '',
                            formatSubmit: 'yyyy/mm/dd',
                            hiddenName: true,
                            onStart: function() {
                                var date = new Date()
                                this.set('select', [date.getFullYear(), date.getMonth(), date.getDate()]);
                            }})
                            
$('.timepicker').pickatime({clear: ''})

