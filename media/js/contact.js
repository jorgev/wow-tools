// contact.js

$(document).ready(function() {
	$('form').submit(function(event) {
		$('#submit-message').remove();
		var username = $('#username').val();
		var email = $('#email').val();
		var subject = $('#subject').val();
		var body = $('#body').val();
		if (username.length == 0 || email.length == 0 || subject.length == 0 || body.length == 0) {
			$('<p></p>').attr({'id': 'submit-message', 'class': 'warning'})
			.append('All fields are required')
			.insertBefore('#submit');
			return false;
		}
	});
});
