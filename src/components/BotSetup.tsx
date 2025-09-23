import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import TelegramService, { BotResponse } from '../services/TelegramService';

interface BotSetupProps {
  onBotConfigured: (botInfo: any) => void;
}

const BotSetup: React.FC<BotSetupProps> = ({ onBotConfigured }) => {
  const [botToken, setBotToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSetToken = async () => {
    if (!botToken.trim()) {
      Alert.alert('Error', 'Please enter a bot token');
      return;
    }

    setIsLoading(true);
    try {
      await TelegramService.setBotToken(botToken.trim());
      const response: BotResponse = await TelegramService.getBotInfo();
      
      if (response.success && response.data?.ok) {
        Alert.alert(
          'Success!', 
          `Bot "${response.data.result.first_name}" is ready!`,
          [{ text: 'OK', onPress: () => onBotConfigured(response.data.result) }]
        );
      } else {
        Alert.alert('Error', response.error || 'Failed to verify bot token');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to connect to Telegram API');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkip = () => {
    Alert.alert(
      'Skip Setup',
      'You can set up the bot token later in settings. The app will work in demo mode.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Skip', onPress: () => onBotConfigured(null) }
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>🤖 Telegram Bot Setup</Text>
        <Text style={styles.subtitle}>
          To use this app with Telegram, you need to create a bot and get its token.
        </Text>
        
        <View style={styles.instructions}>
          <Text style={styles.instructionTitle}>How to create a bot:</Text>
          <Text style={styles.instructionText}>
            1. Open Telegram and search for @BotFather
          </Text>
          <Text style={styles.instructionText}>
            2. Send /newbot command
          </Text>
          <Text style={styles.instructionText}>
            3. Follow the instructions to create your bot
          </Text>
          <Text style={styles.instructionText}>
            4. Copy the bot token and paste it below
          </Text>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Bot Token:</Text>
          <TextInput
            style={styles.tokenInput}
            value={botToken}
            onChangeText={setBotToken}
            placeholder="Enter your bot token here..."
            placeholderTextColor="#999"
            secureTextEntry
            multiline
            editable={!isLoading}
          />
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton]}
            onPress={handleSetToken}
            disabled={isLoading || !botToken.trim()}
            activeOpacity={0.7}
          >
            {isLoading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.primaryButtonText}>Connect Bot</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={handleSkip}
            disabled={isLoading}
            activeOpacity={0.7}
          >
            <Text style={styles.secondaryButtonText}>Skip for Now</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.note}>
          Note: Your bot token is stored locally on your device and is never shared.
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  content: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 32,
    color: '#666',
    lineHeight: 22,
  },
  instructions: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  instructionText: {
    fontSize: 14,
    marginBottom: 8,
    color: '#666',
    lineHeight: 20,
  },
  inputContainer: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  tokenInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    minHeight: 80,
    textAlignVertical: 'top',
  },
  buttonContainer: {
    gap: 12,
    marginBottom: 24,
  },
  button: {
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  primaryButton: {
    backgroundColor: '#2196F3',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButtonText: {
    color: '#2196F3',
    fontSize: 16,
    fontWeight: '600',
  },
  note: {
    fontSize: 12,
    textAlign: 'center',
    color: '#999',
    fontStyle: 'italic',
  },
});

export default BotSetup;

