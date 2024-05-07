function showCreateChatDialog() {
    const dialog = document.getElementById('createChatDialog');
    dialog.style.display = 'flex';
}

function hideCreateChatDialog() {
    const dialog = document.getElementById('createChatDialog');
    dialog.style.display = 'none';
}

function createNewChat() {
    const chatName = document.getElementById('chatnameInput').value;
    fetch('/api/chat/create', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        'chat_name': chatName
    })
        })
        .then(response => response.json())
        .then(data => {
    fetchChats();
    hideCreateChatDialog();
        })
        .catch(error => console.error('Error creating chat:', error));
}

function fetchChats() {
    fetch('/api/chats')
    .then(response => response.json())
    .then(data => {
    const chatList = document.querySelector('.chat-list');
    chatList.innerHTML = '';
    data.forEach(chat => {
        const chatId = chat[Object.keys(chat)[0]];
        const listItem = document.createElement('li');
        listItem.className = 'chat-item';
        const link = document.createElement('a');
        link.className = 'chat-link';
        link.href = `/chat/${chatId}`;
        link.textContent = chat[Object.keys(chat)[1]];
        listItem.appendChild(link);
        chatList.appendChild(listItem);
    });
    })
    .catch(error => console.error('Error fetching chats:', error));
}

function fetchUsers() {
    fetch('/api/users')
    .then(response => response.json())
    .then(data => {
    const userList = document.querySelector('.user-list');
    userList.innerHTML = '';
    data.forEach(user => {
        const listItem = document.createElement('li');
        listItem.className = 'user-item';
        listItem.textContent = user.username;
        userList.appendChild(listItem);
});
    })
    .catch(error => console.error('Error fetching users:', error));
}

function Logout() {
    window.location.href = '/logout';
}

window.onload = function() {
    fetchChats();
    fetchUsers();
};