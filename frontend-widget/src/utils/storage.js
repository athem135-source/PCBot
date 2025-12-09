/**
 * Storage Utility Functions for PDBOT Widget
 * ==========================================
 * 
 * Handles localStorage operations for chat history,
 * session management, and widget state persistence.
 * 
 * @author Ministry of Planning, Development & Special Initiatives
 * @version 3.3.3
 */

import html2canvas from 'html2canvas';

// Storage keys
const STORAGE_KEYS = {
  CHAT_HISTORY: 'pdbot_chat_history',
  SESSION_ID: 'pdbot_session_id',
  WIDGET_STATE: 'pdbot_widget_state',
  USER_PREFERENCES: 'pdbot_user_prefs'
};

/**
 * Generate a unique session ID
 * @returns {string} UUID v4
 */
export function generateSessionId() {
  // Use crypto API if available, fallback to manual generation
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  
  // Fallback UUID generation
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Get or create session ID
 * @returns {string} Session ID
 */
export function getSessionId() {
  let sessionId = localStorage.getItem(STORAGE_KEYS.SESSION_ID);
  
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
  }
  
  return sessionId;
}

/**
 * Create a new session (generates new ID)
 * @returns {string} New session ID
 */
export function createNewSession() {
  const newSessionId = generateSessionId();
  localStorage.setItem(STORAGE_KEYS.SESSION_ID, newSessionId);
  return newSessionId;
}

/**
 * Save chat history to localStorage
 * @param {Array} messages - Array of chat messages
 */
export function saveChatHistory(messages) {
  try {
    const data = {
      messages: messages,
      lastUpdated: new Date().toISOString(),
      sessionId: getSessionId()
    };
    localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(data));
  } catch (error) {
    console.error('[PDBOT Storage] Failed to save chat history:', error);
  }
}

/**
 * Load chat history from localStorage
 * @returns {Array} Array of chat messages
 */
export function loadChatHistory() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    if (!data) return [];
    
    const parsed = JSON.parse(data);
    
    // Check if session matches
    const currentSession = getSessionId();
    if (parsed.sessionId !== currentSession) {
      // Different session, clear old history
      clearChatHistory();
      return [];
    }
    
    return parsed.messages || [];
  } catch (error) {
    console.error('[PDBOT Storage] Failed to load chat history:', error);
    return [];
  }
}

/**
 * Clear chat history
 */
export function clearChatHistory() {
  try {
    localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
    console.log('[PDBOT Storage] Chat history cleared');
  } catch (error) {
    console.error('[PDBOT Storage] Failed to clear chat history:', error);
  }
}

/**
 * Save widget state (position, minimized, etc.)
 * @param {Object} state - Widget state object
 */
export function saveWidgetState(state) {
  try {
    localStorage.setItem(STORAGE_KEYS.WIDGET_STATE, JSON.stringify(state));
  } catch (error) {
    console.error('[PDBOT Storage] Failed to save widget state:', error);
  }
}

/**
 * Load widget state
 * @returns {Object} Widget state or defaults
 */
export function loadWidgetState() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.WIDGET_STATE);
    if (!data) {
      return getDefaultWidgetState();
    }
    return { ...getDefaultWidgetState(), ...JSON.parse(data) };
  } catch (error) {
    console.error('[PDBOT Storage] Failed to load widget state:', error);
    return getDefaultWidgetState();
  }
}

/**
 * Get default widget state
 * @returns {Object} Default state
 */
function getDefaultWidgetState() {
  return {
    isOpen: false,
    isMinimized: false,
    position: { x: null, y: null }, // null = default bottom-right
    hasGreeted: false
  };
}

/**
 * Save user preferences
 * @param {Object} prefs - User preferences
 */
export function saveUserPreferences(prefs) {
  try {
    const existing = loadUserPreferences();
    const merged = { ...existing, ...prefs };
    localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(merged));
  } catch (error) {
    console.error('[PDBOT Storage] Failed to save preferences:', error);
  }
}

/**
 * Load user preferences
 * @returns {Object} User preferences
 */
export function loadUserPreferences() {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
    return data ? JSON.parse(data) : {};
  } catch (error) {
    console.error('[PDBOT Storage] Failed to load preferences:', error);
    return {};
  }
}

/**
 * Export chat history as text
 * @param {Array} messages - Chat messages
 * @returns {string} Formatted text
 */
export function exportChatAsText(messages) {
  const header = `PDBOT Chat Export
==================
Ministry of Planning, Development & Special Initiatives
Government of Pakistan

Exported: ${new Date().toLocaleString()}
Session ID: ${getSessionId()}

-------------------

`;

  const body = messages.map(msg => {
    const role = msg.role === 'user' ? '👤 You' : '🤖 PDBOT';
    const time = new Date(msg.timestamp).toLocaleTimeString();
    return `[${time}] ${role}:\n${msg.content}\n`;
  }).join('\n---\n\n');

  return header + body;
}

/**
 * Export chat history as Markdown
 * @param {Array} messages - Chat messages
 * @returns {string} Markdown content
 */
