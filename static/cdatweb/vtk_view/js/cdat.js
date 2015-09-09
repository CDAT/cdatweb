(function (global, $, vtkWeb) {
    'use strict';

    /**
     * Create a droppable DOM element that handles drags from make_draggable.
     * @param {jQuery} node A jquery DOM element
     * @param {string} cls A selector expected on the element
     * @param {function?} drop A drop event handler
     */
    function make_droppable(node, cls, drop) {
        node.droppable({
            accept: cls,
            hoverClass: 'label-success'
        });
        node.on('drop', function (evt, ui) {
            evt.preventDefault();
            if (drop) {
                drop.call(node, evt, ui);
            }
        });
        return node;
    }

    /**
     * The vtkweb connection
     * @private
     */
    var connection = null;

    /**
     * A list of all open viewports
     * @private
     */
    var viewports = [];

    /**
     * The connection promise object to attach async calls to.
     * @private
     */
    var open = null;

    /**
     * global module for CDAT specific methods
     * @namespace
     */
    var cdat = {
        /**
         * This is an initialization function that should be called once to initiate
         * the vtkweb connection.
         *
         * @param {string} launcher The launcher service endpoint
         * @param {Obect?} config The visualization launcher configuration
         * @returns {$.Deferred} A promise-like object for attaching asynchronous handlers
         *
         * @example
         *   cdat.setup('http://localhost:7000/vtk')
         *     .then(
         *       function () { console.log('loaded successfully'); },
         *       function (code, reason) { console.log('load failed because ' + reason); }
         *   );
         */
        setup: function (config) {
            config = config || {};
            config.application  = config.application || 'default';
            config.sessionManagerURL = 'vtk/launch/';
            open = new $.Deferred();

            /*
             * WARNING: This is an unauthenticated service!  The launcher should really be hidden
             * behind a firewall and the request made server side.  The setup for doing this is more
             * complicated and involves proxying websocket data through the front end webserver.
             *
             *   http://pvw.kitware.com/#!/guide/launching_examples
             *
             * As is, this service is trivial to kill via DOS.
             */

            vtkWeb.start(
                config,
                function (_connection) {
                    connection = _connection;

                    // this should really be fixed at some point
                    connection.secret = 'vtkweb-secret';

                    if (connection.error) {
                        open.reject(null, connection.error);
                    } else {
                        vtkWeb.connect(
                            connection,
                            function () {
                                open.resolve(connection);
                            },
                            function () {
                                open.reject.apply(this, arguments);
                            }
                        );
                    }
                },
                function (code, reason) {
                    open.reject(code, reason);
                });
            return open.promise();
        },

        /**
         * Explicitly close the vtkweb session.  Sessions will be automatically closed after
         * a period of inactivity configured by the server.
         * @returns {$.Deferred} A promise-like object
         *
         * @todo handle closing open viewports
         */
        exit: function () {
            open = null;
            var defer = new $.Deferred();
            if (connection) {
                vtkWeb.stop(connection)
                .then(function () {
                    defer.resolve.apply(this, arguments);
                }, function () {
                    defer.reject.apply(this, arguments);
                });

            }
            return defer.promise();
        },

        /**
         * Open a file for visualization.  The setup method must be called
         * prior to calling this method.  The promise returned by this method
         * has a additional methods.
         *   render: to force the image to rerender when for
         *           example the viewport size has changed
         *   close: to close the viewport when it no longer needed
         *
         * @param {object} config A plot configuration object
         *
         * @param {object[]} config.variables       The variable from the file to display
         * @param {string}   config.template        The plot template to use
         * @param {string}   config.type            The plot type to create
         * @param {string}   config.method          The plot method to use
         * @param {string|$} config.node            The node to draw the visualization in (selector or jquery object)
         * @param {object?}  config.cdatopts        Extra plotting options to pass to cdat
         * @param {object?}  config.viewportopts    Extra options to pass to the viewport
         *
         * @returns {$.Deferred} A promise-like object for attaching handlers
         *
         * @example
         *     var view = cdat.open({
         *     }).then(
         *        function () { console.log('success'); },
         *        function () { console.log('fail'); }
         *     );
         *
         *     // force a rerender
         *     view.render();
         *
         *     // close the view
         *     view.close();
         */
        show: function (config) {
            if (!open) {
                throw new Error('cdat.setup must be called before cdat.show');
            }
            var viewport = null;  // This will store the viewport once it is active

            var defer = new $.Deferred();
            var promise = defer.promise();
            var view, v;

            // backward compatibility
            if (config.file && config.variable) {
                if (typeof config.variable === 'string') {
                    config.variables = [{
                        name: config.variable,
                        file: config.file
                    }];
                } else {
                    config.variables = [];
                    for (v in config.variable) {
                        config.variables.push({
                            name: config.variable[v],
                            file: config.file
                        });
                    }
                }
            }

            open.then(
                function (connection) {
                    connection.session.call(
                        'cdat.view.create',
                        [
                            config.type || 'isofill',
                            config.method || 'default',
                            config.variables,
                            config.template || 'default',
                            config.opts || {}
                        ]
                    ).then(function (_view) {
                        view = _view;

                        // Generate the viewport in the dom element
                        // @todo store open viewport somehow to clean up
                        viewport = new vtkWeb.createViewport(
                            $.extend({
                                view: view,
                                enableInteractions: true,
                                renderer: 'image',
                                interactiveQuality: 100,        // possibly reduce for remote connections
                                stillQuality: 100,              // ditto
                                keepServerInSync: false         // prevent double renders in some cases
                            }, connection, config.viewportopts) // override defaults
                        );
                        viewport.bind(config.node);
                        defer.resolve(viewport);
                    }, function () { defer.reject(arguments); });
                },
                function () { defer.reject(arguments); });

            // append a render function to the promise
            promise.render = function () {
                if (viewport) {
                    viewport.render();
                }
            };

            // append a close method to the promise
            promise.close = function () {
                if (viewport) {
                    viewport.unbind(config.node);
                    // this is technically a race condition, but I can't be bothered
                    // to fix it because it is unlikely to occur
                    connection.session.call('cdat.view.destroy', [view]);
                    viewport = null;
                    view = null;
                }
            };
            return promise;
        },

        /**
         * Returns a method that inserts a vtkWeb viewport inside a jquery panel element.
         * @param {object} options See {@link cdat.show}
         */
        _panel: function (options) {
            return function (panel) {
                var spinner = new Spinner().spin();
                panel.content.append(spinner.el);
                options.node = panel.content.get(0);

                function destroy_spinner() {
                    if (spinner) {
                        spinner.el.remove();
                        spinner = null;
                    }
                    panel.content.off('stop-loading', destroy_spinner);
                }

                var view = cdat.show(options);
                view.then(function () {
                    panel.content.on('stop-loading', destroy_spinner);
                });
                panel.on('resize jspanelloaded jspanelmaximized jspanelnormalized', view.render);
                $('body').on('jspanelclosed', function (evt, id) {
                    if (panel.attr('id') === id.toString()) {
                        view.close();
                    }
                });
            };
        },

        /**
         * Generate a jspanel containing the given content.
         * @returns {$.Panel} The panel dom element
         */
        make_panel: function (container, help, opts) {
            opts = $.extend(true, {content: container}, opts);
            return cdat.Panel(opts).$el;
        },

        /**
         * This is the main method for inserting a cdatweb variable view into a panel.
         * @param {string} file A file name or opendap url
         * @param {string} variable A variable name that exists in the file
         * @param {string} type A view type understood by the visualization server
         * @param {string} method A graphics method
         * @param {string} template A graphics template
         */
        create_plot: function (file, variable, type, method, template) {
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
                    callback: cdat._panel({
                        file: file,
                        variable: variable,
                        type: type,
                        method: method,
                        template: template
                    })
                }
            );
        },

        /**
         * Given a file or opendap url, return an object containing the list of variables
         * in the file.
         * @param {string} filename An absolute path to a file on the vis server.
         * @return {$.Deferred} A promise resolving with the variable info object
         */
        get_variables: function (filename) {
            if (!open) {
                throw new Error('cdat.setup must be called before get_variables');
            }
            var defer = new $.Deferred();
            open.then(
                function (connection) {
                    return connection.session.call(
                        'cdat.file.list_variables',
                        [filename]
                    ).then(
                    function (m) { defer.resolve(m); },
                    function (m) { defer.reject(arguments); }
                    );
                }
            );
            return defer.promise();
        },

        /**
         * Return a list of graphics methods.
         * @return {$.Deferred} A promise resolving with information about graphics methods
         */
        get_graphics_methods: function () {
            if (!open) {
                throw new Error('cdat.setup must be called before get_graphics_methods');
            }
            var defer = new $.Deferred();
            open.then(
                function (connection) {
                    connection.session.call(
                        'cdat.vcs.methods',
                        []
                    ).then(
                    function (m) { defer.resolve(m); },
                    function () { defer.reject(arguments); }
                    );
                }
            );
            return defer.promise();
        },

        /**
         * Return a list of graphics templates.
         * @return {$.Deferred} A promise resolving with a list of strings
         */
        get_templates: function () {
            if (!open) {
                throw new Error('cdat.setup must be called before get_templates');
            }
            var defer = new $.Deferred();
            open.then(
                function (connection) {
                    connection.session.call(
                        'cdat.vcs.templates',
                        []
                    ).then(
                    function (m) { defer.resolve(m); },
                    function () { defer.reject(arguments); }
                    );
                }
            );
            return defer.promise();
        },

        /**
         * Generate a new plot config window.
         */
        make_plot_panel: function (evt) {
            var content, panel, vlist, template, method, opts = {};


            // render a new plot when ready
            function render_when_ready() {
                if (opts.method &&
                    opts.file &&
                    opts.template &&
                    opts.nvars !== null &&
                    opts.vlist[0] &&
                    opts.vlist[1]) {

                    vlist = opts.vlist;
                    if (opts.nvars < 2) {
                        vlist = opts.vlist[0];
                    }
                    cdat.create_plot(
                        opts.file,
                        vlist,
                        opts.family,
                        opts.method,
                        opts.template
                    );
                }
            }

            opts.family = null;
            opts.method = null;
            opts.template = 'default';
            opts.nvars = null;
            opts.file = null;
            opts.vlist = [null, null];

            // need something better
            $('.cdat-temporary-window').remove();

            content = $('<div/>').addClass('cdat-plot-panel')
                .css('width', '500px')
                .css('height', '500px');

            method = $('<span/>')
                .addClass('cdat-graphic-method label label-default')
                .text('Drop a graphic method');

            make_droppable(
                method,
                '.cdat-plot-method',
                function (evt, ui) {
                    var el = ui.draggable, box, v1, v2;
                    opts.nvars = parseInt(el.attr('data-nvars'));
                    opts.family = el.attr('data-family');
                    opts.method = el.attr('data-type');
                    this.text(opts.family + '/' + opts.method);

                    $('.cdat-variable-list').empty();
                    box = $('<h3/>').appendTo('.cdat-variable-list');
                    v1 = $('<span/>')
                        .addClass('cdat-variable-1 label label-default')
                        .text('variable 1')
                        .appendTo(box);

                    make_droppable(
                        v1,
                        '.cdat-variable',
                        function (evt, ui) {
                            var el = ui.draggable;
                            opts.vlist[0] = el.attr('data-name');
                            opts.file = el.attr('data-file');
                            this.text(opts.vlist[0]);
                            render_when_ready();
                        }
                    );

                    if (opts.nvars > 1) {
                        if (opts.vlist[1] === true) {
                            opts.vlist[1] = null;
                        }
                        v2 = $('<span/>')
                        .addClass('cdat-variable-2 label label-default')
                        .text('variable 2')
                        .appendTo(box);

                        make_droppable(
                            v2,
                            '.cdat-variable',
                            function (evt, ui) {
                                var el = ui.draggable;
                                opts.vlist[1] = el.attr('data-name');
                                opts.file = el.attr('data-file');
                                this.text(opts.vlist[1]);
                                render_when_ready();
                            }
                        );
                    } else {
                        opts.vlist[1] = opts.vlist[1] || true;
                    }


                    $('.cdat-variable-list').append(box);
                    render_when_ready();
                }
            );

            template = $('<span/>')
                .addClass('cdat-graphic-template label label-default')
                .text('default');

            make_droppable(
                template,
                '.cdat-template-option',
                function (evt, ui) {
                    var el = ui.draggable;
                    opts.template = el.attr('id');
                    this.text(opts.template);
                    render_when_ready();
                }
            );

            vlist = $('<div/>').addClass('cdat-variable-list');

            content.append([
                $('<h3/>').append(method),
                $('<h3/>').append(template),
                vlist
            ]);
            panel = cdat.make_panel(
                content.get(0),
                null,
                {
                    selector: '.vtk-view-container',
                    title: '<span><i class="fa fa-picture-o"></i>Plot window</span>',
                    overflow: 'hidden'
                });
        }
    };

    global.cdat = cdat;
})(window, jQuery, vtkWeb);
