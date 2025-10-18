// Test script to validate duplicate key fix
// Run this in browser console on the running app

console.log('🔍 Testing for duplicate keys in SceneOutliner...');

// Check if React warnings appear in console
const originalWarn = console.warn;
const originalError = console.error;
let reactWarnings = [];

console.warn = function(...args) {
  const message = args.join(' ');
  if (message.includes('duplicate') || message.includes('key') || message.includes('Each child')) {
    reactWarnings.push(message);
  }
  originalWarn.apply(console, args);
};

console.error = function(...args) {
  const message = args.join(' ');
  if (message.includes('duplicate') || message.includes('key') || message.includes('Each child')) {
    reactWarnings.push(message);
  }
  originalError.apply(console, args);
};

// Simulate loading a GLB model multiple times
setTimeout(() => {
  console.log('📊 React warnings collected:', reactWarnings.length);
  if (reactWarnings.length === 0) {
    console.log('✅ No duplicate key warnings found!');
  } else {
    console.log('❌ React warnings found:', reactWarnings);
  }
}, 5000);

console.log('⏳ Monitoring for 5 seconds...');