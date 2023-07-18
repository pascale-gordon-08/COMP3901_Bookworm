$(document).on('change', '.file-input', function() {
        

    var filesCount = $(this)[0].files.length;
    
    var textbox = $(this).prev();
  
    if (filesCount === 1) {
      var fileName = $(this).val().split('\\').pop();
      textbox.text(fileName);
    } else {
      textbox.text(filesCount + ' files selected');
    }
  });
$(document).ready(function() {
  $("#chat-form").submit(function(e) {
    e.preventDefault();  // Prevent form submission
    var message = $("#chat-form input").val();  // Get the entered message
    // Perform further actions like sending the message to the server and updating the chat container
    // ...
    $("#chat-container").append('<p>' + message + '</p>');  // Add the message to the chat container
    $("#chat-form input").val('');  // Clear the input field
  });
});

