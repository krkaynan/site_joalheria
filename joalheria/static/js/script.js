$(document).ready(function() {

    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');

        } else {
            item.removeClass('active');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
        } else {
            $(this).closest('.js-check').removeClass('active');
        }
    });

	if($('[data-toggle="tooltip"]').length>0) {  
		$('[data-toggle="tooltip"]').tooltip()
	} 

}); 

setTimeout(function(){
    $('#message').fadeOut('slow')
}, 4000);