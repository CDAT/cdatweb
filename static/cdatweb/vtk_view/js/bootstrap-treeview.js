(function(a, b, c, d) {
    "use strict";
    var e = "treeview";
    var f = function(b, c) {
        this.$element = a(b);
        this._element = b;
        this._elementId = this._element.id;
        this._styleId = this._elementId + "-style";
        this.tree = [];
        this.nodes = [];
        this.selectedNode = {};
        this._init(c);
    };
    f.defaults = {
        injectStyle: true,
        levels: 2,
        expandIcon: "glyphicon glyphicon-plus",
        collapseIcon: "glyphicon glyphicon-minus",
        emptyIcon: "glyphicon",
        nodeIcon: "glyphicon glyphicon-stop",
        color: d,
        backColor: d,
        borderColor: d,
        onhoverColor: "#F5F5F5",
        selectedColor: "#FFFFFF",
        selectedBackColor: "#428bca",
        enableLinks: false,
        highlightSelected: true,
        showBorder: true,
        showTags: false,
        onNodeSelected: d
    };
    f.prototype = {
        remove: function() {
            this._destroy();
            a.removeData(this, "plugin_" + e);
            a("#" + this._styleId).remove();
        },
        _destroy: function() {
            if (this.initialized) {
                this.$wrapper.remove();
                this.$wrapper = null;
                this._unsubscribeEvents();
            }
            this.initialized = false;
        },
        _init: function(b) {
            if (b.data) {
                if (typeof b.data === "string") {
                    b.data = a.parseJSON(b.data);
                }
                this.tree = a.extend(true, [], b.data);
                delete b.data;
            }
            this.options = a.extend({}, f.defaults, b);
            this._setInitialLevels(this.tree, 0);
            this._destroy();
            this._subscribeEvents();
            this._render();
        },
        _unsubscribeEvents: function() {
            this.$element.off("click");
        },
        _subscribeEvents: function() {
            this._unsubscribeEvents();
            this.$element.on("click", a.proxy(this._clickHandler, this));
            if (typeof this.options.onNodeSelected === "function") {
                this.$element.on("nodeSelected", this.options.onNodeSelected);
            }
        },
        _clickHandler: function(b) {
            if (!this.options.enableLinks) {
                b.preventDefault();
            }
            var c = a(b.target), d = c.attr("class") ? c.attr("class").split(" ") : [], e = this._findNode(c);
            if (d.indexOf("click-expand") != -1 || d.indexOf("click-collapse") != -1) {
                this._toggleNodes(e);
                this._render();
            } else if (e) {
                if (this._isSelectable(e)) {
                    this._setSelectedNode(e);
                } else {
                    this._toggleNodes(e);
                    this._render();
                }
            }
        },
        _findNode: function(a) {
            var b = a.closest("li.list-group-item").attr("data-nodeid"), c = this.nodes[b];
            if (!c) {
                console.log("Error: node does not exist");
            }
            return c;
        },
        _triggerNodeSelectedEvent: function(b) {
            this.$element.trigger("nodeSelected", [ a.extend(true, {}, b) ]);
        },
        _setSelectedNode: function(a) {
            if (!a) {
                return;
            }
            if (a === this.selectedNode) {
                this.selectedNode = {};
            } else {
                this._triggerNodeSelectedEvent(this.selectedNode = a);
            }
            this._render();
        },
        _setInitialLevels: function(b, c) {
            if (!b) {
                return;
            }
            c += 1;
            var e = this;
            a.each(b, function f(a, b) {
                if (c >= e.options.levels) {
                    e._toggleNodes(b);
                }
                var f = b.nodes ? b.nodes : b._nodes ? b._nodes : d;
                if (f) {
                    return e._setInitialLevels(f, c);
                }
            });
        },
        _toggleNodes: function(a) {
            if (!a.nodes && !a._nodes) {
                return;
            }
            if (a.nodes) {
                a._nodes = a.nodes;
                delete a.nodes;
            } else {
                a.nodes = a._nodes;
                delete a._nodes;
            }
        },
        _isSelectable: function(a) {
            return a.selectable !== false;
        },
        _render: function() {
            var b = this;
            if (!b.initialized) {
                b.$element.addClass(e);
                b.$wrapper = a(b._template.list);
                b._injectStyle();
                b.initialized = true;
            }
            b.$element.empty().append(b.$wrapper.empty());
            b.nodes = [];
            b._buildTree(b.tree, 0);
        },
        _buildTree: function(b, c) {
            if (!b) {
                return;
            }
            c += 1;
            var d = this;
            a.each(b, function e(b, f) {
                f.nodeId = d.nodes.length;
                d.nodes.push(f);
                var g = a(d._template.item).addClass("node-" + d._elementId).addClass(f === d.selectedNode ? "node-selected" : "").attr("data-nodeid", f.nodeId).attr("style", d._buildStyleOverride(f));
                for (var h = 0; h < c - 1; h++) {
                    g.append(d._template.indent);
                }
                if (f._nodes) {
                    g.append(a(d._template.expandCollapseIcon).addClass("click-expand").addClass(d.options.expandIcon));
                } else if (f.nodes) {
                    g.append(a(d._template.expandCollapseIcon).addClass("click-collapse").addClass(d.options.collapseIcon));
                } else {
                    g.append(a(d._template.expandCollapseIcon).addClass(d.options.emptyIcon));
                }
                g.append(a(d._template.icon).addClass(f.icon ? f.icon : d.options.nodeIcon));
                if (d.options.enableLinks) {
                    g.append(a(d._template.link).attr("href", f.href).append(f.text));
                } else {
                    g.append(f.text);
                }
                if (d.options.showTags && f.tags) {
                    a.each(f.tags, function i(b, c) {
                        g.append(a(d._template.badge).append(c));
                    });
                }
                d.$wrapper.append(g);
                if (f.nodes) {
                    return d._buildTree(f.nodes, c);
                }
            });
        },
        _buildStyleOverride: function(a) {
            var b = "";
            if (this.options.highlightSelected && a === this.selectedNode) {
                b += "color:" + this.options.selectedColor + ";";
            } else if (a.color) {
                b += "color:" + a.color + ";";
            }
            if (this.options.highlightSelected && a === this.selectedNode) {
                b += "background-color:" + this.options.selectedBackColor + ";";
            } else if (a.backColor) {
                b += "background-color:" + a.backColor + ";";
            }
            return b;
        },
        _injectStyle: function() {
            if (this.options.injectStyle && !c.getElementById(this._styleId)) {
                a('<style type="text/css" id="' + this._styleId + '"> ' + this._buildStyle() + " </style>").appendTo("head");
            }
        },
        _buildStyle: function() {
            var a = ".node-" + this._elementId + "{";
            if (this.options.color) {
                a += "color:" + this.options.color + ";";
            }
            if (this.options.backColor) {
                a += "background-color:" + this.options.backColor + ";";
            }
            if (!this.options.showBorder) {
                a += "border:none;";
            } else if (this.options.borderColor) {
                a += "border:1px solid " + this.options.borderColor + ";";
            }
            a += "}";
            if (this.options.onhoverColor) {
                a += ".node-" + this._elementId + ":hover{" + "background-color:" + this.options.onhoverColor + ";" + "}";
            }
            return this._css + a;
        },
        _template: {
            list: '<ul class="list-group"></ul>',
            item: '<li class="list-group-item"></li>',
            indent: '<span class="indent"></span>',
            expandCollapseIcon: '<span class="expand-collapse"></span>',
            icon: '<span class="icon"></span>',
            link: '<a href="#" style="color:inherit;"></a>',
            badge: '<span class="badge"></span>'
        },
        _css: ".list-group-item{cursor:pointer;}span.indent{margin-left:10px;margin-right:10px}span.expand-collapse{width:1rem;height:1rem}span.icon{margin-left:10px;margin-right:5px}"
    };
    var g = function(a) {
        if (b.console) {
            b.console.error(a);
        }
    };
    a.fn[e] = function(b, c) {
        return this.each(function() {
            var d = a.data(this, "plugin_" + e);
            if (typeof b === "string") {
                if (!d) {
                    g("Not initialized, can not call method : " + b);
                } else if (!a.isFunction(d[b]) || b.charAt(0) === "_") {
                    g("No such method : " + b);
                } else {
                    if (typeof c === "string") {
                        c = [ c ];
                    }
                    d[b].apply(d, c);
                }
            } else {
                if (!d) {
                    a.data(this, "plugin_" + e, new f(this, a.extend(true, {}, b)));
                } else {
                    d._init(b);
                }
            }
        });
    };
})(jQuery, window, document);