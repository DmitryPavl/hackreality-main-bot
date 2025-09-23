import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import ChatMessage from '../components/ChatMessage';
import MessageInput from '../components/MessageInput';
import TelegramService, { TelegramMessage, TelegramUpdate } from '../services/TelegramService';

interface ChatScreenProps {
  botInfo: any;
  onBackToSetup: () => void;
}

const ChatScreen: React.FC<ChatScreenProps> = ({ botInfo, onBackToSetup }) => {
  const [messages, setMessages] = useState<TelegramMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdateId, setLastUpdateId] = useState<number>(0);
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Add a welcome message
    const welcomeMessage: TelegramMessage = {
      message_id: 0,
      from: {
        id: 0,
        is_bot: true,
        first_name: botInfo?.first_name || 'Bot',
      },
      chat: {
        id: 0,
        first_name: 'User',
        type: 'private',
      },
      date: Math.floor(Date.now() / 1000),
      text: `Hello! I'm ${botInfo?.first_name || 'your bot'}. How can I help you today?`,
    };
    setMessages([welcomeMessage]);
  }, [botInfo]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message to the chat
    const userMessage: TelegramMessage = {
      message_id: Date.now(),
      from: {
        id: 1,
        is_bot: false,
        first_name: 'You',
      },
      chat: {
        id: 1,
        first_name: 'You',
        type: 'private',
      },
      date: Math.floor(Date.now() / 1000),
      text: text,
    };

    setMessages(prev => [...prev, userMessage]);

    // Generate bot response
    const botResponse = TelegramService.generateBotResponse(text);
    
    // Add bot response to the chat
    const botMessage: TelegramMessage = {
      message_id: Date.now() + 1,
      from: {
        id: 0,
        is_bot: true,
        first_name: botInfo?.first_name || 'Bot',
      },
      chat: {
        id: 1,
        first_name: 'You',
        type: 'private',
      },
      date: Math.floor(Date.now() / 1000),
      text: botResponse,
    };

    // Simulate typing delay
    setTimeout(() => {
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  const handleGetUpdates = async () => {
    setIsLoading(true);
    try {
      const response = await TelegramService.getUpdates(lastUpdateId);
      if (response.success && response.data?.ok) {
        const updates: TelegramUpdate[] = response.data.result;
        
        if (updates.length > 0) {
          const newMessages: TelegramMessage[] = [];
          let newLastUpdateId = lastUpdateId;

          for (const update of updates) {
            if (update.message) {
              newMessages.push(update.message);
              newLastUpdateId = Math.max(newLastUpdateId, update.update_id);
            }
          }

          if (newMessages.length > 0) {
            setMessages(prev => [...prev, ...newMessages]);
            setLastUpdateId(newLastUpdateId + 1);
          }
        }
      } else {
        Alert.alert('Error', response.error || 'Failed to get updates');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch messages');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettings = () => {
    Alert.alert(
      'Settings',
      'What would you like to do?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Get Updates', onPress: handleGetUpdates },
        { text: 'Reset Bot', onPress: onBackToSetup },
      ]
    );
  };

  const renderMessage = ({ item }: { item: TelegramMessage }) => (
    <ChatMessage
      message={item}
      isFromBot={item.from.is_bot}
    />
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBackToSetup} style={styles.backButton}>
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.botName}>{botInfo?.first_name || 'Bot'}</Text>
          <Text style={styles.botStatus}>
            {botInfo ? 'Connected' : 'Demo Mode'}
          </Text>
        </View>
        <TouchableOpacity onPress={handleSettings} style={styles.settingsButton}>
          <Text style={styles.settingsButtonText}>⚙️</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item, index) => `${item.message_id}-${index}`}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color="#2196F3" />
          <Text style={styles.loadingText}>Getting updates...</Text>
        </View>
      )}

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isLoading}
        placeholder="Type a message..."
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 16,
    color: '#2196F3',
    fontWeight: '500',
  },
  headerInfo: {
    flex: 1,
    alignItems: 'center',
  },
  botName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  botStatus: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  settingsButton: {
    padding: 8,
  },
  settingsButtonText: {
    fontSize: 20,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: 8,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
});

export default ChatScreen;

