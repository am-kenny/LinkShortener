
// Switch to the 'link_shortener_db' database
db = db.getSiblingDB('link_shortener_db');

// Create the 'links' collection
db.createCollection('links');
db.createCollection('telegram_users');
db.createCollection('redirects');

db.createCollection('users');
db.users.insert({
    _id: ObjectId(),
    username: 'johndoe',
    full_name: 'John Doe',
    email: 'johndoe@example.com',
    hashed_password: '5ebe2294ecd0e0f08eab7690d2a6ee69',
    disabled: false
})
