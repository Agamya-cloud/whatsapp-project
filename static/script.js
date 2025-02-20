// function login() {
//     let username = document.getElementById("username").value.trim();
//     let profilePic = document.getElementById("profilePic").files[0];

//     if (username !== "") {
//         document.getElementById("displayUsername").textContent = username;
        
//         if (profilePic) {
//             let reader = new FileReader();
//             reader.onload = function(e) {
//                 document.getElementById("userProfilePic").src = e.target.result;
//             }
//             reader.readAsDataURL(profilePic);
//         }

//         // Hide login page and show chat page
//         document.getElementById("loginPage").classList.add("hidden");
//         document.getElementById("chatPage").classList.remove("hidden");
//     } else {
//         alert("Please enter your name to continue.");
//     }
// }

// function sendMessage() {
//     let messageInput = document.getElementById("messageInput");
//     let messageText = messageInput.value.trim();
//     if (messageText !== "") {
//         let chatMessages = document.getElementById("chatMessages");
//         let messageDiv = document.createElement("div");
//         messageDiv.classList.add("message", "sent");
//         messageDiv.textContent = messageText;
//         chatMessages.appendChild(messageDiv);
//         messageInput.value = "";
//         chatMessages.scrollTop = chatMessages.scrollHeight;
//     }
// }

// function selectUser(userName) {
//     document.getElementById("chatHeader").textContent = "Chatting with " + userName;
//     document.getElementById("chatMessages").innerHTML = "";
// }
// function login() {
//     let username = document.getElementById("username").value.trim();
//     let profilePic = document.getElementById("profilePic").files[0];

//     if (username === "") {
//         alert("Please enter your name.");
//         return;
//     }

//     document.getElementById("displayUsername").textContent = username;

//     if (profilePic) {
//         let reader = new FileReader();
//         reader.onload = function(e) {
//             document.getElementById("userProfilePic").src = e.target.result;
//         }
//         reader.readAsDataURL(profilePic);
//     } else {
//         document.getElementById("userProfilePic").src = "default-profile.png";
//     }

//     document.getElementById("loginPage").classList.add("hidden");
//     document.getElementById("chatPage").classList.remove("hidden");
// }

// function sendMessage() {
//     let messageInput = document.getElementById("messageInput");
//     let messageText = messageInput.value.trim();

//     if (messageText === "") return;

//     let chatMessages = document.getElementById("chatMessages");
//     let messageDiv = document.createElement("div");
//     messageDiv.classList.add("message", "sent");

//     let timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

//     messageDiv.innerHTML = `${messageText} <span class="timestamp">${timestamp}</span>`;
//     chatMessages.appendChild(messageDiv);

//     messageInput.value = "";
//     chatMessages.scrollTop = chatMessages.scrollHeight;

//     hideTypingIndicator();
// }

// function selectUser(userName) {
//     document.getElementById("chatHeader").textContent = "Chatting with " + userName;
//     document.getElementById("chatMessages").innerHTML = "";
// }

// // function showTypingIndicator() {
// //     document.getElementById("typingIndicator").classList.remove("hidden");
// //     clearTimeout(typingTimeout);
// //     typingTimeout = setTimeout(hideTypingIndicator, 1000);
// // }

// // function hideTypingIndicator() {
// //     document.getElementById("typingIndicator").classList.add("hidden");
// // }

// // function toggleEmojiPicker() {
// //     let emojiPicker = document.getElementById("emojiPicker");
// //     emojiPicker.classList.toggle("hidden");

// //     if (!emojiPicker.classList.contains("hidden")) {
// //         loadEmojis();
// //     }
// // }

// // function loadEmojis() {
// //     let emojiPicker = document.getElementById("emojiPicker");
// //     emojiPicker.innerHTML = "";
// //     let emojis = ["😀", "😂", "😍", "😢", "😎", "😡", "👍", "❤️", "🔥", "🤔"];
    
