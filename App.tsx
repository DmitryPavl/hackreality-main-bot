/**
 * Telegram ChatBot App
 * A React Native app for creating and managing Telegram bots
 *
 * @format
 */

import React, { useState, useEffect } from 'react';
import { StatusBar, useColorScheme } from 'react-native';
import {
  SafeAreaProvider,
} from 'react-native-safe-area-context';
import BotSetup from './src/components/BotSetup';
import ChatScreen from './src/screens/ChatScreen';
import TelegramService from './src/services/TelegramService';

function App() {
  const isDarkMode = useColorScheme() === 'dark';
  const [botInfo, setBotInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkExistingBot();
  }, []);

  const checkExistingBot = async () => {
    try {
      const response = await TelegramService.getBotInfo();
      if (response.success && response.data?.ok) {
        setBotInfo(response.data.result);
      }
    } catch (error) {
      console.log('No existing bot found');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBotConfigured = (bot: any) => {
    setBotInfo(bot);
  };

  const handleBackToSetup = () => {
    setBotInfo(null);
  };

  if (isLoading) {
    return (
      <SafeAreaProvider>
        <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
        {/* You could add a loading screen here */}
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar barStyle={isDarkMode ? 'light-content' : 'dark-content'} />
      {botInfo ? (
        <ChatScreen 
          botInfo={botInfo} 
          onBackToSetup={handleBackToSetup}
        />
      ) : (
        <BotSetup onBotConfigured={handleBotConfigured} />
      )}
    </SafeAreaProvider>
  );
}

export default App;
