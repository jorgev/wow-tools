// upload.js

$(document).ready(function() {
	$('form').submit(function(event) {
		$('#submit-message').remove();
		var username = $('#username').val();
		var password = $('#password').val();
		if (username.length == 0 || password.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('All fields are required')
			.insertBefore('#submit');
			return false;
		}
	});
});
