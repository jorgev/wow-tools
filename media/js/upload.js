// upload.js

$(document).ready(function() {
	$('form').submit(function(event) {
		$('#submit-message').remove();
		var fileName = $('#file').val();
		var name = $('#name').val();
		if (fileName.length == 0 || name.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('All fields are required')
			.insertBefore('#submit');
			return false;
		}
		$('#submit').attr('disabled', true);
		$('<p></p>').attr({'id': 'submit-message', 'class': 'status'})
		.append('Uploading ' + fileName + '...')
		.insertAfter('#submit');
	});
});