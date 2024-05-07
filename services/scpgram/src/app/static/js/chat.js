let socket;
        
function connectWebSocket() {
    socket = io();

    socket.on('close', function() {
        setTimeout(connectWebSocket, 3000); 
    });

    socket.on('error', function(error) {
        console.error('WebSocket error:', error);
        setTimeout(connectWebSocket, 3000); 
    });

}
connectWebSocket();
function sendMessage() {
    const chat_id = document.getElementById('chat_id').value;
    const messageInput = document.getElementById('message');
    const message = messageInput.value;
    messageInput.value = '';
    socket.emit('send_message', { chat_id: chat_id, message: message });
}

function getMessages() {
    const chat_id = document.getElementById('chat_id').value;
    socket.emit('get_messages', { chat_id: chat_id });
}

socket.on('message_received', function(data) {
    const message = data.message;
    const sender = data.sender;
    const timestamp = data.timestamp;
    const messagesList = document.getElementById('messagesList');
    const formattedTime = new Date(timestamp).toLocaleString();
    const sanitizedSender = escapeHtml(sender);
    messagesList.innerHTML += `<li><strong>${sanitizedSender}</strong> (${formattedTime}): ${message}</li>`;
    messagesList.scrollTop = messagesList.scrollHeight;
});

function scrollToBottom() {
    const messagesList = document.getElementById('messagesList');
    messagesList.scrollTop = messagesList.scrollHeight;
}

function connectChat() {
    const chat_id = document.getElementById('chat_id').value;
    socket.emit('join_room', { chat_id: chat_id });
}

function addUserToChat() {
    const chat_id = document.getElementById('chat_id').value;
    const username = document.getElementById('usernameInput').value;
    fetch(`/api/chat/${chat_id}/add_user`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'username': username })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        hideAddUserModal();
        document.getElementById('usernameInput').value = '';
        loadChatMembers();
    })
    .catch(error => console.error('Error adding user to chat:', error));
}

function showAddUserModal() {
    const modal = document.getElementById('addUserModal');
    modal.style.display = 'block';
}

function hideAddUserModal() {
    const modal = document.getElementById('addUserModal');
    modal.style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('addUserModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

function removeUserFromChat() {
    const chat_id = document.getElementById('chat_id').value;
    const username = document.getElementById('usernameInput').value;
    fetch(`/api/chat/${chat_id}/remove_user`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'username': username })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        hideAddUserModal();
        document.getElementById('usernameInput').value = '';
        loadChatMembers();

    })
    .catch(error => console.error('Error removing user from chat:', error));
}

function redirectToProfile() {
    window.location.href = '/';
}

function loadChatMembers() {
    const chat_id = document.getElementById('chat_id').value;
    fetch(`/api/chat/${chat_id}/members`)
    .then(response => response.json())
    .then(data => {
        const membersList = document.getElementById('membersList');
        membersList.innerHTML = ''; 
        data.forEach(member => {
            const listItem = document.createElement('li');
            listItem.innerText = member.username;
            membersList.appendChild(listItem);
        });
    })
    .catch(error => console.error('Error loading chat members:', error));
}

window.onload = function() {
    scrollToBottom();
    getMessages();
    connectChat();
    loadChatMembers();            
};


function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });}