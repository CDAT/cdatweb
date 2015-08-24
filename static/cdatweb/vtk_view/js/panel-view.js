/*global cdat*/
/**
 * This file defines the infrastructure for generating visualization panels,
 * which are wrapped jspanel classes with extra support for custom layouts.
 */
(function () {
    'use strict';

    var _id = 0;
    function newId() {
        _id += 1;
        return _id.toString(16);
    }

    /**
     * Panel option object type.
     * @typedef cdat.Panel.options
     * @type object
     * @property {string} container="body" Selector for the ui container
     * @property {DOM} [content] DOM element to place inside the panel
     * @property {string} type="cdat-panel" The widget type for css styling
     * @property {string} theme="default" The widget theme a la bootstrap default/primary, etc
     * @property {string|function} title The widget title
     * @property {object} controls={} Set control keys to false to disable,
     * @property {object|"scroll"|"hidden"} overflow="hidden" Set overflow behavior
     * @property {object|"auto"} size="auto" The initial size of the panel
     * @property {string} position="auto" The initial position of the panel
     * @property {function|function[]} callback
     *     Function(s) to call after the panel is created
     */

    /**
     * Main panel widget class defining ui behavior.  Built on top of jsPanel.
     * @class
     * @param {cdat.Panel.options} options Panel options overriding static options
     * @returns {cdat.Panel}
     */
    cdat.Panel = function (options) {
        if (!(this instanceof cdat.Panel)) {
            return new cdat.Panel(options);
        }
        var _this = this;

        /**
         * Current options object
         * @type cdat.Panel.options
         */
        this.options = $.extend(true, {}, cdat.Panel.defaults, options);

        /**
         * The parent node id read only
         */
        this.id = newId();

        /**
         * jQuery selection of the main widget node
         */
        this.$el = $.jsPanel({
            addClass: {
                header: this.options.type + '-header',
                footer: this.options.type + '-footer',
                content: this.options.type + '-content'
            },
            id: this.id,
            selector: this.options.container,
            theme: this.options.theme,
            title: this.options.title,
            controls: this.options.controls,
            size: this.options.size,
            content: this.options.content || $('<div/>'),
            callback: this.options.callback,
            draggable: {
                containment: this.options.container
            },
            resizable: {
                containment: this.options.container
            },
            overflow: this.options.overflow
        });

        /**
         * DOM element of the main widget node
         */
        this.el = this.$el.get(0);

        return this;
    };

    /**
     * @instance
     * @type cdat.Panel.options
     */
    cdat.Panel.defaults = {
        container: '.vtk-view-container',
        content: null,
        type: 'cdat-panel',
        selector: 'body',
        theme: 'default',
        title: 'The developer should define the title here',
        controls: {iconfont: 'font-awesome'},
        overflow: 'hidden',
        size: 'auto',
        position: 'auto',
        callback: $.noop
    };
})();
