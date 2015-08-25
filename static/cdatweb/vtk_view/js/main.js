/** @namespace cdat */
(function () {
    window.cdat = window.cdat || {};
    var app = window.cdat;

    // set bootstrap theme for jsPanel
    $.jsPanel.defaults.controls.iconfont = 'font-awesome';

    function setBrowserHeight() {
        var el = $('.vtk-file-browser');
        if (!el.length) {
            return;
        }
        var h = $(window).height();
        var maxheight = h - el.offset().top - 25;
        el.css({
            'max-height': maxheight
        });
    }

    $(window).resize(setBrowserHeight);
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
                    containment: 'window',
                    scroll: false,
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
        $('.vtk-browser-container').trigger('cdat-render').on('cdat-expand', setBrowserHeight);
        setBrowserHeight();

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
        }).on('drop', function (evt, ui) {
            var node = ui.draggable.data('node');
            var varinfo = '    ' + node.file.replace(/^\./, '') + ': ' + node.text;
            cdat.make_panel(
                $('<div/>').get(0),
                null,
                {
                    selector: '.vtk-view-container',
                    title: '<span><i class="fa fa-picture-o"></i>' + varinfo + '</span>',
                    size: {width: 500, height: 500},
                    overflow: 'hidden',
                    callback: cdat.vtkViewCreator({
                        session: connection.session,
                        file: node.file,
                        variable: node.text
                    })
                }
            );
        });

    }

    app.session = $.Deferred();

    app.main = function (connection) {
        cdat.session.resolve(connection.session);
    };

    app.error = function (err) {
        // TODO: create general error page
        cdat.session.reject(err);
    };

    app.browser = function (connection) {
        // connect the vtkweb file browser widget
        connection.session
            .call('file.server.list')
            .then(function (files) {
                renderBrowser(connection, files);
            }, cdat.error);
    };

    app.vtkViewCreator = function (options) {
        // return a function that generates a view inside
        // a given element

        options = $.extend({}, {
            enableInteractions: true,
            renderer: 'image',
            interactiveQuality: 100,
            stillQuality: 100,
            keepServerInSync: false
        }, options);
        return function (panel) {

            var opts = {
                width: 500,
                height: 500
            };
            options.node = panel.content.get(0);
            options.cdatopts = opts;
            var view = cdat.show(options);
            panel.on('resize jspanelloaded jspanelmaximized jspanelnormalized', view.render);
            $('body').on('jspanelclosed', view.close);
        };
    };

    app.make_panel = function (container, help, opts) {
        opts = $.extend(true, {content: container}, opts);
        return cdat.Panel(opts).$el;
    };

    app.create_plot = function (file, variable, type) {
        console.log(
            "Opening file: " + file +
            " variable: " + variable +
            " as type: " + type
        );

        cdat.make_panel(
            $('<div/>').get(0),
            null,
            {
                selector: '.vtk-view-container',
                title: '<span><i class="fa fa-picture-o"></i>' + variable + '</span>',
                size: {width: 500, height: 500},
                overflow: 'hidden',
                callback: cdat.vtkViewCreator({
                    file: file,
                    variable: variable,
                    type: type
                })
            }
        );
    };
})();
