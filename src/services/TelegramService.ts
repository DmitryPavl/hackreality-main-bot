import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface TelegramMessage {
  message_id: number;
  from: {
    id: number;
    is_bot: boolean;
    first_name: string;
    last_name?: string;
    username?: string;
  };
  chat: {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    type: string;
  };
  date: number;
  text?: string;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
}

export interface BotResponse {
  success: boolean;
  data?: any;
  error?: string;
}

class TelegramService {
  private botToken: string = '';
  private baseUrl: string = 'https://api.telegram.org/bot';
  private webhookUrl: string = '';

  constructor() {
    this.loadBotToken();
  }

  private async loadBotToken(): Promise<void> {
    try {
      const token = await AsyncStorage.getItem('telegram_bot_token');
      if (token) {
        this.botToken = token;
      }
    } catch (error) {
      console.error('Error loading bot token:', error);
    }
  }

  async setBotToken(token: string): Promise<void> {
    try {
      this.botToken = token;
      await AsyncStorage.setItem('telegram_bot_token', token);
    } catch (error) {
      console.error('Error saving bot token:', error);
    }
  }

  async getBotInfo(): Promise<BotResponse> {
    try {
      if (!this.botToken) {
        return { success: false, error: 'Bot token not set' };
      }

      const response = await axios.get(`${this.baseUrl}${this.botToken}/getMe`);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  async sendMessage(chatId: number, text: string): Promise<BotResponse> {
    try {
      if (!this.botToken) {
        return { success: false, error: 'Bot token not set' };
      }

      const response = await axios.post(`${this.baseUrl}${this.botToken}/sendMessage`, {
        chat_id: chatId,
        text: text,
        parse_mode: 'HTML'
      });

      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  async getUpdates(offset?: number): Promise<BotResponse> {
    try {
      if (!this.botToken) {
        return { success: false, error: 'Bot token not set' };
      }

      const params: any = {};
      if (offset) {
        params.offset = offset;
      }

      const response = await axios.get(`${this.baseUrl}${this.botToken}/getUpdates`, {
        params
      });

      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  async setWebhook(url: string): Promise<BotResponse> {
    try {
      if (!this.botToken) {
        return { success: false, error: 'Bot token not set' };
      }

      const response = await axios.post(`${this.baseUrl}${this.botToken}/setWebhook`, {
        url: url
      });

      this.webhookUrl = url;
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  async deleteWebhook(): Promise<BotResponse> {
    try {
      if (!this.botToken) {
        return { success: false, error: 'Bot token not set' };
      }

      const response = await axios.post(`${this.baseUrl}${this.botToken}/deleteWebhook`);
      this.webhookUrl = '';
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  // Simple bot logic - you can expand this
  generateBotResponse(message: string): string {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return 'Hello! 👋 How can I help you today?';
    }

    if (lowerMessage.includes('help')) {
      return 'I\'m a simple chatbot! Try asking me:\n• Say hello\n• Ask about the weather\n• Tell me a joke\n• Ask for help';
    }

    if (lowerMessage.includes('weather')) {
      return 'I don\'t have access to real-time weather data, but I hope it\'s a beautiful day! ☀️';
    }

    if (lowerMessage.includes('joke')) {
      const jokes = [
        'Why don\'t scientists trust atoms? Because they make up everything! 😄',
        'Why did the scarecrow win an award? He was outstanding in his field! 🌾',
        'Why don\'t eggs tell jokes? They\'d crack each other up! 🥚'
      ];
      return jokes[Math.floor(Math.random() * jokes.length)];
    }

    if (lowerMessage.includes('time')) {
      return `The current time is: ${new Date().toLocaleTimeString()}`;
    }

    return 'I\'m not sure how to respond to that. Try saying "help" to see what I can do! 🤖';
  }
}

export default new TelegramService();

