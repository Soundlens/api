module.exports = {
  apps: [{
    name: 'nextjs',
    script: 'npm',
    args: 'start',
    cwd: '/var/www/html/app/frontend',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
} 