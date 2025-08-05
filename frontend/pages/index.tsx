import React from 'react';
import Head from 'next/head';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  return (
    <>
      <Head>
        <title>Crypto Futures Monitor - Real-time Price Tracking & Arbitrage</title>
        <meta name="description" content="Real-time cryptocurrency futures price monitoring and arbitrage opportunity detection across multiple exchanges" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Open Graph */}
        <meta property="og:title" content="Crypto Futures Monitor" />
        <meta property="og:description" content="Real-time cryptocurrency futures price tracking and arbitrage detection" />
        <meta property="og:type" content="website" />
        
        {/* Additional meta tags */}
        <meta name="keywords" content="cryptocurrency, futures, arbitrage, trading, binance, bybit, okx" />
        <meta name="author" content="Crypto Futures Monitor" />
        
        {/* Prevent zoom on mobile */}
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
      </Head>
      
      <main>
        <Dashboard />
      </main>
    </>
  );
}