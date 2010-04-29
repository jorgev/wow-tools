// register.js

$(document).ready(function() {
	$('form').submit(function(event) {
		$('#submit-message').remove();
		var username = $('#username').val();
		var email = $('#email').val();
		var password = $('#password').val();
		if (username.length == 0 || email.length == 0 || password.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('All fields are required')
			.insertBefore('#submit');
			return false;
		}
		var password2 = $('#password2').val();
		if (password != password2) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('Passwords do not match, please re-enter')
			.insertBefore('#submit');
			return false;
		}
	});
});
