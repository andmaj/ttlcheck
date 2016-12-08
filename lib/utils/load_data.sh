mongorestore --host localhost:27017 -d ts48jk -c subscriptions -drop dump/ts48jk/subscriptions.bson -v
mongorestore --host localhost:27017 -d ts48jk -c events -drop dump/ts48jk/events.bson -v
mongorestore --host localhost:27017 -d ts48jk -c messages -drop dump/ts48jk/messages.bson -v