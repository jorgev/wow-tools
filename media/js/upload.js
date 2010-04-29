// upload.js

$(document).ready(function() {
	$('form').submit(function(event) {
		$('#submit-message').remove();
		var fileName = $('#file').val();
		var name = $('#name').val();
		if (name.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('Event name is missing')
			.insertBefore('#submit');
			return false;
		}
		else if (fileName.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('File name is missing')
			.insertBefore('#submit');
			return false;
		}
		$('#submit').attr('disabled', true);
		$('<p></p>').attr({'id': 'submit-message', 'class': 'status'})
		.append('Uploading ' + fileName + '...')
		.insertAfter('#submit');
	});
});