// //     emojis.forEach(emoji => {
// //         let span = document.createElement("span");
// //         span.textContent = emoji;
// //         span.onclick = function() {
// //             document.getElementById("messageInput").value += emoji;
// //             emojiPicker.classList.add("hidden");
// //         };
// //         emojiPicker.appendChild(span);
// //     });
// // }
// // document.getElementById("loginForm").addEventListener("submit", function (event) {
// //     event.preventDefault(); // Prevent default form submission

// //     let phone = document.getElementById("phone").value;

// //     fetch("/login", {
// //         method: "POST",
// //         headers: { "Content-Type": "application/json" },
// //         body: JSON.stringify({ phone: phone })
// //     })
// //     .then(response => response.json())
// //     .then(data => {
// //         if (data.redirect) {
// //             window.location.href = data.redirect; // Redirect to chat page
// //         } else {
// //             alert(data.error);
// //         }
// //     })
// //     .catch(error => console.error("Error logging in:", error));
// // });
// // document.addEventListener("DOMContentLoaded", function() {
// //     const loginForm = document.querySelector("form");

// //     loginForm.addEventListener("submit", function(event) {
// //         event.preventDefault(); // Prevent default form submission

// //         const formData = new FormData(loginForm);

// //         fetch("/phone-login", {
// //             method: "POST",
// //             body: formData
// //         })
// //         .then(response => response.json())
// //         .then(data => {
// //             if (data.success) {
// //                 window.location.href = `/chat/${data.user_id}`;  // Redirect to chat page
// //             } else {
// //                 alert("Invalid login details!");
// //             }
// //         })
// //         .catch(error => console.error("Error:", error));
// //     });
// // });
// Toggle visibility of elements based on ID
function showElement(id) {
    document.getElementById(id).classList.remove('hidden');
}

// Hide elements based on ID
function hideElement(id) {
    document.getElementById(id).classList.add('hidden');
}

// Handle login (store username and profile pic, then go to chat page)
function login() {
    const username = document.getElementById("username").value;
    const profilePic = document.getElementById("profilePic").files[0];
    
    if (username && profilePic) {
        // Store user data in session or localStorage
        localStorage.setItem("username", username);
        localStorage.setItem("profilePic", URL.createObjectURL(profilePic));

        // Preview profile picture
        const previewImg = document.getElementById("previewImg");
        previewImg.src = URL.createObjectURL(profilePic);
        previewImg.classList.remove('hidden');

        // Display chat page
        document.getElementById("displayUsername").textContent = username;
        document.getElementById("userProfilePic").src = previewImg.src;

        // Hide login page and show chat page
        hideElement("loginPage");
        showElement("chatPage");
    } else {
        alert("Please provide a username and profile picture!");
    }
}

// Select a user to chat with
function selectUser(user) {
    document.getElementById("chatHeader").textContent = `Chatting with ${user}`;
    document.getElementById("chatMessages").innerHTML = ""; // Clear previous messages
}

// Show typing indicator
function showTypingIndicator() {
    const input = document.getElementById("messageInput").value;
    const typingIndicator = document.getElementById("typingIndicator");
    if (input.length > 0) {
        showElement("typingIndicator");
    } else {
        hideElement("typingIndicator");
    }
}

// Send message function
function sendMessage() {
    const message = document.getElementById("messageInput").value;
    if (message) {
        const chatMessages = document.getElementById("chatMessages");
        const newMessage = document.createElement("p");
        newMessage.textContent = `You: ${message}`;
        chatMessages.appendChild(newMessage);
        document.getElementById("messageInput").value = ""; // Clear input field
        hideElement("typingIndicator"); // Hide typing indicator
    }
}

// Toggle emoji picker visibility
function toggleEmojiPicker() {
    const emojiPicker = document.getElementById("emojiPicker");
    emojiPicker.classList.toggle("hidden");
}

// For the emoji picker (could add actual emojis here)
document.getElementById("emojiPicker").innerHTML = "😊 😍 😁 😎"; // Example emojis
