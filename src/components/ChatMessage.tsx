import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { TelegramMessage } from '../services/TelegramService';

interface ChatMessageProps {
  message: TelegramMessage;
  isFromBot: boolean;
  onPress?: () => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  message, 
  isFromBot, 
  onPress 
}) => {
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getSenderName = () => {
    if (isFromBot) {
      return 'Bot';
    }
    return message.from.first_name || message.from.username || 'User';
  };

  return (
    <TouchableOpacity 
      style={[
        styles.messageContainer,
        isFromBot ? styles.botMessage : styles.userMessage
      ]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[
        styles.messageBubble,
        isFromBot ? styles.botBubble : styles.userBubble
      ]}>
        <Text style={[
          styles.senderName,
          isFromBot ? styles.botSenderName : styles.userSenderName
        ]}>
          {getSenderName()}
        </Text>
        <Text style={[
          styles.messageText,
          isFromBot ? styles.botText : styles.userText
        ]}>
          {message.text || 'No text content'}
        </Text>
        <Text style={[
          styles.timestamp,
          isFromBot ? styles.botTimestamp : styles.userTimestamp
        ]}>
          {formatTime(message.date)}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  messageContainer: {
    marginVertical: 4,
    paddingHorizontal: 16,
  },
  botMessage: {
    alignItems: 'flex-start',
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  botBubble: {
    backgroundColor: '#E3F2FD',
    borderBottomLeftRadius: 4,
  },
  userBubble: {
    backgroundColor: '#2196F3',
    borderBottomRightRadius: 4,
  },
  senderName: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 4,
  },
  botSenderName: {
    color: '#1976D2',
  },
  userSenderName: {
    color: '#FFFFFF',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 20,
    marginBottom: 4,
  },
  botText: {
    color: '#333333',
  },
  userText: {
    color: '#FFFFFF',
  },
  timestamp: {
    fontSize: 10,
    opacity: 0.7,
  },
  botTimestamp: {
    color: '#666666',
  },
  userTimestamp: {
    color: '#FFFFFF',
  },
});

export default ChatMessage;

