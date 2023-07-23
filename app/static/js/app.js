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

// document.addEventListener('DOMContentLoaded', function () {
//   const chatForm = document.getElementById('chat-form');
//   const chatLog = document.getElementById('chat-log');
//   const userMessageInput = document.getElementById('user-input');

//   chatForm.addEventListener('submit', function (event) {
//     event.preventDefault();
//     const userMessage = userMessageInput.value.trim();
//     if (userMessage === '') return;

//     chatLog.innerHTML += '<div class="user-message">' + userMessage + '</div>';

//     userMessageInput.value = '';
//     userMessageInput.focus();

//     fetch('/get_response', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/x-www-form-urlencoded',
//       },
//       body: 'user_message=' + encodeURIComponent(userMessage),
//     })
//       .then((response) => response.json())
//       .then((data) => {
//         const modelResponse = data.response;
//         chatLog.innerHTML += '<div class="model-response">' + modelResponse + '</div>';
//       })
//       .catch((error) => {
//         console.error('Error:', error);
//       });
//   });
// });


