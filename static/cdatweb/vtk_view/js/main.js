(function () {
    window.cdat = window.cdat || {};
    var app = window.cdat;

    function renderVariables(connection, variables) {
        // element containing the list of variables
        var el = $('.vtk-variable-browser').empty();

        // element containing info about the selected variable
        var vl = $('.vtk-variable-info').empty();

        var vlist = $('<ul/>');
        variables.forEach(function (v) {
            var li = $('<li/>');

            vlist.append(li);
        });

        el.append(vlist);
    }

    function renderBrowser(connection, files) {
        $('.vtk-file-browser').fileBrowser({
            data: [files],
            session: connection.session
        })
        .bind('file-click',/* directory-click directory-not-found file-group-click'*/ function (e) {
            // e.type, e.name, e.path, e.relativePathList

            if (e.relativePathList.length) {
                connection.sessions
                    .call('file.server.info', e.relativePathList[0])
                    .then(function (variables) {
                        renderVariables(connection, variables);
                    });
            }

        });
    }

    app.main = function (connection) {
        // default!?
    };

    app.error = function (msg) {
        // TODO: create error page
        console.error(msg);
    };

    app.variables = function () {
        // list all variables in the given file

    };

    app.browser = function (connection) {
        // connect the vtkweb file browser widget
        connection.session
            .call('file.server.directory.list', ['.'])
            .then(function (files) {
                renderBrowser(connection, files);
            });
    };
})();
