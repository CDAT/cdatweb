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
                    zIndex: 1000
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

    app.make_panel = function (container, help, opts) {
        $.jsPanel({
            selector: 'body',
            title: 'title',
            position: 'top left',
            theme: 'light',
            content: container
        });
    };

    app.make_panel0 = function (container, help, opts) {
        // construct a general collapseable panel

        opts = opts || {};
        var panel = container.find('.panel');
        var panelBody = panel.find('.panel-body');
        var icon = panel.find('i.glyphicon');

        function toggle() {
            panel.toggleClass('cdat-panel-collapsed');
            if (panel.hasClass('cdat-panel-collapsed')) {
                panelBody.slideUp();
                icon.addClass('glyphicon-chevron-down')
                    .removeClass('glyphicon-chevron-up');
                container.trigger('cdat-collapse');
            } else {
                panelBody.slideDown();
                icon.removeClass('glyphicon-chevron-down')
                    .addClass('glyphicon-chevron-up');
                container.trigger('cdat-expand');
            }
        }

        panel.find('.panel-heading').on('click', function () {
            toggle();
        }).tooltip({
            container: 'body',
            delay: {
                show: 500,
                hide: 100
            },
            placement: 'top',
            title: function () {
                if (panel.hasClass('cdat-panel-collapsed')) {
                    return help;
                }
            }
        });
        /*
        if (opts.resizable) {
            container.resizable({
                autoHide: true,
                containment: 'document',
                distance: 5,
                ghost: true,
                helper: 'cdat-resize-ghost'
            });
        }
        */
    };

})();
