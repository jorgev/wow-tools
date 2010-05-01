// raids.js

$(document).ready(function() {
	// confirm user action
	$('.delete').click(function() {
		var name = $(this).parent().children('.name').text();
		if (!confirm('Are you sure you want to remove ' + name + ' from the mailing list?'))
			return false;
	});
});
