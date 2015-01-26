/** @namespace cdat */
(function () {
    window.cdat = window.cdat || {};
    var app = window.cdat;

    // set bootstrap theme for jsPanel
    $.jsPanel.defaults.controls.iconfont = 'bootstrap';

    function renderBrowser(connection, files) {
        el = $('.vtk-file-browser');

        var template = [
            '<div class="tooltip cdat-nowrap" role="tooltip">',
            '<div class="tooltip-arrow"></div>',
            '<div class="tooltip-inner"></div></div>'
        ].join('');
        function makeDraggable(node) {
            if (node.type === 'variable') {
                var v = $(this);
                v.draggable({
                    helper: 'clone',
                    appendTo: 'body',
                    scope: 'variable',
                    zIndex: 1000,
                    refreshPositions: true
                });

                v.find('.node-label').addClass('btn btn-primary');
            } else {
                $(this).tooltip({
                    placement: 'right',
                    delay: {
                        show: 100,
                        hide: 0
                    },
                    title: node.full.replace(/^\./, ''),
                    container: 'body',
                    template: template
                });
            }
        }

        function cleanup(node) {
            if (node.type === 'variable') {
                $(this).draggable('destroy');
            } else {
                $(this).tooltip('destroy');
            }
        }

        el.treeview({data: files, showTags: true, oncreate: makeDraggable, ondestroy: cleanup})
            .find('li.list-group-item')
            .filter(function () {
                return $(this).data('node').type === 'variable';
            })
            .draggable();
        $('.vtk-browser-container').trigger('cdat-render');

        // make the backdrop droppable to open a new vis window
        $('.vtk-view-container').droppable({
            scope: 'variable',
            tolerance: 'pointer',
            over: function (evt, ui) {
                ui.draggable.addClass('cdat-over-target');
            },
            out: function (evt, ui) {
                ui.draggable.removeClass('cdat-over-target');
            }
        }).on('drop', function () {
            cdat.make_panel(
                $('<div/>').get(0),
                null,
                {
                  selector: '.vtk-view-container',
                  title: 'testing',
                  size: {width: 500, height: 500},
                  overflow: 'hidden',
                  callback: app.vtkViewCreator({session: connection.session})
                }
            );
        });

    }

    app.main = function (connection) {
        // default!?
    };

    app.error = function (err) {
        // TODO: create general error page
        var msg;
        try {
            msg = JSON.stringify(err, null, 2);
        } catch (e) {
            msg = err;
        }
        console.error(msg);
    };

    app.variables = function () {
        // list all variables in the given file

    };

    app.browser = function (connection) {
        // connect the vtkweb file browser widget
        connection.session
            .call('file.server.list')
            .then(function (files) {
                renderBrowser(connection, files);
            }, app.error);
    };

    app.vtkViewCreator = function (options) {
        // return a function that generates a view inside
        // a given element

        if (!options.session) {
            throw new Error('A session must be provided.');
        }
        options = $.extend({}, {
            view: -1,
            enableInteractions: true,
            renderer: 'image',
            interactiveQuality: 30,
            stillQuality: 100,
            keepServerInSync: false
        }, options);
        return function (panel) {
            var viewport = new vtkWeb.createViewport(options);
            function render() {
                viewport.render();
            }
            viewport.bind(panel.content.get(0));
            panel.on('resize jspanelloaded jspanelmaximized jspanelnormalized', render)
                .on('jspanelclosed', function () {
                    view.unbind(panel.content.get(0));
                });
        };
    };

    app.make_panel = function (container, help, opts) {
        opts = $.extend(true, {content: container}, opts);
        return cdat.Panel(opts).$el;
    };
})();
