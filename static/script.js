document.addEventListener('DOMContentLoaded', () => {
    const chatScreen = document.getElementById('chatScreen');
    const chatInput = document.getElementById('chatInput');
    const micButton = document.getElementById('micButton');
    const emojiButton = document.getElementById('emojiButton');
    const sendButton = document.getElementById('sendButton');
    const emojiPicker = document.getElementById('emojiPicker');
    let isListening = false;
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    const username = "User";
    let commands = [];
    let imageData = null;

    // Fetch commands from the Flask backend
    fetch('/api/commands')
        .then(response => response.json())
        .then(data => commands = data)
        .catch(error => console.error('Error fetching commands:', error));

    // Function to send chat
   function sendChat() {
        const userText = chatInput.value.trim();
        if (userText || imageData) {
            if (userText) addChatBubble(userText, 'user');
            if (imageData) {
                addChatBubble('User sent an image:', 'user', imageData);
                imageData = null;
                clearImagePreview();
            }
            chatInput.value = '';
            getResponse(userText);
        }
    }

    function clearImagePreview() {
        const imagePreview = chatInput.parentNode.querySelector('.image-preview');
        if (imagePreview) {
            imagePreview.remove(); // Remove the image preview from the input field
        }
    }

    // Add event listener for "Send" button
    chatInput.addEventListener('keypress', e => e.key === 'Enter' && sendChat());
    sendButton.addEventListener('click', sendChat);

    // Function to toggle microphone
    function toggleMic() {
        isListening = !isListening;
        micButton.classList.toggle('active', isListening);
        if (isListening) {
            recognition.start();
        } else {
            recognition.stop();
        }
    }

    // Add event listener for "Mic" button
    micButton.addEventListener('click', toggleMic);

    // Function to add chat bubble
   function addChatBubble(text, sender, imageUrl = null) {
        const bubble = document.createElement('div');
        bubble.className = `chat-message ${sender}`;

        const card = document.createElement('div');
        card.className = 'card';

        if (imageUrl) {
            const img = document.createElement('img');
            img.src = imageUrl;
            img.alt = 'Sent Image';
            img.className = 'chat-image';
            card.appendChild(img);
        }

      if (text.includes('```')) {
    const codeBlock = document.createElement('pre');
    const code = document.createElement('code');
    code.innerText = text.replace(/```/g, '').trim();
    codeBlock.appendChild(code);
    card.appendChild(codeBlock);
} else {
    const p = document.createElement('p');
    p.innerText = text;
    card.appendChild(p);
}


        bubble.appendChild(card);
        chatScreen.appendChild(bubble);
        chatScreen.scrollTop = chatScreen.scrollHeight;
    }

    recognition.onresult = event => {
        const command = event.results[0][0].transcript;
        addChatBubble(command, 'user');
        getResponse(command);
    };

    // Voice recognition results
    recognition.onresult = function (event) {
        const command = event.results[0][0].transcript;
        addChatBubble(command, 'user');
        getResponse(command);
    };

    // Function to get a response from the commands array
    function stopCurrentSpeech() {
        window.speechSynthesis.cancel();
    }

    // Function to get a response
    function getResponse(userText) {
    const isAdultMode = localStorage.getItem("adultMode") === "enabled";

    // Create a placeholder typing bubble
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-message aurabot typing-bubble';
    typingBubble.innerHTML = `
        <div class="card">
            <p><em>AuraBot is typing...</em></p>
        </div>
    `;
    chatScreen.appendChild(typingBubble);
    chatScreen.scrollTop = chatScreen.scrollHeight;

    if (isAdultMode) {
        const match = commands.find(c => userText.toLowerCase().includes(c.command.toLowerCase()));

        if (match) {
            updateTypingBubble(match.response);
            stopCurrentSpeech();
            textToSpeech(match.response);
        } else {
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: userText })
            })
            .then(res => res.json())
            .then(data => {
                stopCurrentSpeech();
                updateTypingBubble(data.response, data.image_url);
                textToSpeech(data.response);
            })
            .catch(err => {
                console.error('Error fetching chat:', err);
                updateTypingBubble("Sorry, I couldn't understand that.");
                stopCurrentSpeech();
                textToSpeech("Sorry, I couldn't understand that.");
            });
        }
    } else {
        updateTypingBubble(userText);
        stopCurrentSpeech();
        textToSpeech(userText);
    }
}

function updateTypingBubble(finalText, imageUrl = null) {
    const typingBubble = document.querySelector('.typing-bubble');
    if (!typingBubble) return;

    const card = typingBubble.querySelector('.card');
    card.innerHTML = ''; // Clear "typing..."

    if (finalText.includes('```')) {
        const codeBlock = document.createElement('pre');
        codeBlock.innerHTML = `<code>${finalText.replace(/```/g, '').trim()}</code>`;
        card.appendChild(codeBlock);
    } else {
        const p = document.createElement('p');
        p.innerText = finalText;
        card.appendChild(p);
    }

    if (imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'AuraBot Image';
        img.className = 'chat-image';
        card.appendChild(img);
    }

    typingBubble.classList.remove('typing-bubble'); // Mark as completed
    chatScreen.scrollTop = chatScreen.scrollHeight;
}

    // Text-to-Speech function
    function textToSpeech(text) {
        const isTextToSpeechEnabled = localStorage.getItem("ttsEnabled") === "true";
        if (!isTextToSpeechEnabled) return; // Check TTS setting

        const utterance = new SpeechSynthesisUtterance(text);
        const selectedVoiceName = localStorage.getItem('selectedVoice');
        const voices = window.speechSynthesis.getVoices();
        const selectedVoice = voices.find(voice => voice.name === selectedVoiceName);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
        window.speechSynthesis.speak(utterance);
    }

    // Emoji Picker functionality
    const emojis = ['😊', '😂', '😍', '😎', '😢', '😭', '😜', '😏', '😡', '🤔'];

    // Toggle emoji picker
    emojiButton.addEventListener('click', () => {
        emojiPicker.style.display = emojiPicker.style.display === 'none' || emojiPicker.style.display === '' ? 'block' : 'none';
        populateEmojiPicker();
    });

    // Populate emoji picker with emojis
    function populateEmojiPicker() {
        emojiPicker.innerHTML = '';
        emojis.forEach(emoji => {
            const button = document.createElement('button');
            button.textContent = emoji;
            button.onclick = () => insertEmoji(emoji);
            emojiPicker.appendChild(button);
        });
    }

    // Insert selected emoji into chat input
    function insertEmoji(emoji) {
        chatInput.value += emoji;
        emojiPicker.style.display = 'none'; // Hide the emoji picker after selection
    }

    document.getElementById('cameraButton').addEventListener('click', () => {
        document.getElementById('imageInput').click();
    });

     document.getElementById('imageInput').addEventListener('change', event => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = e => {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.classList.add('image-preview');
                img.style.width = '30px';
                img.style.height = '30px';
                chatInput.parentNode.insertBefore(img, chatInput);
                imageData = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Image send logic when user clicks "Send" or presses "Enter"
    sendButton.addEventListener('click', sendChat);
    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendChat();
        }
    });
});



function showAbout() {
    document.getElementById("aboutPopup").style.display = "block";
}

function openComplaintBox() {
    document.getElementById("complaintBox").style.display = "block";
}

function showSettings() {
    document.getElementById("settingsPopup").style.display = "block";
}

function showHistory() {
    document.getElementById("historyPopup").style.display = "block";
}

function closePopup(popupId) {
    document.getElementById(popupId).style.display = "none";
}

function sendComplaint() {
    const complaintText = document.getElementById("complaintText").value;
    if (!complaintText.trim()) {
        alert("Please enter a complaint before sending.");
        return;
    }

    const email = "mailto:sivagomasani01@gmail.com?subject=User Complaint&body=" + encodeURIComponent(complaintText);            
    window.location.href = email;

    closePopup("complaintBox");
    alert("Complaint sent successfully!");
}

document.addEventListener("DOMContentLoaded", function () {
    const modeToggle = document.getElementById("modeToggle");
    const modeLabel = document.getElementById("modeLabel");
    const contentToggle = document.getElementById("contentToggle");
    const contentLabel = document.getElementById("contentLabel");

    function applyDarkMode(isDark) {
        if (isDark) {
            document.body.classList.add("dark-mode");
            document.body.style.backgroundColor = "#1e1e1e"; 
            document.body.style.color = "#ffffff"; 
            localStorage.setItem("darkMode", "enabled");
            modeLabel.textContent = "Dark Mode";
        } else {
            document.body.classList.remove("dark-mode");
            document.body.style.backgroundColor = "#ffffff"; 
            document.body.style.color = "#000000"; 
            localStorage.setItem("darkMode", "disabled");
            modeLabel.textContent = "Light Mode";
        }
    }

    function applyContentMode(isAdult) {
        if (isAdult) {
            localStorage.setItem("adultMode", "enabled");
            contentLabel.textContent = "Adult Mode";
            alert("Adult mode enabled! Some content may be unrestricted.");
        } else {
            localStorage.setItem("adultMode", "disabled");
            contentLabel.textContent = "Child Mode";
            alert("Child mode enabled! Safe browsing is active.");
        }
    }
    applyDarkMode(localStorage.getItem("darkMode") === "enabled");
    applyContentMode(localStorage.getItem("adultMode") === "enabled");

    modeToggle.addEventListener("change", function () {
        applyDarkMode(this.checked);
    });

    contentToggle.addEventListener("change", function () {
        applyContentMode(this.checked);
    });

    // Initialize Text-to-Speech toggle state
    document.getElementById('ttsToggle').checked = localStorage.getItem("ttsEnabled") === "true";
    document.getElementById('ttsToggle').addEventListener('change', function () {
        const isTextToSpeechEnabled = this.checked;
        localStorage.setItem("ttsEnabled", isTextToSpeechEnabled ? "true" : "false");
        if (isTextToSpeechEnabled) {
            console.log("Text-to-Speech enabled.");
        } else {
            console.log("Text-to-Speech disabled.");
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // Function to update the content based on the selected language
    function updateContent(lang) {
        const elements = document.querySelectorAll("[data-translate]");

        elements.forEach(element => {
            const key = element.getAttribute("data-translate");
            if (translations[lang][key]) {
                element.innerHTML = translations[lang][key];
            }
        });

        // Update the title dynamically
        document.querySelector('title').innerHTML = translations[lang].headerTitle;
    }

    // Function to change the language
    function changeLanguage(lang) {
        localStorage.setItem('language', lang); // Store the selected language in localStorage
        updateContent(lang); // Update the content
        closeLanguageMenu(); // Close the language selection menu
    }

    // Add event listeners for language change
    const languageLinks = document.querySelectorAll('#languageMenu a');
    languageLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            const lang = event.target.getAttribute('onclick').split("'")[1];
            changeLanguage(lang);
        });
    });

    // Function to toggle the language menu visibility
    function toggleLanguageMenu() {
        const languageMenu = document.getElementById('languageMenu');
        languageMenu.style.display = languageMenu.style.display === 'block' ? 'none' : 'block';
    }

    // Open the language menu when clicking the "Change Language" menu item
    const changeLanguageButton = document.querySelector('[data-translate="changeLanguage"]');
    changeLanguageButton.addEventListener('click', toggleLanguageMenu);

    // Close the language menu when a language is selected
    function closeLanguageMenu() {
        const languageMenu = document.getElementById('languageMenu');
        languageMenu.style.display = 'none';
    }

    // Initialize the language on page load
    const savedLang = localStorage.getItem('language') || 'en';
    updateContent(savedLang); // Update content based on saved language

    // Optionally, you can highlight the active language in the menu
    const activeLangLink = document.querySelector(`#languageMenu a[onclick*="${savedLang}"]`);
    if (activeLangLink) {
        activeLangLink.style.fontWeight = 'bold';
    }
});

function showVoicePopup() {
    var popup = document.getElementById("voicePopup");
    popup.style.display = "block";
    
    var msg = new SpeechSynthesisUtterance();
    msg.text = document.getElementById("popupMessage").innerText;
    window.speechSynthesis.speak(msg);
}

function hidePopup() {
    var popup = document.getElementById("voicePopup");
    popup.style.display = "none";
}

