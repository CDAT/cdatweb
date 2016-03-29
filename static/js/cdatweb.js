$(function() {

    cdat.setup()
        .then(function() {
            console.log('Vis instance launched');
        },
        function() {
            console.log(arguments);
        });

    /**
     * Make the given element draggable.
     * @param {jQuery} node A jquery DOM element
     * @param {function?} ondrag A drag event handler
     */
    function make_draggable(node, ondrag) {
        node.draggable({
            appendTo: '.vtk-view-container',
            zIndex: ~(1 << 31), // because jsPanel, sigh...
            containment: '.vtk-view-container',
            helper: "clone",
            addClass: "cdat-grabbing",
            opacity: 0.75
        }).addClass('cdat-draggable')
            .on('start', function(evt) {
                if (ondrag) {
                    ondrag.call(node, evt);
                }
            });

        return node;
    }

    function get_csrf() {
        var nameEQ = "csrftoken=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function esgf_search_submit() {
        var host = document.getElementById("host").value;
        console.log(host);
        var text = $("input[id=text]").val();
        var project = $("input[id=project]").val();
        var limit = document.getElementById("limit").value;
        console.log(limit);
        var offset = $("input[id=offset]").val();

        var jsonObj = {};
        jsonObj.host = host;
        jsonObj.text = text;
        jsonObj.project = project;
        jsonObj.limit = limit;
        jsonObj.offset = offset;

        var jsonStr = JSON.stringify(jsonObj);
        var search_url = '/esgf_search/';
        var csrftoken = get_csrf();

        $.ajax({
            type: "POST",
            url: search_url,
            async: true,
            cache: false,
            headers: { "X-CSRFToken": csrftoken },
            data: { query: jsonStr },
            dataType: 'json',
            success: function(data) {
                var results = data.data;
                console.log(results);
                var element = $("<div></div>");
                if (results.length == 0) {
                    element.text("No Results");
                }

                for (var x = 0; x < results.length; x++) {
                    var obj = results[x];
                    var wrapper = $("<p></p>");
                    var eol = "<br/>";
                    var split = "<hr>";
                    wrapper.append(split);

                    var project = "Project: " + obj.project + eol;
                    wrapper.append(project);

                    var experiment = "Experiment: " + obj.experiment + eol;
                    wrapper.append(experiment);

                    var title = "Title: " + obj.title + eol;
                    wrapper.append(title);

                    var download = $("<a></a>");
                    download.attr("href", obj.http).text("Download");
                    wrapper.append(download);

                    wrapper.append(eol + "Variables: " + eol);
                    var var_wrap = $("<ul></ul>");

                    if (obj.variables.length == 0) {
                        var no_vars = $("<li></li>");
                        no_vars.text("No Listed Variables");
                        var_wrap.append(no_vars);
                    }

                    for (var v = 0; v < obj.variables.length; v++) {
                        var variable = $("<li></li>");
                        if (typeof (obj.dap) === "undefined") {
                            variable.text(obj.variables[v].name);
                        }
                        else {
                            var _dap = obj.dap;
                            if (_dap.substring(_dap.length - 5, _dap.length) == ".html") {
                                _dap = _dap.substring(0, _dap.length - 5)
                            }
                            var link = $("<a></a>");
                            make_draggable(link);
                            link.text(obj.variables[v].name)
                                .attr("data-name", obj.variables[v].name)
                                .attr("data-file", _dap)
                                .addClass('cdat-variable');
                            variable.append(link);
                        }
                        var_wrap.append(variable);
                    }

                    wrapper.append(var_wrap);
                    element.append(wrapper);
                }

                title = "Search Results";
                //newPanel(title, element);
                var new_tile = '<li id="esgf_search_results" class="tile" >' + header1 + title + header2 + header3 + '</li>';
                add_tile(new_tile, 'esgf_search_results', { ignore: 'true' });
                $('#esgf_search_results').find('.tile-contents').append(element);

            },
            error: function(request, status, error) {
                $("div .error").html(request + " | " + status + " | " + error).show();
            }
        });
    }

    function get_children(path, parent, level) {
        if (parent.attr("data-loaded") === "true") {
            return;
        }
        var next_level = parseInt(level) + 1;
        var parent_id = parent.attr('id');

        var jsonObj = new Object;
        jsonObj.path = path;
        var jsonStr = JSON.stringify(jsonObj);
        var search_url = '/get_children/';
        $.ajax({
            type: "POST",
            url: search_url,
            async: true,
            cache: false,
            data: { query: jsonStr },
            dataType: 'json',
            success: function(data) {
                results = data.dirs;
                for (var x = 0; x < results.length; x++) {
                    var short_name = results[x].split("/")
                    var display_name = short_name[short_name.length - 1]
                    display_name = display_name.replace("+", "_");
                    display_name = display_name.replace(".", "_");
                    var element;

                    element = $("<li><a></a><ul></ul></li>");
                    element.find("a").click(function(e) {
                        if ($(this).attr("data-loaded") === "true") {
                            return;
                        }
                        var path = $(this).attr("data-path");
                        var ul = $(this).parent().find("ul");
                        get_children(path, ul, next_level);
                        $(this).attr('data-loaded', "true");
                    }).text(display_name).attr("data-path", results[x]);
                    element.find("ul").attr("id", parent_id + "_" + display_name);
                    parent.append(element);
                }
                results = data.files;
                for (var x = 0; x < results.length; x++) {
                    var short_name = results[x].split("/")
                    var display_name = short_name[short_name.length - 1]
                    display_name = display_name.replace("+", "_");
                    display_name = display_name.replace(".", "_");
                    var element;

                    element = $("<li><a></a><ul></ul></li>");
                    element.find("a").click(function(e) {
                        if ($(this).attr("data-loaded") === "true") {
                            return;
                        }
                        var path = $(this).attr("data-path");
                        var ul = $(this).parent().find("ul");
                        get_variables(path, ul, next_level);
                        $(this).attr('data-loaded', "true");
                    }).text(display_name).attr("data-path", results[x]);
                    element.find("ul").attr("id", parent_id + "_" + display_name);
                    parent.append(element);
                }
            },
            error: function(request, status, error) {
                console.log(status + " | " + error)
            }
        });
    }

    function get_variables(path, parent, level) {
        cdat.get_variables("/var/www/Data/ne120_monthly_ens3/gridded/1979/gridded_ne120_v0.3_00003.cam.h0.1979-01.nc").then(
            //testing above
            //cdat.get_variables(path).then(
            function(variables) {
                for (v in variables) {
                    element = $("<li><a></a></li>");
                    make_draggable(element);
                    element.text(variables[v].name || v)
                        .attr("data-name", v)
                        .attr("data-file", path)
                        .addClass('cdat-variable');
                    parent.append(element);
                }
            }, function() { console.log(arguments) }
        )
    }

    var docHeight, docWidth, maxCols, maxHeight, tileHeight, tileWidth;
    var widthScale = .75; //represents the portion of the window allocated to tiles. Side bar is currently 25%
    var sidebarWidth = ($(window).width() * (1 - widthScale));
    calcMaxSize();
    $('#slide-menu-left').css('width', sidebarWidth);
    $('.wrapper').height(maxHeight * tileHeight).css({
        "width": ($(window).width() * widthScale),
        "float": "right"
    });
    $('.tile-board').css({
        'height': maxHeight * tileHeight
    });
    var tiles = [];
    var imgInstance = 0;
    var instance = 0; //variable that increments for every codemirror launched.
    var resize_handle_html = '<span class="gs-resize-handle gs-resize-handle-both"></span>';
    // Define a widget
    var header3 = '';
    var contents = '';
    var optionContents = '';
    var header1 = [
        '<div class="tile-panel panel-default">',
        ' <div class="tile-panel-heading">',
        '  <div class="panel-header-title text-center">',
        '    <button type="button" class="btn btn-default btn-xs options" style="float:left;">',
        '     <span class="fa fa-cog" aria-label="Options"></span>',
        '    </button>',
        '    <button type="button" class="btn btn-default btn-xs remove"  style="float:right;">',
        '     <span class="fa fa-times" aria-label="Close"></span>',
        '    </button>',
        '     <p style="text-align: center">'
    ].join('');
    // Widget Name
    var header2 = ['     <p>',
        '   </div>',
        '  </div>',
        ' </div>',
        ' <div class="tile-panel-body" data-direction="horizontal" data-mode="slid">',
        '  <div class="tile-contents">'
    ].join('');
    // Widget Contents
    var content = '<div class="content"></div>';
    header3 += ' </div></div></div>';

    var altheader1 = ['<div class="tile-panel panel-default">',
        ' <div class="tile-panel-heading">',
        '  <div class="panel-header-title text-center">',
        '     <p style="text-align: center">'
    ].join('');

    var dragStartX = 0;
    var dragStartY = 0;
    var dragStartSizeX = 0;
    var dragStartSizeY = 0;
    var dragStartId = '';
    var dragStartOffset = {
        top: 0,
        left: 0
    };
    var widgetMargins = 1;
    var resizeStartSizeX = 0;
    var resizeStartSizeY = 0;
    var resizeStartX = 0;
    var resizeStartY = 0;
    var resizeDir = '';
    var needsFixXBool = true;
    var needsFixYBool = true;
    var fixValX = 99;
    var fixValY = 99;
    var mode = {
        light: 'day'
    };
    boardSetup(maxCols, maxHeight);
    var opts = {
        lines: 17, // The number of lines to draw
        length: 40, // The length of each line
        width: 10, // The line thickness
        radius: 30, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        direction: 1, // 1: clockwise, -1: counterclockwise
        color: '#000', // #rgb or #rrggbb or array of colors
        speed: 1, // Rounds per second
        trail: 100, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '50%', // Top position relative to parent
        left: '50%' // Left position relative to parent
    };
    var esgf_search_terms = {};
    var esgf_search_nodes = [];

    function getFixVal(layouts) {
        if (layouts.length == 0) {
            fixValY = 0;
            fixValX = 0;
            mode = 'day';
            return;
        }
        for (var i = 0; i < layouts.length; i++) {
            layouts[i] = layoutFix(layouts[i]);
            if (layouts[i].x == 1) {
                needsFixXBool = false;
            } else {
                if (layouts[i].x < fixValX) {
                    fixValX = layouts[i].x;
                }
            }
            if (layouts[i].y == 1) {
                needsFixYBool = false;
            } else {
                if (layouts[i].y < fixValY) {
                    fixValY = layouts[i].y;
                }
            }
        }
    }
    var counter = 0;

    $("body").ready(function() {
        //MATT
        $('#new_plot').click(function() {
            var new_tile = '<li id="' + counter + '" class="tile" >' + header1 + 'plot ' + counter + header2 + contents + header3 + '</li>';
            add_tile(new_tile, counter, { ignore: 'true' } /* , call back function here */);
            counter = counter + 1;
        });
        
        $('#cdat_esgf_submit').click(function() { esgf_search_submit() });
        
        $('#show_esgf_form').click(function() {
            $('#esgf_search').toggle();
        });
        
        $('#hide_esgf_form').click(function() {
            $('#esgf_search').hide();
        });

        $(".cdatweb-file-browser > ul > li > a.cdatweb-dir").click(function(e) {
            if ($(this).attr("data-loaded") === "true") {
                return;
            }
            get_children($(this).attr("data-path"), $(this).next("ul"), 1);
            $(this).attr('data-loaded', 'true');
            e.preventDefault();
        });

        $(".cdatweb-file-browser > ul > li > a.cdatweb-file").click(function(e) {
            if ($(this).attr("data-loaded") === "true") {
                return;
            }
            get_variables($(this).attr("data-path"), $(this).next("ul"), 1);
            $(this).attr('data-loaded', 'true');
            e.preventDefault();
        });

        cdat.get_graphics_methods().then(
            function(plots) {
                parent = $(".cdatweb-plot-types");
                var item = $("<li><a></a><ul class='qtree'></ul></li>");
                var child = $("<li><a></a></li>");
                var plot_fam_item, plot_family, plot_item;
                for (plot_family in plots) {
                    if (plots.hasOwnProperty(plot_family) === false) {
                        continue;
                    }
                    plot_fam_item = item.clone();
                    plot_fam_item.attr('id', plot_family);
                    plot_fam_item.find('a').text(plot_family);
                    for (plot_type in plots[plot_family]) {
                        plot_item = child.clone();
                        plot_item.attr('id', plot_type);
                        plot_item
                            .addClass('cdat-plot-method')
                            .attr('data-type', plot_type)
                            .attr('data-family', plot_family)
                            .attr('data-nvars', plots[plot_family][plot_type].nvars)
                            .text(plot_type);
                        plot_item.hide();
                        make_draggable(plot_item);
                        plot_fam_item.find("ul").append(plot_item);
                    }
                    parent.append(plot_fam_item);
                    plot_fam_item.hide();
                }
            },
            function() {
                console.log(arguments)
            }
        );

        cdat.get_templates().then(
            function(templates) {
                parent = $(".cdatweb-plot-templates");
                var item = $("<li><a></a><ul class='qtree'></ul></li>");
                var temp_fam_item, temp_name;
                for (temp_name = 0; temp_name < templates.length; temp_name++) {
                    temp_fam_item = item.clone();
                    temp_fam_item.attr('id', templates[temp_name])
                        .text(templates[temp_name])
                        .addClass('cdat-template-option');
                    make_draggable(temp_fam_item);
                    parent.append(temp_fam_item);
                    temp_fam_item.hide();
                }
            },
            function() {
                console.log(arguments)
            }
        );

        $(".qtree").quicktree();
    });

    //setup the hander to fix the windows after a resize
    $(window).resize(function() {
        if (event.target == this) {
            if (this.resizeTO) clearTimeout(this.resizeTO);
            this.resizeTO = setTimeout(function() {
                $(this).trigger('resizeEnd');
            }, 500);
        }

    });

    $(window).bind('resizeEnd', function() {
        //handleWindowResize();
    });

    function getFile(url, id) {

    }



    function isFolder(file) {
        return file.split('.').pop() == file;
    }

    function populateFile(file) {
        alert(file);
    }

    function add_sidebar_window(html, id) {
        var w = $('#' + id);
        $(w).replaceWith(html);
        console.log(id);
        $(w).css({
            'z-index': 1,
            'opacity': 1
        });
        return $(w);
    }
    function add_tile(html, id, options, callback) {
        $('.tile-holder').append(html);
        var w = $('#' + id);
        $(w).css({
            'z-index': 1,
            'opacity': 0
        });
        console.log('setting options button id to ' + id + '_window_options');
        $(w).find('.fa-cog').parent().attr({
            id: id + '_options'
        });
        $(w).find('.fa-times').parent().attr({
            id: id + '_close'
        });

        $(w).draggable({
            //containment: '.tile-board',
            helper: 'clone',
            start: function(event, ui) {
                ui.helper.find('.tile-contents').hide();
                ui.helper.addClass('ui-draggable-dragging-no-transition');
                ui.helper.animate({
                    'opacity': '0.5',
                    'z-index': 10,
                    'width': '20%',
                    'height': '20%'
                });
            },
            stop: function(event, ui) {
                ui.helper.find('.tile-contents').show();
                var pos = grid_from_offset(ui.position);
                dragFixup(pos.col, pos.row);
                $(ui.helper).css({
                    'opacity': '1.0',
                    'z-index': 1
                });
            },
            cursorAt: {
                left: 200,
                top: 15
            }
        });

        $(w).resizable({
            handles: 'n, w, e, s',
            animate: true,
            animateDuration: 'fast',
            animateEasing: 'easeOutQuint',
            // containment: '.wrapper',
            helper: 'ui-resizable-helper',
            grid: [tileWidth, tileHeight],
            start: function(event, ui) {
                handleResizeStart(event, ui);
            },
            resize: function(event, ui) {
                event.stopPropagation();
            },
            stop: function(event, ui) {
                handleResizeStop(event, ui);
                event.stopPropagation();
            }
        });

        $(w).find('.ui-resizable-n').mousedown(function() {
            resizeDir = 'n';
        });
        $(w).find('.ui-resizable-s').mousedown(function() {
            resizeDir = 's';
        });
        $(w).find('.ui-resizable-e').mousedown(function() {
            resizeDir = 'e';
        });
        $(w).find('.ui-resizable-w').mousedown(function() {
            resizeDir = 'w';
        });

        tiles.push($(w).attr('id'));

        //Setup the live tile for the options menu
        $(w).find('.live-tile').liveTile({
            direction: 'horizontal'
        });

        //Stop the body from being able to drag
        $(w).find('.tile-panel-body').mousedown(function(event) {
            event.stopPropagation();
        });

        $(w).find('.tile-panel-heading').mousedown(function(event) {
            dragStartId = w[0].id;
            var grid = $('#' + dragStartId);
            dragStartX = parseInt(grid.attr('col'));
            dragStartY = parseInt(grid.attr('row'));
            dragStartSizeX = parseInt(grid.attr('sizex'));
            dragStartSizeY = parseInt(grid.attr('sizey'));
            dragStartOffset = grid.offset();
        });

        $(w).find('.remove').click(function(e) {

            $('#' + id).remove();
            for (var i = tiles.length - 1; i >= 0; i--) {
                if (tiles[i] == id) {
                    tiles.splice(i, 1);
                    break;
                }
            }
            positionFixup();
        });

        $(w).find('.options').click(function(e) {

        });

        if (options != null && options.ignore != 'true') {
            $(w).attr({
                'row': options.y,
                'col': options.x,
                'sizex': options.sizex,
                'sizey': options.sizey
            });
            update_board(id);
            var tile_offset = offset_from_location(parseInt($(w).attr('row')), parseInt($(w).attr('col')));
            $(w).css({
                "top": tile_offset.top,
                "left": tile_offset.left,
                "width": $(w).attr('sizex') * tileWidth,
                "height": $(w).attr('sizey') * tileHeight
            });
            console.log(tileWidth);
            console.log(tileHeight);
            console.log(options.sizex);
            console.log(options.sizey);
        } else {
            positionFixup();
        }
        if ($('body').attr('class') == 'night') {
            $(w).find('.tile-panel-body').css({
                'background-color': '#0C1021;',
                'border-color': '#00f;',
                'color': '#fff'
            });
        }
        $(w).animate({
            'opacity': 1
        }, 'slow', 'easeOutCubic');

        if (callback != null) {
            callback();
        }
        instance++;
        return $(w);
    }
    function handleResizeStart(event, ui) {
        resizeStartX = parseInt(ui.element.attr('col'));
        resizeStartSizeX = parseInt(ui.element.attr('sizex'));
        resizeStartY = parseInt(ui.element.attr('row'));
        resizeStartSizeY = parseInt(ui.element.attr('sizey'));
        //noinspection FallThroughInSwitchStatementJS
        switch (resizeDir) {
            case 'n':
                $('#' + ui.element.attr('id')).css({
                    '-webkit-transition': 'height 200ms easeOutQuint!important',
                    '-moz-transition': 'height 200ms easeOutQuint!important',
                    '-o-transition': 'height 200ms easeOutQuint!important',
                    '-ms-transition': 'height 200ms easeOutQuint!important',
                    'transition': 'height 200ms easeOutQuint!important'
                });
                break;
            case 's':
                break;
            case 'e':
                break;
            case 'w':
                break;
        }
        event.stopPropagation();
    }

    function handleResizeStop(event, ui) {
        resizeFixup(ui);
        var el = ui.element;
        el.css({
            'left': (parseInt(el.attr('col')) - 1) * tileWidth + $('.tile-holder').offset().left,
            'height': parseInt(el.attr('sizey')) * tileHeight,
            'width': parseInt(el.attr('sizex')) * tileWidth
        });
        setTimeout(function(el) {
            if (resizeDir == 'n' && parseInt(el.attr('row')) == 1) {
                el.css({
                    'top': $('.tile-board').offset().top,
                    'height': tileHeight * parseInt(el.attr('sizey')),
                    'width': tileWidth * parseInt(el.attr('sizex'))
                });
            } else if (resizeDir == 's') {
                el.css({
                    'height': tileHeight * parseInt(el.attr('sizey')),
                    'width': tileWidth * parseInt(el.attr('sizex'))
                });
            } else if (resizeDir == 'e' && parseInt(el.attr('col')) + parseInt(el.attr('sizex')) - 1 == maxCols) {
                el.css({
                    'left': tileWidth * (parseInt(el.attr('col')) - 1) + $('.tile-holder').offset().left,
                    'width': tileWidth * parseInt(el.attr('sizex')),
                    'height': tileWidth * parseInt(el.attr('sizey'))
                });

            } else if (resizeDir == 'w' && parseInt(el.attr('col')) == 1) {
                el.css({
                    'width': tileWidth * parseInt(el.attr('sizex')),
                    'height': tileWidth * parseInt(el.attr('sizey')),
                    'left': $('.tile-board').offset().left
                });
            } else {
                el.css({
                    'left': (parseInt(el.attr('col')) - 1) * tileWidth + $('.tile-holder').offset().left,
                    'height': parseInt(el.attr('sizey')) * tileHeight,
                    'width': parseInt(el.attr('sizex')) * tileWidth
                });
            }
        }, 500, el);
    }

    function recursiveResize(moved, dir, diff, side, id) {
        var curWindow = $('#' + id);
        var x = parseInt(curWindow.attr('col'));
        var y = parseInt(curWindow.attr('row'));
        var sizex = parseInt(curWindow.attr('sizex'));
        var sizey = parseInt(curWindow.attr('sizey'));
        var toAdd = true;
        var adj = [];
        if (dir == 'up') {
            if (side == 'n') {
                //var adj = new Set();
                for (var i = x; i < x + sizex; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[i - 1][y - 2].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[i - 1][y - 2].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                var startY = curWindow.offset().top;
                curWindow.attr({
                    'row': y - diff,
                    'sizey': sizey + diff
                });
                curWindow.css({
                    //'top':(y-diff)*tileHeight + $('.navbar').height() - 1,
                    'top': startY - (diff * tileHeight),
                    'height': (sizey + diff) * tileHeight
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, done resizing

                } else {
                    //we need to keep resizing
                    recursiveResize(moved, dir, diff, 's', helperReturn.adj[0]);
                }
            } else if (side == 's') {
                for (var i = x; i < x + sizex; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[i - 1][y + sizey - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[i - 1][y + sizey - 1].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'sizey': sizey - diff
                });
                curWindow.css({
                    'height': (sizey - diff) * tileHeight
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'n', helperReturn.adj[0]);
                }
            } else {
                //error

            }
        } else if (dir == 'down') {
            if (side == 'n') {
                for (var i = x; i < x + sizex; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[i - 1][y - 2].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[i - 1][y - 2].tile);
                    }
                }
                //check the base case-> all windows have been moved
                moved.add(id);
                var helperReturn = adjHelper(adj, moved);
                var startY = curWindow.offset().top;
                curWindow.attr({
                    'row': y - diff,
                    'sizey': sizey + diff
                });
                curWindow.css({
                    //'top':(y-diff)*tileHeight + $('.navbar').height() - 1,
                    'top': startY - (diff * tileHeight),
                    'height': (sizey + diff) * tileHeight
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, done resizing

                } else {
                    //we need to keep resizing
                    recursiveResize(moved, dir, diff, 's', helperReturn.adj[0]);
                }
            } else if (side == 's') {
                for (var i = x; i < x + sizex; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[i - 1][y + sizey - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[i - 1][y + sizey - 1].tile);
                    }
                }
                //check the base case-> all windows have been moved
                moved.add(id);
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'sizey': sizey - diff
                });
                curWindow.css({
                    'height': (sizey - diff) * tileHeight
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished == true) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'n', helperReturn.adj[0]);
                }
            } else {
                //error

            }
        } else if (dir == 'right') {
            if (side == 'e') {
                for (var i = y; i < y + sizey; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[x + sizex - 1][i - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[x + sizex - 1][i - 1].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'sizex': sizex - diff
                });
                curWindow.css({
                    'width': (sizex - diff) * tileWidth
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'w', helperReturn.adj[0]);
                }
            } else if (side == 'w') {
                for (var i = y; i < y + sizey; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[x - 2][i - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[x - 2][i - 1].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'col': x - diff,
                    'sizex': sizex + diff
                });
                curWindow.css({
                    'width': (sizex + diff) * tileWidth,
                    'left': (x - diff - 1) * tileWidth + $('.tile-holder').offset().left
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'e', helperReturn.adj[0]);
                }
            } else {
                //error

            }
        } else if (dir == 'left') {
            if (side == 'e') {
                for (var i = y; i < y + sizey; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[x + sizex - 1][i - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[x + sizex - 1][i - 1].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'sizex': sizex - diff
                });
                curWindow.css({
                    'width': (sizex - diff) * tileWidth
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'w', helperReturn.adj[0]);
                }
            } else if (side == 'w') {
                for (var i = y; i < y + sizey; i++) {
                    for (var j = 0; j < adj.length; j++) {
                        if (adj[j] == board[x - 2][i - 1].tile) {
                            toAdd = false;
                            break;
                        } else {
                            toAdd = true;
                        }
                    }
                    if (toAdd) {
                        adj.push(board[x - 2][i - 1].tile);
                    }
                }
                var helperReturn = adjHelper(adj, moved);
                curWindow.attr({
                    'col': x - diff,
                    'sizex': sizex + diff
                });
                curWindow.css({
                    'width': (sizex + diff) * tileWidth,
                    'left': (x - diff - 1) * tileWidth + $('.wrapper').offset().left
                });
                update_board(id);
                moved.add(id);
                removeHelper(curWindow);
                if (helperReturn.finished) {
                    //base case, all windows have been resized

                } else {
                    //we need to keep resizeing 
                    recursiveResize(moved, dir, diff, 'e', helperReturn.adj[0]);
                }
            } else {
                //error

            }
        } else {
            //error

        }
    }

    function adjHelper(adj, moved) {
        var done = true;
        adj.forEach(function(item) {
            if (!moved.has(item)) {
                done = false;
            } else {
                adj.splice(adj.indexOf(item), 1);
            }
        }, moved);

        return {
            'finished': done,
            'adj': adj
        };
    }

    function removeHelper(tile) {
        if (parseInt(tile.attr('sizex')) <= 0 || parseInt(tile.attr('sizey')) <= 0) {
            $.when(tile.fadeOut()).then(function() {
                tile.remove();
            });
            for (var i = tiles.length - 1; i >= 0; i--) {
                if (tiles[i] == tile.attr('id')) {
                    tiles.splice(i, 1);
                    break;
                }
            }
        }
    }

    function resizeFixup(ui) {
        var resizeId = ui.element.attr('id');
        //which direction did it resize?
        if (resizeDir == 'n') {
            var diff = virtical_location(ui.originalPosition.top, 0) - virtical_location(ui.helper.position().top, 0);
            if (diff <= 0 && parseInt(ui.element.attr('row')) <= 1) {
                //the tile is at the top
                return;
            }
            var virt_adj = new Set();
            for (var i = resizeStartX; i < resizeStartX + resizeStartSizeX; i++) {
                if (board[i - 1][resizeStartY - 2].tile != resizeId) {
                    virt_adj.add(board[i - 1][resizeStartY - 2].tile);
                }
            }
            //did it go up or down?
            $(ui.element).attr({
                'row': parseInt(ui.element.attr('row')) - diff,
                'sizey': parseInt(ui.element.attr('sizey')) + diff
            });
            update_board(resizeId);
            var moved = new Set();
            moved.add(resizeId);
            if (diff < 0) {
                //it moved down
                virt_adj.forEach(function(item) {
                    recursiveResize(moved, 'down', diff, 's', item);
                });
            } else if (diff > 0) {
                //it moved up
                virt_adj.forEach(function(item) {
                    recursiveResize(moved, 'up', diff, 's', item);
                });
            }
        }
        if (resizeDir == 's') {
            var diff = virtical_location(ui.originalPosition.top, ui.originalSize.height) - virtical_location(ui.helper.position().top, ui.helper.height());
            if (parseInt(ui.element.attr('row')) + parseInt(ui.element.attr('sizey')) - 1 == maxHeight) {
                //the tile is at the bottom
                return;
            }
            var virt_adj = new Set();
            for (var i = resizeStartX; i < resizeStartX + resizeStartSizeX; i++) {
                if (board[i - 1][resizeStartY + resizeStartSizeY - 1].tile != resizeId) {
                    virt_adj.add(board[i - 1][resizeStartY + resizeStartSizeY - 1].tile);
                }
            }
            //did it go up or down?
            $(ui.element).attr({
                'sizey': parseInt(ui.element.attr('sizey')) - diff
            });
            update_board(resizeId);
            var moved = new Set();
            moved.add(resizeId);
            if (diff < 0) {
                //it moved down
                virt_adj.forEach(function(item) {
                    recursiveResize(moved, 'down', diff, 'n', item);
                });
            } else if (diff > 0) {
                //it moved up
                virt_adj.forEach(function(item) {
                    recursiveResize(moved, 'up', diff, 'n', item);
                });
            }
        }
        if (resizeDir == 'e') {
            if (parseInt(ui.element.attr('col')) + parseInt(ui.element.attr('sizex')) - 1 == maxCols) {
                //the element is on the right of the board
                return;
            }
            var horz_adj = new Set();
            for (var i = resizeStartY; i < resizeStartY + resizeStartSizeY; i++) {
                if (board[resizeStartX + resizeStartSizeX - 1][i - 1].tile != resizeId) {
                    horz_adj.add(board[resizeStartX + resizeStartSizeX - 1][i - 1].tile);
                }
            }
            //did it go right or left?
            var diff = horizontal_location(ui.originalPosition.left, ui.originalSize.width) - horizontal_location(ui.helper.position().left, ui.helper.width());
            ui.element.attr({
                'sizex': parseInt(ui.element.attr('sizex')) - diff
            });
            update_board(resizeId);
            var moved = new Set();
            moved.add(resizeId);
            if (diff < 0) {
                //it moved right
                horz_adj.forEach(function(item) {
                    recursiveResize(moved, 'right', diff, 'w', item);
                });
            } else if (diff > 0) {
                //it moved left
                horz_adj.forEach(function(item) {
                    recursiveResize(moved, 'left', diff, 'w', item);
                });
            }
        }
        if (resizeDir == 'w') {
            if (parseInt(ui.element.attr('col')) == 1) {
                //the element is on the left side of the board
                return;
            }
            var horz_adj = new Set();
            for (var i = resizeStartY; i < resizeStartY + resizeStartSizeY; i++) {
                if (board[resizeStartX - 2][i - 1].tile != resizeId) {
                    horz_adj.add(board[resizeStartX - 2][i - 1].tile);
                }
            }
            //did it go right or left?
            var diff = horizontal_location(ui.originalPosition.left, 0) - horizontal_location(ui.helper.position().left, 0);
            ui.element.attr({
                'col': parseInt(ui.element.attr('col')) - diff,
                'sizex': parseInt(ui.element.attr('sizex')) + diff
            });
            update_board(resizeId);
            var moved = new Set();
            moved.add(resizeId);
            if (diff < 0) {
                //it moved right

                horz_adj.forEach(function(item) {
                    recursiveResize(moved, 'right', diff, 'e', item);
                });
            } else if (diff > 0) {
                //it moved left
                horz_adj.forEach(function(item) {
                    recursiveResize(moved, 'left', diff, 'e', item);
                });
            }
        }
    }

    function positionFixup() {
        for (var i = tiles.length - 1; i >= 0; i--) {
            var layout = returnBalanced(maxCols, maxHeight);
            var t = $('#' + tiles[i]);
            t.attr({
                'row': layout[tiles.length - 1][i].row(maxHeight),
                'col': layout[tiles.length - 1][i].col(maxCols),
                'sizex': layout[tiles.length - 1][i].sizex(maxCols),
                'sizey': layout[tiles.length - 1][i].sizey(maxHeight)
            });
            var tile_offset = offset_from_location(parseInt(t.attr('row')), parseInt(t.attr('col')));
            t.css({
                "top": tile_offset.top,
                "left": tile_offset.left,
                "width": t.attr('sizex') * tileWidth * widthScale,
                "height": t.attr('sizey') * tileHeight
            });

            console.log(tile_offset.top);
            console.log(tile_offset.left);
            console.log(t.attr('sizex') * tileWidth);
            console.log(t.attr('sizey') * tileHeight);
            update_board(tiles[i]);
        }
    }

    function update_board(id) {
        var t = $('#' + id);
        for (var k = parseInt(t.attr('col')) - 1; k < parseInt(t.attr('col')) + parseInt(t.attr('sizex')) - 1; k++) {
            for (var j = parseInt(t.attr('row')) - 1; j < parseInt(t.attr('row')) + parseInt(t.attr('sizey')) - 1; j++) {
                board[k][j].occupied = 1;
                board[k][j].tile = id;
            }
        }
    }

    function offset_from_location(row, col) {
        var offset = $('.tile-board').offset();
        offset.left += (col - 1) * tileWidth; //account for other tiles
        offset.top += (row - 1) * tileHeight;
        offset.left = ((offset.left - sidebarWidth) * widthScale) + sidebarWidth; //reduce widths to the portion of the screen not used by the sidebar
        return offset;
    }

    function dragFixup(col, row) {

        if (col < 0 || col > maxCols || row < 0 || row > maxHeight) {
            $('.ui-draggable-dragging').remove();
            return;
        }
        var targetId = board[col - 1][row - 1].tile;
        var thisTarget = $('#' + targetId);
        var targetX = parseInt(thisTarget.attr('col'));
        var targetY = parseInt(thisTarget.attr('row'));
        var targetSizeX = parseInt(thisTarget.attr('sizex'));
        var targetSizeY = parseInt(thisTarget.attr('sizey'));
        var targetGrid = thisTarget;
        var startGrid = $('#' + dragStartId);
        if (targetId == dragStartId) {
            var targetOffset = offset_from_location(row, col);
            $('#' + targetId).css({
                'top': dragStartOffset.top,
                'left': dragStartOffset.left,
                'height': dragStartSizeY * tileHeight,
                'width': dragStartSizeX * tileWidth
            });
        } else {
            var startOffset = offset_from_location(dragStartSizeY, dragStartSizeX);
            var targetOffset = offset_from_location(targetY, targetX);
            startGrid.attr({
                'col': targetGrid.attr('col'),
                'row': targetGrid.attr('row'),
                'sizex': targetGrid.attr('sizex'),
                'sizey': targetGrid.attr('sizey')
            });
            startGrid.css({
                'top': targetOffset.top,
                'left': targetOffset.left,
                'width': parseInt(startGrid.attr('sizex')) * tileWidth * widthScale,
                'height': parseInt(startGrid.attr('sizey')) * tileHeight
            });
            update_board(dragStartId);

            targetGrid.attr({
                'col': dragStartX,
                'row': dragStartY,
                'sizex': dragStartSizeX,
                'sizey': dragStartSizeY
            });
            targetGrid.css({
                'top': dragStartOffset.top,
                'left': dragStartOffset.left,
                'width': parseInt(targetGrid.attr('sizex')) * tileWidth * widthScale,
                'height': parseInt(targetGrid.attr('sizey')) * tileHeight
            });
            update_board(targetId);
        }
    }
    function grid_from_offset(pos) {
        var thisLocatiion = {
            col: Math.floor(pos.left / tileWidth) + 1,
            row: Math.floor(pos.top / tileHeight) + 1
        };
        return thisLocation;
    }

    function horizontal_location(x, sizex) {
        if (((x + sizex) / tileWidth) % 1 >= 0.5) {
            return Math.ceil((x + sizex) / tileWidth) + 1;
        } else {
            return Math.floor((x + sizex) / tileWidth) + 1;
        }
    }

    function virtical_location(y, sizey) {
        if (((y + sizey) / tileHeight) % 1 >= 0.5) {
            return Math.ceil((y + sizey) / tileHeight) + 1
        } else {
            return Math.floor((y + sizey) / tileHeight) + 1;
        }
    }

    var body = document.body;

    function layoutFix(layout) {

        layout.x = checkZero(Math.round(layout.x * maxCols));
        layout.y = checkZero(Math.round(layout.y * maxHeight));
        layout.sizex = checkZero(Math.round(layout.sizex * maxCols));
        layout.sizey = checkZero(Math.round(layout.sizey * maxHeight));
        var diff = layout.x + layout.sizex - 1 - maxCols;
        if (diff > 0) {
            layout.sizex -= diff;
        }
        diff = layout.y + layout.sizey - 1 - maxHeight;
        if (diff > 0) {
            layout.sizey -= diff;
        }
        return layout;
    }

    function loadLayout(layout, mode) {
        fadeOutMask();
        if (mode == 'day') {
            setDay();
        } else if (mode == 'night') {
            setNight();
        }
        mode.light = mode;

        for (var i = 0; i < layout.length; i++) {
            var name = layout[i].tileName;
            var new_tile = '<li id="' + name + '_window" class="tile">' + header1 + name + header2 + contents + header3 + '</li>';
            add_tile(new_tile, name + '_window', {
                x: layout[i].x - needsFixX(),
                y: layout[i].y - needsFixY(),
                sizex: layout[i].sizex,
                sizey: layout[i].sizey
            });
        }
    }

    function createMask(id, opacity) {
        var mask = document.createElement('div');
        $(mask).addClass('mask');
        $(mask).attr({
            'id': 'mask'
        });
        if (typeof opacity !== 'undefined') {
            $(mask).css({
                'opacity': opacity
            });
        }
        $(mask).click(function() {
            fadeOutMask(id);
        });
        $('body').append(mask);
        $(mask).fadeIn();
    }

    function fadeOutMask(id) {
        $('#' + id).remove();
        $('#mask').fadeOut('fast').queue(function() {
            $('#mask').remove();
        });
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function calcMaxSize() {
        docHeight = $(window).height() - $('.navbar').height() - 10;
        docHeight -= docHeight % 10;
        docWidth = $(window).width();
        docWidth -= docWidth % 10;
        var dimensionComponents = factor(docHeight).sort(function(a, b) {
            return a.factor - b.factor
        });
        for (var i = 0; i < dimensionComponents.length; i++) {
            if (dimensionComponents[i].multiplicator % 10 != 0) {
                dimensionComponents.splice(i, 1);
                i--;
            }
        }
        if (dimensionComponents.legnth == 0) {
            tileHeight = 50;
            maxHeight = Math.floor(docHeight) / 50;
        } else {
            dimensionComponents = dimensionComponents[Math.floor(dimensionComponents.length / 2)];
            tileHeight = dimensionComponents.factor;
            maxHeight = dimensionComponents.multiplicator;
        }

        dimensionComponents = factor(docWidth).sort(function(a, b) {
            return a.factor - b.factor
        });
        for (var i = 0; i < dimensionComponents.length; i++) {
            if (dimensionComponents[i].multiplicator % 10 != 0) {
                dimensionComponents.splice(i, 1);
                i--;
            }
        }
        if (dimensionComponents.length == 0) {
            tileWidth = 50;
            maxCols = Math.floor(docWidth / 50);
        } else {
            dimensionComponents = dimensionComponents[Math.floor(dimensionComponents.length / 2)];
            tileWidth = dimensionComponents.factor; //uhhhhh hopefully this is right
            maxCols = dimensionComponents.multiplicator;
        }
    }

    function handleWindowResize() {
        //iterate over all windows and adjust their size based on their proportion of the screen
        var oldMaxCols = maxCols,
            oldMaxHeight = maxHeight;
        calcMaxSize();
        boardSetup(maxCols, maxHeight);

        for (var i = 0; i < tiles.length; i++) {
            var curTile = $('#' + tiles[i]);
            var layout = layoutFix({
                tileName: tiles[i],
                x: parseInt(curTile.attr('col')),
                y: parseInt(curTile.attr('row')),
                sizex: parseInt(curTile.attr('sizex')),
                sizey: parseInt(curTile.attr('sizey'))
            });
            curTile.attr({
                'col': layout.y,
                'row': layout.x,
                'sizex': layout.sizex,
                'sizey': layout.sizey
            });
            curTile.css({
                'top': (layout.y - 1) * tileHeight + $('.tile-board').offset().top,
                'left': (layout.x - 1) * tileWidth + $('.tile-board').offset().left,
                'width': layout.sizex * tileWidth,
                'height': layout.sizey * tileHeight
            });
            update_board(tiles[i]);
        }
        $('.tile-board').height(maxHeight * tileHeight);
        $('.wrapper').height(maxHeight * tileHeight);
    }

    function checkZero(val) {
        if (val == 0)
            return 1;
        else
            return val
    }

    function boardSetup(cols, height) {
        //i = cols, j = rows
        board = new Array(cols + 1);
        //setup the empty board
        for (var i = board.length - 1; i >= 0; i--) {
            board[i] = new Array(height + 1);
            for (var j = board[i].length - 1; j >= 0; j--) {
                board[i][j] = {
                    occupied: 0,
                    tile: ''
                };
            }
        }
    }

    function factor(a) {
        var c, i = 2,
            j = Math.floor(a / 2),
            output = [];
        for (; i <= a; i++) {
            if (i == 1)
                return;
            c = a / i;
            if (c == 1)
                continue;
            if (c === Math.floor(c)) {
                var b = {
                    'factor': c,
                    'multiplicator': i
                };
                output.push(b);
            }
        }
        return output;
    }

    function needsFixX() {
        if (needsFixXBool) {
            return fixValX - 1;
        } else {
            return 0;
        }
    }

    function needsFixY() {
        if (needsFixYBool) {
            return fixValY - 1;
        } else {
            return 0;
        }
    }

    function get_csrf() {
        var nameEQ = "csrftoken=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    function get_data(url, type, jsonObj, success_callback, fail_callback) {
        var csrftoken = get_csrf();

        // var jsonObj = new Object;®
        // jsonObj.result = '';
        // jsonObj.data = '';
        var data = JSON.stringify(jsonObj);
        var csrf_ajax_obj = $.ajax({
            type: type,
            url: url,
            data: data,
            dataType: 'json',
            success: function(data) {
                jsonObj.result = 'success';
                jsonObj.data = data;
                success_callback(jsonObj.data);
            },
            headers: {
                "X-CSRFToken": csrftoken
            },
            error: function(request, status, error) {
                jsonObj.result = 'error';
                if (request.status == 200) {
                    success_callback(request);
                    return;
                }
                var errorObj = {};
                errorObj.request = request;
                errorObj.status = status;
                errorObj.error = error;
                jsonObj.data = JSON.stringify(errorObj);
                console.log(jsonObj);
                fail_callback(status);

            }
        });
        return ajax_obj;
    }

    function mtree(id) {
        if (typeof id === 'undefined') {
            id = 'tile-contents';
        }
        /*
           The following is copied from mtree.js
           */
        // mtree.js
        // Only apply if mtree list exists
        if ($('#' + id + ' ul.mtree').length) {
            // Settings
            var collapsed = true; // Start with collapsed menu (only level 1 items visible)
            var close_same_level = true; // Close elements on same level when opening new node.
            var duration = 400; // Animation duration should be tweaked according to easing.
            var listAnim = true; // Animate separate list items on open/close element (velocity.js only).
            var easing = 'easeOutQuart'; // Velocity.js only, defaults to 'swing' with jquery animation.

            if (mode == 'day') {
                var mtree_style = 'jet';
            } else {
                mtree_style = 'transit';
            }
            $('.mtree').addClass(mtree_style);

            // Set initial styles 
            $('#' + id + ' .mtree ul').css({
                'overflow': 'hidden',
                'height': (collapsed) ? 0 : 'auto',
                'display': (collapsed) ? 'none' : 'block'
            });

            // Get node elements, and add classes for styling
            var node = $('#' + id + ' .mtree li:has(ul)');
            node.each(function(index, val) {
                $(this).children(':first-child').css('cursor', 'pointer');
                $(this).addClass('mtree-node mtree-' + ((collapsed) ? 'closed' : 'open'));
                $(this).children('ul').addClass('mtree-level-' + ($(this).parentsUntil($('#' + id + ' ul.mtree'), 'ul').length + 1));
            });

            // Set mtree-active class on list items for last opened element
            $('#' + id + ' .mtree li > *:first-child').on('click.mtree-active', function(e) {
                if ($(this).parent().hasClass('mtree-closed')) {
                    $('.mtree-active').not($(this).parent()).removeClass('mtree-active');
                    $(this).parent().addClass('mtree-active');
                } else if ($(this).parent().hasClass('mtree-open')) {
                    $(this).parent().removeClass('mtree-active');
                } else {
                    $('.mtree-active').not($(this).parent()).removeClass('mtree-active');
                    $(this).parent().toggleClass('mtree-active');
                }
            });

            // Set node click elements, preferably <a> but node links can be <span> also
            node.children(':first-child').on('click.mtree', function(e) {

                // element vars
                var el = $(this).parent().children('ul').first();
                var isOpen = $(this).parent().hasClass('mtree-open');

                // close other elements on same level if opening 
                if ((close_same_level || $('.csl').hasClass('active')) && !isOpen) {
                    var close_items = $(this).closest('ul').children('.mtree-open').not($(this).parent()).children('ul');

                    // Velocity.js
                    if ($.Velocity) {
                        close_items.velocity({
                            height: 0
                        }, {
                                duration: duration,
                                easing: easing,
                                display: 'none',
                                delay: 100,
                                complete: function() {
                                    setNodeClass($(this).parent(), true)
                                }
                            });

                        // jQuery fallback
                    } else {
                        close_items.delay(100).slideToggle(duration, function() {
                            setNodeClass($(this).parent(), true);
                        });
                    }
                }

                // force auto height of element so actual height can be extracted
                el.css({
                    'height': 'auto'
                });

                // listAnim: animate child elements when opening
                if (!isOpen && $.Velocity && listAnim) el.find(' > li, li.mtree-open > ul > li').css({
                    'opacity': 0
                }).velocity('stop').velocity('list');

                // Velocity.js animate element
                if ($.Velocity) {
                    el.velocity('stop').velocity({
                        //translateZ: 0, // optional hardware-acceleration is automatic on mobile
                        height: isOpen ? [0, el.outerHeight()] : [el.outerHeight(), 0]
                    }, {
                            queue: false,
                            duration: duration,
                            easing: easing,
                            display: isOpen ? 'none' : 'block',
                            begin: setNodeClass($(this).parent(), isOpen),
                            complete: function() {
                                if (!isOpen) $(this).css('height', 'auto');
                            }
                        });

                    // jQuery fallback animate element
                } else {
                    setNodeClass($(this).parent(), isOpen);
                    el.slideToggle(duration);
                }

                // We can't have nodes as links unfortunately
                e.preventDefault();
            });

            // Function for updating node class
            function setNodeClass(el, isOpen) {
                if (isOpen) {
                    el.removeClass('mtree-open').addClass('mtree-closed');
                } else {
                    el.removeClass('mtree-closed').addClass('mtree-open');
                }
            }

            // List animation sequence
            if ($.Velocity && listAnim) {
                $.Velocity.Sequences.list = function(element, options, index, size) {
                    $.Velocity.animate(element, {
                        opacity: [1, 0],
                        translateY: [0, -(index + 1)]
                    }, {
                            delay: index * (duration / size / 2),
                            duration: duration,
                            easing: easing
                        });
                };
            }

            if ($('#' + id + ' .mtree').css('opacity') == 0) {
                if ($.Velocity) {
                    $('.mtree').css('opacity', 1).children().css('opacity', 0).velocity('list');
                } else {
                    $('.mtree').show(200);
                }
            }
        }

    }
});
