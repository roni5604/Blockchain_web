$(document).ready(function() {
    $('#password').on('input', function() {
        var password = $(this).val();
        $.post('/validate_password', {password: password}, function(data) {
            $('#passwordStrength').text(data.strength);
            $('#passwordHelp').removeClass('text-muted text-danger text-warning text-success');
            if (data.strength === 'Weak') {
                $('#passwordHelp').addClass('text-danger');
            } else if (data.strength === 'Medium') {
                $('#passwordHelp').addClass('text-warning');
            } else if (data.strength === 'Strong') {
                $('#passwordHelp').addClass('text-success');
            }
        });
    });
});