export function exportChatAsMarkdown(messages) {
  const header = `# 🤖 PDBOT Chat Export

**Ministry of Planning, Development & Special Initiatives**  
**Government of Pakistan**

---

| Field | Value |
|-------|-------|
| **Exported** | ${new Date().toLocaleString()} |
| **Session** | ${getSessionId()} |
| **Messages** | ${messages.length} |

---

## 💬 Conversation

`;

  const body = messages.map(msg => {
    const role = msg.role === 'user' ? '### 👤 You' : '### 🤖 PDBOT';
    const time = new Date(msg.timestamp).toLocaleTimeString();
    const content = msg.content.replace(/\n/g, '\n\n');
    return `${role}\n*${time}*\n\n${content}\n`;
  }).join('\n---\n\n');

  const footer = `\n---\n\n*Generated by PDBOT v3.3.2 | © Ministry of Planning, Development & Special Initiatives*\n`;

  return header + body + footer;
}

/**
 * Export chat history as styled HTML (looks like the chat widget)
 * @param {Array} messages - Chat messages
 * @returns {string} HTML content
 */
export function exportChatAsHTML(messages) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PDBOT Chat Export</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .chat-container {
      max-width: 500px;
      margin: 0 auto;
      background: white;
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      overflow: hidden;
    }
    .chat-header {
      background: linear-gradient(135deg, #006600 0%, #1fa67a 100%);
      color: white;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .chat-logo {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }
    .chat-title h1 {
      font-size: 16px;
      font-weight: 600;
      margin: 0;
    }
    .chat-title p {
      font-size: 11px;
      opacity: 0.9;
      margin: 2px 0 0;
    }
    .chat-messages {
      padding: 20px;
      background: #f8f9fa;
      min-height: 300px;
    }
    .message {
      margin-bottom: 16px;
      display: flex;
      flex-direction: column;
    }
    .message.user {
      align-items: flex-end;
    }
    .message.bot {
      align-items: flex-start;
    }
    .message-bubble {
      max-width: 85%;
      padding: 12px 16px;
      border-radius: 16px;
      line-height: 1.5;
      font-size: 14px;
    }
    .message.user .message-bubble {
      background: linear-gradient(135deg, #006600, #1fa67a);
      color: white;
      border-bottom-right-radius: 4px;
    }
    .message.bot .message-bubble {
      background: white;
      color: #333;
      border: 1px solid #e0e0e0;
      border-bottom-left-radius: 4px;
    }
    .message-time {
      font-size: 10px;
      color: #999;
      margin-top: 4px;
      padding: 0 8px;
    }
    .chat-footer {
      background: white;
      padding: 16px 20px;
      border-top: 1px solid #eee;
      text-align: center;
    }
    .chat-footer p {
      font-size: 11px;
      color: #666;
    }
    .chat-footer .version {
      color: #006600;
      font-weight: 600;
    }
    .export-meta {
      background: #f0f0f0;
      padding: 12px 20px;
      font-size: 12px;
      color: #666;
      text-align: center;
      border-top: 1px solid #ddd;
    }
    @media print {
      body { padding: 0; background: white; }
      .chat-container { box-shadow: none; max-width: 100%; }
    }
  </style>
</head>
<body>
  <div class="chat-container">
    <div class="chat-header">
      <div class="chat-logo">🤖</div>
      <div class="chat-title">
        <h1>PDBOT</h1>
        <p>Ministry of Planning, Development & Special Initiatives</p>
      </div>
    </div>
    <div class="chat-messages">
      ${messages.map(msg => `
        <div class="message ${msg.role === 'user' ? 'user' : 'bot'}">
          <div class="message-bubble">${escapeHtml(msg.content)}</div>
          <span class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</span>
        </div>
      `).join('')}
    </div>
    <div class="chat-footer">
      <p><span class="version">PDBOT v3.3.2</span> | Government of Pakistan</p>
    </div>
    <div class="export-meta">
      Exported: ${new Date().toLocaleString()} | Session: ${getSessionId()} | Messages: ${messages.length}
    </div>
  </div>
</body>
</html>`;
  return html;
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br>');
}

/**
 * Download content as file
 * @param {string} content - File content
 * @param {string} filename - File name
 * @param {string} mimeType - MIME type
 */
export function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Download chat as image (PNG)
 * Uses html2canvas to capture element as image
 * @param {HTMLElement} element - The element to capture
 * @param {string} filename - Output filename
 */
export async function downloadAsImage(element, filename) {
  console.log('[PDBOT] Starting image download...', element);
  
  if (!element) {
    console.error('[PDBOT] No element provided for image capture');
    alert('Could not capture chat. Please try again.');
    return false;
  }
  
  try {
    console.log('[PDBOT] Calling html2canvas...');
    const canvas = await html2canvas(element, {
      backgroundColor: '#f8f9fa',
      scale: 2,
      useCORS: true,
      logging: true, // Enable logging for debugging
      allowTaint: true,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight
    });
    
    console.log('[PDBOT] Canvas created:', canvas.width, 'x', canvas.height);
    
    // Convert to blob and download
    canvas.toBlob((blob) => {
      if (!blob) {
        console.error('[PDBOT] Failed to create blob');
        alert('Failed to create image. Please try again.');
        return;
      }
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = filename;
      link.href = url;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, 100);
      
      console.log('[PDBOT] Image download triggered:', filename);
    }, 'image/png', 1.0);
    
    return true;
  } catch (error) {
    console.error('[PDBOT] Image export failed:', error);
    alert('Image export failed: ' + error.message);
    return false;
  }
}

export default {
  getSessionId,
  createNewSession,
  saveChatHistory,
  loadChatHistory,
  clearChatHistory,
  saveWidgetState,
  loadWidgetState,
  saveUserPreferences,
  loadUserPreferences,
  exportChatAsText,
  exportChatAsMarkdown,
  exportChatAsHTML,
  downloadFile,
  downloadAsImage
};
