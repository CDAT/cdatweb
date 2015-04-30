$('body').ready(function(){
    
    var gridster;
    var maxCols = 6;
    var maxHeight = 4;
    var resize_handle_html = '<span class="gs-resize-handle gs-resize-handle-both"></span>';

    // Define a widget
    var header1 = ''; 
    var header2 = '';
    var header3 = '';
    var contents = '';
    header1 += '<div class="grid-panel panel-default">';
    header1 += ' <div class="grid-panel-heading">';
    header1 += '  <div class="panel-header-title text-center">';
    header1 += '    <button type="button" class="btn btn-default btn-xs options" style="float:left;">';
    header1 += '     <span class="fa fa-cog" aria-label="Options"></span>';
    header1 += '    </button>';
    header1 += '    <button type="button" class="btn btn-default btn-xs remove"  style="float:right;">';
    header1 += '     <span class="fa fa-times" aria-label="Close"></span>';
    header1 += '    </button>';
    header1 += '     <p style="text-align: center">';
    // Widget Name
    header2 += '     <p>';
    header2 += '   </div>';
    header2 += '  </div>';
    header2 += ' </div>';
    header2 += ' <div class="panel-body">';
    header2 += '  <div class="box">&nbsp</div><br>';
    // Widget Contents
    contents += '  The path of the righteous man is beset on all sides by the iniquities of the selfish and the tyranny of evil men.';
    header3 += ' </div>';
    header3 += '</div>';




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



  gridster = $(".gridster ul").gridster({
      widget_margins: [widgetMargins, widgetMargins],
      widget_base_dimensions: [140, 140],
      max_cols: maxCols,
      min_cols: maxCols,
      resize: {
        enabled: true,
        stop: function(e, ui, widget) {
          resizeFixup(e, ui, widget[0].id);
        },
        start: function(e, ui, widget) {
          resizeStartX = parseInt($('#'+widget[0].id).attr('data-col'));
          resizeStartY = parseInt($('#'+widget[0].id).attr('data-row'));
          resizeStartSizeX = parseInt($('#'+widget[0].id).attr('data-sizex'));
          resizeStartSizeY = parseInt($('#'+widget[0].id).attr('data-sizey'));
        }
      },
      draggable: {
        distance: 0,
        limit: true,
        start: function(e, ui, id) {
          dragStartId = id[0].id;
          var grid = $('#' + dragStartId);
          var offset = grid.offset();
          dragStartX = grid.attr('data-col');
          dragStartY = grid.attr('data-row');
          dragStartSizeX = grid.attr('data-sizex');
          dragStartSizeY = grid.attr('data-sizey');
          dragStartOffset.top = Math.floor(offset.top);
          dragStartOffset.left = Math.floor(offset.left)+1;
          //console.log('drag starting at left:' + dragStartOffset.left + ' top:' + dragStartOffset.top);
        },
        stop: function(e, ui, col, row) {
          dragFixup(e, ui, col, row);
        },
        drag: function(e, ui, id) {
          //dragFixup(e, ui, id);
        }
      },
  }).data('gridster');

  gridster.set_dom_grid_height(640);
  //gridster.set_dom_grid_width(2*widgetMargins*maxCols);


  $('#provenance').click(function(){
      add_grid('provenance');
    });
  $('#status').click(function(){
      add_grid('status');
    });
  $('#science').click(function(){
      add_grid('science');
    });
  $('#nodeList').click(function(){
      add_grid('nodeList');
    });
  $('#heatMap').click(function(){
      add_grid('heatMap');
    });
  $('#modelRun').click(function(){
      add_grid('modelRun');
    });
  $('#nodeSelect').click(function(){
      add_grid('nodeSelect');
    });
  $('#cdat').click(function(){
      add_grid('cdat');
    });
  $('#charting').click(function(){
      add_grid('charting');
    });

  /**
   * Registers call backs for window creation buttons
   */
  function add_grid(name){
    if($('#' + name + '_window').length == 0) {
      var widget_t = ['<li id=' + name + '_window>' + header1 +''+ name +''+ header2 +''+ contents +''+ header3 +'</li>',1,1];
      var w = gridster.add_widget.apply(gridster,widget_t);
      $(w).find('.panel-body').mousedown(function (event) {
        event.stopPropagation();
      });
      $(w).find('.remove').click(function(e) {
        //send the widget that got clicked to the remove handler
        removeFixup(e.target.parentElement.parentElement.parentElement.parentElement);
      });
      $(w).find('.options').click(function(e) {
        widgetOptions(e.target.parentElement.parentElement.parentElement.parentElement);
      });
      new_window_fixup({id: name + '_window'});
    }
  }
  
 
  /**
   * Fixes the widget sizes after a remove event
   * widget -> the widget being removed
   */
  function removeFixup(widget){
    var x = parseInt($(widget).attr('data-col'));
    var y = parseInt($(widget).attr('data-row'));
    var sizex = parseInt($(widget).attr('data-sizex'));
    var sizey = parseInt($(widget).attr('data-sizey'));

    //push the closing window to the back of the canvas
    $(widget).css('z-index', 1);

    var adj = findAdj(x, y, sizex, sizey, $(widget).attr('id'));
    
    //remove the window in question
    gridster.remove_widget($(widget), true);

    //resize the adj windows
    resizeAdj(x, y, sizex, sizey, adj);
  }

  /**
   * Resises the appropriate adjacent windows to the window that is closing
   * x, y, sizex, sizey, the col row sizex and sizey of the window being closed
   * adj, an array of all windows adjacent to the window being closed
   */
  function resizeAdj(x , y, sizex, sizey, adj) {
    //decide what to do with the other windows to fill in the space
    for (var i = adj.length - 1; i >= 0; i--) {
      var adjx = parseInt(adj[i].attr('data-col'));
      var adjy = parseInt(adj[i].attr('data-row'));
      var adjSizeX = parseInt(adj[i].attr('data-sizex'));
      var adjSizeY = parseInt(adj[i].attr('data-sizey'));
      if(adjx == x) {
        if(adjy > y) {
          //see if we can expand the adj window into the place of 
          //the removed window without hitting any other windows
          if(adjSizeX == sizex) {
            //the simple case
            gridster.mutate_widget_in_gridmap(
              adj[i],
              {
                col: adjx,
                row: adjy,
                size_x: adjSizeX,
                size_y: adjSizeY
              },{
                col: adjx,
                row: adjy - sizey,
                size_x: adjSizeX,
                size_y: adjSizeY + sizey
              }
            );
            return;
          } else {
            //the move complex case
          }
        } else {
          if(adjSizeX == sizex) {
            //the simple case
            gridster.mutate_widget_in_gridmap(
              adj[i],
              {
                col: adjx,
                row: adjy,
                size_x: adjSizeX,
                size_y: adjSizeY
              },{
                col: adjx,
                row: adjy,
                size_x: adjSizeX,
                size_y: adjSizeY + sizey
              }
            );
            return;
          } else {

          }
        }
      }
      else if(adjy == y) {
        if(adjx > x) {
          if(adjSizeY == sizey){
            //simple case
            gridster.mutate_widget_in_gridmap(
              adj[i],
              {
                col: adjx,
                row: adjy,
                size_x: adjSizeX,
                size_y: adjSizeY
              },{
                col: adjx - sizex,
                row: adjy,
                size_x: adjSizeX + sizex,
                size_y: adjSizeY
              }
            );
            return;
          } else {

          }
        } else {
          if(adjSizeY == sizey){
            //simple case
            gridster.mutate_widget_in_gridmap(
              adj[i],
              {
                col: adjx,
                row: adjy,
                size_x: adjSizeX,
                size_y: adjSizeY
              },{
                col: adjx,
                row: adjy,
                size_x: adjSizeX + sizex,
                size_y: adjSizeY
              }
            );
            return;
          } else {
            
          }
        }
      } 
    };
  }


  /**
   * Finds all windows adjacent to the window specified
   * x, y, sizex, sizey are the col, row, sizex and sizey of the given window
   * id, the id of the window being closed
   */
  function findAdj(x, y, sizex, sizey, id){
    var windows = $('.gs-w');
    var adj = [];
    //find the adjacent windows
    for (var i = windows.length - 1; i >= 0; i--) {
      if($(windows[i]).attr('id') == id)
        continue;
      var wx = parseInt($(windows[i]).attr('data-col'));
      var wy = parseInt($(windows[i]).attr('data-row'));
      var wsizex = parseInt($(windows[i]).attr('data-sizex'));
      var wsizey = parseInt($(windows[i]).attr('data-sizey'));
      if((x == wx) || ((x < wx) && (x + sizex - 1 >= wx)) || ((x > wx) && (x <= wx + wsizex - 1))) {
        if(wy + wsizey == y || y + sizey == wy) {
          adj.push($(windows[i]));
        }
      }
      if((y == wy) || ((y < wy) && (y + sizey - 1 >= wy)) || ((y > wy)  && (y <= wy + wsizey - 1))) {
        if(wx + wsizex == x || x + sizex == wx) {
          adj.push($(windows[i]));
        }
      }
    };
    return adj;
  }

  /**
   * Brings up the options for the widget
   * widget -> the widget requesting its options
   */
  function widgetOptions(id){

  }




  //this only works when going up and to the left
  //  TODO: add the sizex and sizey so it works going down and to the right
  function idFromLocation(col, row, sizex, sizey) {
    var windows = $('.gs-w');
    var id;
    for (var i = windows.length - 1; i >= 0; i--) {
      if(parseInt($(windows[i]).attr('data-row')) <= row && row <= ( parseInt($(windows[i]).attr('data-row'))+parseInt($(windows[i]).attr('data-sizey'))-1) )  
      {
        if(parseInt($(windows[i]).attr('data-col')) <= col && col <= (parseInt($(windows[i]).attr('data-col'))+parseInt($(windows[i]).attr('data-sizex'))-1) ) 
        {
          id = $(windows[i]).attr('id');
          return id;
        }
      }
      
    };
  }


  

  /**
  * Computes and sets the size for each window
  */
  function resizeFixup(e, ui, id) {
    var i = 0;
    var windows = $(".gs-w");
    for(; i < windows.length; i++) {
      // var j = 0;
      // var rowsCols = get_windows({
      //   id: $(windows[i]).attr('id'),
      //   x: parseInt($(windows[i]).attr('data-col')),
      //   y: parseInt($(windows[i]).attr('data-row')),
      // });
      // var nodes = get_rows_cols({
      //   id: $(windows[i]).attr('id'),
      //   x: parseInt($(windows[i]).attr('data-col')),
      //   y: parseInt($(windows[i]).attr('data-row')),
      //   sizex: parseInt($(windows[i]).attr('data-sizex')),
      //   sizey: parseInt($(windows[i]).attr('data-sizey')),
      // });
    }
  }

  /**
   * Fixes the window positions after a drag event
   * col, row -> the ending col and row of the dragged element
   */
  function dragFixup(e, ui, col, row) {
    
    var targetId = idFromLocation(col, row);
    var targetX = parseInt($('#'+targetId).attr('data-col'));
    var targetY = parseInt($('#'+targetId).attr('data-row'));
    var targetSizeX = parseInt($('#'+targetId).attr('data-sizex'));
    var targetSizeY = parseInt($('#'+targetId).attr('data-sizey'));
    var targetGrid = $('#'+targetId);
    var startGrid = $('#'+dragStartId);
    if(targetId == dragStartId) {
      gridster.mutate_widget_in_gridmap(
        targetGrid,
        {
          col: 1,//parseInt(targetGrid.attr('data-col')),
          row: 1,//parseInt(targetGrid.attr('data-row')),
          size_x: 1,//parseInt(targetGrid.attr('data-sizex')),
          size_y: 1,//parseInt(targetGrid.attr('data-sizey')),
        },
        {
          col: dragStartX,
          row: dragStartY,
          size_x: dragStartSizeX,
          size_y: dragStartSizeY,
        });
      var targetOffset = targetGrid.offset();
      startGrid.offset({
        top: dragStartOffset.top,
        left: dragStartOffset.left - 1// - Math.floor(widgeMargins/2)-2)
      });
    } else {
      var startOffset = startGrid.offset();
      var targetOffset = targetGrid.offset();
      gridster.mutate_widget_in_gridmap(
        startGrid,
        {
          col: startGrid.attr('data-col'),
          row: startGrid.attr('data-row'),
          size_x: startGrid.attr('data-sizex'),
          size_y: startGrid.attr('data-sizey'),
        },
        {
          col: targetGrid.attr('data-col'),
          row: targetGrid.attr('data-row'),
          size_x: targetGrid.attr('data-sizex'),
          size_y: targetGrid.attr('data-sizey'),
        });
      gridster.mutate_widget_in_gridmap(
        targetGrid,
        {
          col: targetGrid.attr('data-col'),
          row: targetGrid.attr('data-row'),
          size_x: targetGrid.attr('data-sizex'),
          size_y: targetGrid.attr('data-sizey'),
        },
        {
          col: dragStartX,
          row: dragStartY,
          size_x: dragStartSizeX,
          size_y: dragStartSizeY,
        });
      startGrid.offset({
        top: targetOffset.top,
        left: targetOffset.left
      });
      targetGrid.offset({
        top: dragStartOffset.top,
        left: dragStartOffset.left - 1 // - Math.floor(widgeMargins/2)-2
      }); 
    }
  }

  /**
   * Recomputes and then places each window in its correct position
   * widget -> x, y, id
   */
  function new_window_fixup(widget) {
    var windows = $('.gs-w');
    if (windows.length == 1) {
      gridster.mutate_widget_in_gridmap(
        $(windows[0]),
        {
          col: 1,
          row: 1,
          size_x: 1,
          size_y: 1
        },
        {
          col: 1,
          row: 1,
          size_x: maxCols,
          size_y: maxHeight
        });
    } else {

      //find the largest widget
      var largetsWidget = 0;
      var largetsWidgetIndex = 0;
      for (var i = windows.length - 1; i >= 0; i--) {
        var currentWidget = parseInt($(windows[i]).attr('data-sizex')) * parseInt($(windows[i]).attr('data-sizey'));
        if( currentWidget > largetsWidget ) {
          largetsWidget = currentWidget;
          largetsWidgetIndex = i;
        }
      }
      //Now find the largest widgets major axis, cut it in half and place the new widget in the space
        //If the largest window found is taller then it is wide
      if(parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) >= parseInt($(windows[largetsWidgetIndex]).attr('data-sizex'))  ) {
        var newHeight = parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) / 2;
        if(Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) / 2) != parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) / 2) {
          newHeight = Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) / 2) + 1;
        }
        var largetsWidgetRow = parseInt($(windows[largetsWidgetIndex]).attr('data-row'));
        gridster.mutate_widget_in_gridmap(
          $(windows[largetsWidgetIndex]),
          {
            col: parseInt($(windows[largetsWidgetIndex]).attr('data-col')),
            row: parseInt($(windows[largetsWidgetIndex]).attr('data-row')),
            size_x: parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')),
            size_y: parseInt($(windows[largetsWidgetIndex]).attr('data-sizey'))
          },
          {
            col: parseInt($(windows[largetsWidgetIndex]).attr('data-col')),
            row: parseInt($(windows[largetsWidgetIndex]).attr('data-row')),
            size_x: parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')),
            size_y: Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')) / 2)
          });
        gridster.mutate_widget_in_gridmap(
          $('#' + widget.id),
          {
            col: parseInt($('#' + widget.id).attr('data-col')),
            row: parseInt($('#' + widget.id).attr('data-row')),
            size_x: parseInt($('#' + widget.id).attr('data-sizex')),
            size_y: parseInt($('#' + widget.id).attr('data-sizey'))
          },
          {
            col: parseInt($(windows[largetsWidgetIndex]).attr('data-col')),
            row: largetsWidgetRow + parseInt($(windows[largetsWidgetIndex]).attr('data-sizey')),
            size_x: parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')),
            size_y: newHeight
          });
      } else { //If the largest window found is wider then it is tall
        var newWidth = parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')) / 2;
        if(Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')) / 2) != parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')) / 2) {
          newWidth = Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')) / 2) + 1;
        }
        gridster.mutate_widget_in_gridmap(
          $(windows[largetsWidgetIndex]),
          {
            col: parseInt($(windows[largetsWidgetIndex]).attr('data-col')),
            row: parseInt($(windows[largetsWidgetIndex]).attr('data-row')),
            size_x: parseInt($(windows[largetsWidgetIndex]).attr('data-sizex')),
            size_y: parseInt($(windows[largetsWidgetIndex]).attr('data-sizey'))
          },
          {
            col: parseInt($(windows[largetsWidgetIndex]).attr('data-col')),
            row: parseInt($(windows[largetsWidgetIndex]).attr('data-row')),
            size_x: Math.floor(parseInt($(windows[largetsWidgetIndex]).attr('data-sizex'))/2),
            size_y: parseInt($(windows[largetsWidgetIndex]).attr('data-sizey'))
          });

        gridster.mutate_widget_in_gridmap(
          $('#' + widget.id),
          {
            col: parseInt($('#' + widget.id).attr('data-col')),
            row: parseInt($('#' + widget.id).attr('data-row')),
            size_x: parseInt($('#' + widget.id).attr('data-sizex')),
            size_y: parseInt($('#' + widget.id).attr('data-sizey'))
          },
          {
            col: (parseInt($(windows[largetsWidgetIndex]).attr('data-col')) + parseInt($(windows[largetsWidgetIndex]).attr('data-sizex'))),
            row: parseInt($(windows[largetsWidgetIndex]).attr('data-row')),
            size_x: newWidth,
            size_y: parseInt($(windows[largetsWidgetIndex]).attr('data-sizey'))
          });
        console.log('moving ' + widget.id + ' to x:' + (parseInt($(windows[largetsWidgetIndex]).attr('data-col')) + parseInt($(windows[largetsWidgetIndex]).attr('data-sizex'))) + ' y:' + parseInt($(windows[largetsWidgetIndex]).attr('data-row')));
        
      }    
    }
    gridster.set_dom_grid_height();
    gridster.set_dom_grid_width();
  }

  /**
   * returns the number unique windows to the left, right, above, and below the given widget
   * widget -> x, y, id
   */
  function get_windows(widget) {
    var nodesInCol = 1;
    var nodesInRow = 1;
    var windows = $('.gs-w');
    for(var j = 0; j < windows.length; j++) { 
      if (widget.id != $(windows[j]).attr('id')) {
        if( widget.y == parseInt($(windows[j]).attr('data-row')) 
            || ( parseInt($(windows[j]).attr('data-row')) <= widget.y 
                && widget.y <= ( parseInt($(windows[j]).attr('data-row'))+parseInt($(windows[j]).attr('data-sizey'))-1) ) ) 
        {
          //console.log($(windows[i]).attr('id') + " is in the same row as " + $(windows[j]).attr('id'));
          nodesInRow++;
        }
        if(widget.x == parseInt($(windows[j]).attr('data-col'))
            || ( parseInt($(windows[j]).attr('data-col')) <= widget.x 
                && widget.x <= (parseInt($(windows[j]).attr('data-col'))+parseInt($(windows[j]).attr('data-sizex'))-1) ) )
        {
          //console.log($(windows[i]).attr('id') + " is in the same col as " + $(windows[j]).attr('id'));
          nodesInCol++;
        }
      }
    }
    var newHTML = '<div><p>' + widget.id + '</p><p>nodesInRow:' + nodesInRow + '</p><p>nodesInCol:' + nodesInCol + '</p></div>';
    $('#'+widget.id).html(newHTML);
    return {
      row: nodesInRow,
      col: nodesInCol
    };
  }


  /**
   * returns the number of widgets to the left, right, above, and below the requested widget
   * left = left of *any* of the widget of interest cells
   * widget -> x, y, sizex, sizey

   * TODO: Make sure it scans to the left no only from the origin of the node, but to the left
          of each grid it extends down, and like wise for right, down, up
   */
  function get_rows_cols(widget) {
    var nodes = {
      left: 0,
      right: 0,
      up: 0, //above the widget on the page, lower row number
      down: 0 //below the widget on the page, higher row number
    };
    var windows = $('.gs-w');
    var highestRow = 1;
    for( var i = 0; i < windows.length; i++) {
      if(parseInt($(windows[i]).attr('data-row')) + parseInt($(windows[i]).attr('data-sizey')) > highestRow ) {
        highestRow = parseInt($(windows[i]).attr('data-row')) + parseInt($(windows[i]).attr('data-sizey'));
      }
    }
    for( var j = 1; j < widget.x; j++) { //scan to the left of the widget.x position
      if( gridster.is_widget(j, widget.y)) {
        nodes.left++;
      }
    }
    for(j = widget.x + widget.sizex; j <= maxCols; j++) {
      if( gridster.is_widget(j, widget.y)) {
        nodes.right++;
      }
    }
    for(j = widget.y-1 ; j > 0; j--) {
      if( gridster.is_widget(widget.x, j)) {
        nodes.up++;
      }
    }
    for(j = widget.y + widget.sizey; j < highestRow; j++) {
      if( gridster.is_widget(widget.x, j)) {
        nodes.down++;
      }
    }
    var newHTML = $('#'+widget.id).html() + '<p>Up:' + nodes.up + '</p><p>Right:' + nodes.right + '</p><p>Down:' + nodes.down + '</p><p>Left:' + nodes.left + '</p>' + resize_handle_html;
    $('#'+widget.id).html(newHTML);
    return nodes;
  }

});


