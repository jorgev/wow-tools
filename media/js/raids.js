// raids.js

var rowToDelete;

$(document).ready(function() {
	// confirm user action
	$('.delete').click(function() {
		var name = $(this).parent().children('.name').text();
		if (!confirm('Are you sure you want to delete ' + name + ' from your raid listings?'))
			return false;
		rowToDelete = $(this).parent().parent();
		$.ajax({
			type: 'DELETE',
			url: $(this).parent().children('a').attr('href'),
			success: function(data) {
				rowToDelete.remove();
			}
		});
	});
});
