import React from 'react';
import { motion } from 'framer-motion';
import { Wifi, WifiOff, AlertCircle, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { ConnectionStatus as ConnectionStatusType } from '@/types';

interface ConnectionStatusProps {
  status: ConnectionStatusType;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status }) => {
  const getStatusConfig = () => {
    if (status.connected) {
      return {
        icon: Wifi,
        text: 'Connected',
        color: 'text-green-400',
        bgColor: 'bg-green-900/20',
        borderColor: 'border-green-400/20',
        pulse: true
      };
    }

    if (status.connecting) {
      return {
        icon: Clock,
        text: 'Connecting...',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20',
        borderColor: 'border-yellow-400/20',
        pulse: true
      };
    }

    if (status.error) {
      return {
        icon: AlertCircle,
        text: 'Error',
        color: 'text-red-400',
        bgColor: 'bg-red-900/20',
        borderColor: 'border-red-400/20',
        pulse: false
      };
    }

    return {
      icon: WifiOff,
      text: 'Disconnected',
      color: 'text-gray-400',
      bgColor: 'bg-gray-800/20',
      borderColor: 'border-gray-400/20',
      pulse: false
    };
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${config.bgColor} ${config.borderColor}`}>
      <motion.div
        animate={config.pulse ? { scale: [1, 1.1, 1] } : {}}
        transition={{ repeat: Infinity, duration: 2 }}
      >
        <Icon className={`w-4 h-4 ${config.color}`} />
      </motion.div>
      
      <div className="flex flex-col">
        <span className={`text-sm font-medium ${config.color}`}>
          {config.text}
        </span>
        
        {status.lastConnected && (
          <span className="text-xs text-gray-500">
            Last: {format(status.lastConnected, 'HH:mm:ss')}
          </span>
        )}
        
        {status.error && (
          <span className="text-xs text-red-400" title={status.error}>
            {status.error.length > 20 ? `${status.error.substring(0, 20)}...` : status.error}
          </span>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatus;