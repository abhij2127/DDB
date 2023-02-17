var db = new PouchDB('my_database');
var signallingServer = new WebSocket('ws://localhost:8080');


var peerConnection = new RTCPeerConnection();

// Setting up the data channel
var dataChannel = peerConnection.createDataChannel('my_channel');
dataChannel.onopen = function() {
    console.log('Data channel opened');
};
dataChannel.onclose = function() {
    console.log('Data channel closed');
};
dataChannel.onerror = function(error) {
    console.error('Data channel error:', error);
};

// replication
peerConnection.onicecandidate = function(event) {
    if (event.candidate) {
        signallingServer.send(JSON.stringify({'candidate': event.candidate}));
    }
};
peerConnection.ondatachannel = function(event) {
    dataChannel = event.channel;
    dataChannel.onopen = function() {
        console.log('Data channel opened');
        db.replicate.to(dataChannel);
    };
};


db.changes({
    since: 'now',
    live: true
}).on('change', function(change) {
    if (change.deleted) {
        dataChannel.send(JSON.stringify({'_id': change.id, '_deleted': true}));
    } else {
        db.get(change.id).then(function(doc) {
            dataChannel.send(JSON.stringify(doc));
        });
    }
});


dataChannel.onmessage = function(event) {
    var data = JSON.parse(event.data);
    if (data._id && data._deleted) {
        db.get(data._id).then(function(doc) {
            return db.remove(doc);
        });
    } else if (data._id) {
        db.put(data);
    }
};

