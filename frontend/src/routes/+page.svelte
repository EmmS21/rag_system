<script lang="ts">
    import { onMount, afterUpdate } from 'svelte';

    interface Message {
        id: number;
        content: string;
        sentByUser?: boolean;
    }

    let messages: Message[] = [
      { id: 1, content: "What would you like to learn about buying property in Colombia as a foreign national?" },
    ];

    let inputText = '';
    let waitingForResponse = false; 
    let chatContainer: { scrollTop: any; scrollHeight: any; };

    function handleClearChat() {
        messages = [messages[0]]; 
    }


    function handleKeyPress(event: { key: string; }) {
        if (event.key === 'Enter' || event.key === ' ') {
        sendMessage();
       }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    onMount(scrollToBottom);
    afterUpdate(scrollToBottom);



    let ongoingMessageContent = ""; 
    let activeMessageId = messages.length + 1; 
    
    async function sendMessage() {
        if (inputText.trim() === '') return;
        const newMessage = { id: activeMessageId, content: inputText, sentByUser: true };
        messages = [...messages, newMessage];
        inputText = '';
        activeMessageId++;

        const userQueries = messages.filter(msg => msg.id % 2 !== 0).map(msg => msg.content);
        userQueries.push(inputText);  

        waitingForResponse = true;
        messages = [...messages, { id: activeMessageId, content: "" }];

        const response = await fetch('http://localhost:8000/query/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                query: inputText,
                context: userQueries.length > 0 ? userQueries.join("\n") : undefined  
            })
        });

        if (response.ok) {
            const data = await response.json();
            const queryId = data.query_id;

            const eventSource = new EventSource(`http://localhost:8000/stream/${queryId}/`);
            eventSource.onmessage = function(event) {
                waitingForResponse = false;
                ongoingMessageContent += event.data + "\n"; 
                messages = messages.map(msg => msg.id === activeMessageId ? {...msg, content: ongoingMessageContent} : msg);
            };
            eventSource.addEventListener('end-of-stream', () => {
                console.log('Stream ended normally');
                eventSource.close();
            });
            eventSource.onerror = function(error) {
                if (eventSource.readyState === EventSource.CLOSED) {
                    console.log('EventSource closed by the server');
                } else {
                    console.error('EventSource failed:', error);
                }
                eventSource.close();
            };
        } else {
            waitingForResponse = false;
            console.error('Failed to send message:', await response.text());
        }
    }

    let profile = {
        name: "PropAbroadBot",
        details: "A Bot to help you navigate legal issues of investing in real estate in Colombia as a foreign national",
    };

  </script>
  
  <style>
    :global(body) {
      margin: 0;
      font-family: sans-serif;
    }
    
    header {
      background-color: #333;
      color: white;
      padding: 1em;
    }
  
    main {
      display: flex;
    }
  
    .chat {
        position: relative;
        width: 70%;
        background-color: #777; 
        padding: 1em 1em 60px 1em; 
        padding: 1em;
        margin-left: 20px; 
        border-radius: 10px;
        margin-top: 20px; 
        position: relative;
        overflow-y: scroll; 
        height: 70vh;    
    }

    .message-input-container {
        display: flex;
        align-items: center;
        bottom: 0;
        left: 0;
        width: calc(100% - 40px); 
        margin-left: 20px;
    }

    .message-input {
        flex: 1; 
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    .send-icon {
        width: 30px;
        height: 30px;
        cursor: pointer;
        transition: color 0.3s;
        margin-left: 10px; 
    }

    .send-icon:hover {
        animation: color-flash 1s infinite;
    }

  
    .profile {
      width: 30%;
      padding: 1em;
      background-color: #ffffff;
      border-left: 1px solid #dddddd;
      margin-top: 20px; 
    }
  
    .message {
      background-color: #fff;
      padding: 1em;
      margin-bottom: 1em;
      border-radius: 4px;
      display: flex; 
    }
  
    .profile-image {
      width: 100%;
      border-radius: 10px;
      margin-bottom: 1em;
    }

    .profile-tabs {
        display: flex;
        justify-content: space-around;
        margin-bottom: 20px;
    }

    .profile-tab {
        padding: 10px 20px;
        cursor: pointer;
        border-radius: 5px;
        background-color: #777;
    }
  
    .profile-info {
      margin-bottom: 1em;
    }
      
    .profile-info p {
      margin: 0; 
      color: #666; 
    }
  
    .logo {
      font-size: 34px;
      font-weight: bold;
      margin-right: 20px;
      animation: none; 
    }
    
    @keyframes color-change {
      0%, 100% {
        color: red;
      }
      33% {
        color: white;
      }
      67% {
        color: blue;
      }
    }
  
    .person-icon {
      width: 20px;
      height: 20px;
      margin-right: 10px;
    }
  
    .message-input {
      width: calc(100% - 40px); 
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }

    @keyframes color-flash {
        0%, 100% {
            color: inherit; 
        }
        50% {
            color: #ADD8E6; 
        }
    }

    footer {
        background-color: #333;
        color: white;
        padding: 1em;
        position: fixed;
        bottom: 0;
        width: 100%;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }

    .footer-section {
        display: flex;
        align-items: center;
    }

    .footer-icon {
        margin-right: 10px;
        color: white;
        text-decoration: none;
        transition: color 0.3s;
    }

    .footer-icon:hover {
        color: #ADD8E6;
    }

    .typing-animation::after {
    content: '';
        display: inline-block;
        width: 100%;
        height: 100%;
        background-color: transparent;
        animation: typing 2s steps(40) infinite;
    }

    .grey-background {
        background-color: #c2c0c0; 
    }

    .send-icon.disabled {
        pointer-events: none;
        opacity: 0.5;
    }

    .profile-tab.disabled {
        cursor: default;
    }
  </style>
  
  <svelte:head>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
  </svelte:head>
  
  <header>
    <span class="logo">PropAbroad</span>
  </header>
  
  <main>
    <div class="chat" bind:this={chatContainer}>
        {#each messages as message}
            <div class="message {message.sentByUser ? 'grey-background' : ''}">
                {#if message.sentByUser}
                    <svg class="person-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="7" r="4" />
                        <path d="M2 20a15.6 15.6 0 0 1 7-6.5 4 4 0 0 1 5.33 0A15.6 15.6 0 0 1 22 20z" />
                    </svg>
                {/if}
                <div class="typing-animation">{message.content}</div>
                {#if waitingForResponse && message.id === messages[messages.length - 1].id}
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                        <circle cx="4" cy="12" r="2" fill="currentColor">
                            <animate attributeName="r" begin=".67" calcMode="spline" dur="1.5s" keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8" repeatCount="indefinite" values="0;2;0;0"/>
                        </circle>
                        <circle cx="12" cy="12" r="2" fill="currentColor">
                            <animate attributeName="r" begin=".33" calcMode="spline" dur="1.5s" keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8" repeatCount="indefinite" values="0;2;0;0"/>
                        </circle>
                        <circle cx="20" cy="12" r="2" fill="currentColor">
                            <animate attributeName="r" begin="0" calcMode="spline" dur="1.5s" keySplines="0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8;0.2 0.2 0.4 0.8" repeatCount="indefinite" values="0;2;0;0"/>
                        </circle>
                    </svg>
                {/if}
            </div>
        {/each}
        <div class="message-input-container">
          <input type="text" bind:value="{inputText}" placeholder="Type your message..." class="message-input">          

          <svg class="send-icon {waitingForResponse ? 'disabled' : ''}" role="button" tabindex="0" on:click="{sendMessage}" on:keydown="{handleKeyPress}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </div>
    </div>
    
    <aside class="profile">
      <div class="profile-tabs">
        <span class="profile-tab">{profile.name}</span>
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <span class="profile-tab {waitingForResponse ? 'disabled' : ''}" role="button" tabindex="0" on:click={waitingForResponse ? null : handleClearChat}>Clear Chat</span>
    </div>
    

      <img class="profile-image" src="https://www.iconbunny.com/icons/media/catalog/product/4/2/4265.11-robot-ii-icon-iconbunny.jpg" alt="{profile.name}">
      <div class="profile-info">
        <p>{profile.details}</p>
      </div>

    </aside>
    <footer>
        <div class="footer-section">
            <p style="color: #777;">@2024 PropAbroad built by Emmanuel Sibanda</p>
        </div>
        <div class="footer-section" style="margin-left: 20px;">
            <a href="https://twitter.com/Emmoemm" class="footer-icon" target="_blank">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="https://www.linkedin.com/in/emmanuel-s-42b49176/" class="footer-icon" target="_blank">
              <i class="fab fa-linkedin-in"></i>
            </a>
            <a href="https://emmanuelsibanda.vercel.app/" class="footer-icon" target="_blank">
              <i class="fas fa-globe"></i>
            </a>
          </div>        
      </footer>
  </main>
  