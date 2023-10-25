
// Switch to the 'link_shortener_db' database
db = db.getSiblingDB('link_shortener_db');

// Create the 'links' collection
db.createCollection('links');
db.createCollection('telegram_users');
db.createCollection('users');
db.createCollection('redirects');

