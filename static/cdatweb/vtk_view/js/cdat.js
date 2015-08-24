(function (global, $, vtkWeb) {
    'use strict';

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
         * @param {Object} config A plot configuration object
         *
         * @param {string}   config.file            An opendap url or a file on the server
         * @param {string}   config.variable        The variable from the file to display
         * @param {string}  [config.type="Isofill"] The plot type to create (Isofill or Volume for now)
         * @param {string|$} config.node            The node to draw the visualization in (selector or jquery object)
         * @param {Object?}  config.cdatopts        Extra plotting options to pass to cdat
         * @param {Object?}  config.viewportopts    Extra options to pass to the viewport
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
            var defer = new $.Deferred();
            var promise = defer.promise();
            var viewport = null;  // This will store the viewport once it is active
            var view = null; // The vtk canvas id

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

            open.then(
                function (connection) {
                    connection.session.call(
                        'cdat.view.create',
                        [
                            config.file,
                            config.variable,
                            config.type,
                            config.opts || {}
                        ]
                    ).then(
                        function (_view) {
                            view = _view;

                            // Generate the viewport in the dom element
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

                            // @todo store open viewport somehow to clean up
                        },
                        function () {
                            defer.reject.apply(this, arguments);
                        }
                    );

                },
                function () {
                    defer.reject.apply(this, arguments);
                }
            );
            return promise;
        }
    };

    global.cdat = cdat;
})(window, jQuery, vtkWeb);
