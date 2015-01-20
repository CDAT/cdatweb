function appMain(connection) {
    'use strict';
    var session = connection.session;

    window.session = session;
}

function appError() {
    console.error('Failed to open visualization session.');
}
