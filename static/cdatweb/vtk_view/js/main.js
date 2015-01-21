(function () {
    window.cdat = window.cdat || {};
    var app = window.cdat;

    function renderVariables(connection, filename, variables) {
        // element containing the list of variables
        var el = $('.vtk-variable-browser').empty();

        // element containing info about the selected variable
        var vl = $('.vtk-variable-info').empty();

        $('.vtk-variable-current-file').text(filename);

        var vlist;
        if (variables) {
            vlist = $('<ul/>');
            _.each(variables, function (info, vname) {
                var li = $('<li/>');
                li.text(vname);
                vlist.append(li);
            });
        } else {
            vlist = $('<p>');
            vlist.text('Cannot read "' + filename + '".');
        }

        el.append(vlist);
    }

    function renderBrowser(connection, files) {
        $('.vtk-file-browser').fileBrowser({
            data: [files],
            session: connection.session
        })
        .bind('file-click',/* directory-click directory-not-found file-group-click'*/ function (e) {
            // e.type, e.name, e.path, e.relativePathList

            if (e.relativePathList) {
                connection.session
                    .call('file.server.info', e.relativePathList)
                    .then(function (info) {
                        var filename = e.relativePathList[0].split('/').slice(1).join('/');
                        info = info || {variables: null};
                        renderVariables(connection, filename, info.variables);
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
