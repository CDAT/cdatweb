$("body").ready(function() {
	/*FIX THIS*/
	panelArray = []; //access to each panel element
	rowArray = []; //the number of cols in each row, with the index as the row and the value as the amount of cols in that row
	/*DO NOT RELEASE*/
	var gridSize = 12 * 4; //12 * X
	var panelId = 0;
	var dragPositionStartCol = 0;
	var dragPositionStartRow = 0;
	var dragStartWidth = 0;
	var dragStartHeight = 0;
	var dragPositionStopCol = 0;
	var dragPositionStopRow = 0;
	var dragStarted = 0;

	Array.prototype.randomElement = function () {
	    return this[Math.floor(Math.random() * this.length)]
	}

	var sourceArray = ['http://uvcdat.llnl.gov/display.php?file=vcs3D_wnd_vector',
						'http://uvcdat.llnl.gov/display.php?file=vcs3D_uwnd_volume',
						'http://uvcdat.llnl.gov/display.php?file=test_vcs_patterns',
						'http://uvcdat.llnl.gov/display.php?file=test_vcs_basic_yxvsx_masked',
						'http://uvcdat.llnl.gov/display.php?file=test_vcs_basic_vector_zero'];
	
	var pixPerGrid = $('#o-draggable').width() / gridSize;

	var config = {
		id: function() {
			return 'Panel_' + panelId++;
		},
		title: function() {
			return 'Panel_' + ($('.jsPanel').length);
		}, 
		show: 'fadeIn',
		//theme: 'black',
		bootstrap: 'primary',
		position: 'center',
		draggable: {
			containment: '#o-draggable'
		},
		selector: '#o-draggable',
		size: {
			width: $('#o-draggable').width(),
			height: $('#o-draggable').height() - 30,
		},
		iframe: {
			id: 'myFrame',
			src: sourceArray[Math.floor(Math.random()*sourceArray.length)],
			style: { border: "10px solid transparent"},
			width: '100%',
			height: '100%'
		},
		/*callback: function () {
	        document.getElementById("myFrame").onload = function(){
	            $("#myFrame").fadeIn(2000);
	        }
	    }*/
	};

	
	$('#spawn').click(function() {	
		if (rowArray.length == gridSize) {
				return;
		}
		var newConfig = new Object(config);
		//newConfig.iframe.id = newConfig.iframe.id + '1';
		newConfig.iframe.src = 'http://gojs.net/latest/samples/fdLayout.html';
		newConfig.size = {
			width: $('#o-draggable').width(),
			height: $('#o-draggable').height() - 30,
		};
		var panel = $.jsPanel(newConfig);
		
		panel.data('pos', {row: 0, col: 0});
		panel.data('width', 0);
		panel.data('height', 0);
		//panel.content.append('<div class="tiles red"><span class="tile-title">front</span></div><div><p>back side</p><span class="tile-title>back title></span></div>');
		panelArray.push(panel);
		addPanel(panel);

	});

	function dragStartPosition(panel, event) {
		dragStarted = 1;
		dragPositionStartCol = panel.data('pos').col;
		dragPositionStartRow = panel.data('pos').row;
		dragStartWidth = panel.width();
		dragStartHeight = panel.height();
		console.log('start col ' + dragPositionStartCol);
		console.log('start row ' + dragPositionStartRow);
		panel.animate({
			width: '20%',
			height: '20%',
		}, 500);
		//panel.width(200);
		//panel.height(200);
		//panel.transition({perspective: 500, rotateY: '180deg'}, 500, 'linear');
		//panel.css({transformOrigin:'5px 5px'}).transition({scale:0.5});
		//panel.transition({
		//	y: Math.abs(event.pageY - panel.offset().top)-15,
		//	x: Math.abs(event.pageX - panel.offset().left)-30
		//});

/*
		panel.offset({
			top: event.pageY-15,
			left: event.pageX-30
		});
*/

	}

	function dragPositionFixup(panel, event) {
		var i = 0;
		var switchup = 0;
		//panel.css({transformOrigin:'5px 5px'}).transition({scale:1})
		console.log('drag end offset.left ' + panel.offset().left);
		console.log('drag end offset.top ' + panel.offset().top);
		console.log('drag end position x:' + event.pageX + ' y:' +event.pageY);
		
		for (i = 0; i < panelArray.length; i++) {
			if(panel.attr('id') == panelArray[i].attr('id')) {
				continue;
			}
			//if mouse is to the left of the panels right side, and to the right of the panels left side
			if ( (event.pageX < (panelArray[i].offset().left + panelArray[i].width())) && (event.pageX > panelArray[i].offset().left) ) {
				//if the mouse is above the bottom and below the top
				if( (event.pageY < (panelArray[i].offset().top + panelArray[i].height())) && (event.pageY > panelArray[i].offset().top) ) {
					//switch the two panels position
					switchup = 1;
					console.log('switching with panel:' + i + 1);
					/*panel.transition({
						y: Math.abs(panel.offset().top - panelArray[i].offset().top),
						x: Math.abs(panel.offset().left - panelArray[i].offset().left)
					});*/
					panel.offset({
						top: panelArray[i].offset().top,
						left: panelArray[i].offset().left
					});
					panel.width(panelArray[i].width());
					panel.height(panelArray[i].height());
					panel.data('pos', {
						row: panelArray[i].data('pos').row,
						col: panelArray[i].data('pos').col
					});
					panelArray[i].data('pos', {
						row: dragPositionStartRow,
						col: dragPositionStartCol
					});
					panelArray[i].width(dragStartWidth);
					panelArray[i].height(dragStartHeight);
					panelArray[i].offset({
						top: panel.parent().offset().top + dragPositionStartRow * dragStartHeight,
						left: panel.parent().offset().left + dragPositionStartCol  * dragStartWidth
					});
					break;
				}
			}
		}
		if (switchup == 0) {
			console.log('not switching');
			panel.offset({
				top: panel.parent().offset().top + dragPositionStartRow * dragStartHeight,
				left: panel.parent().offset().left + dragPositionStartCol  * dragStartWidth
			});
			panel.width(dragStartWidth);
			panel.height(dragStartHeight);
		}
		dragStarted = 0;
	}

	function dragPositionCheck(panel, event) {
		/*
		if(dragStarted && (event.pageX < (panel.parent().offset().left + 1) || 
			event.pageX > (panel.parent().offset().left + panel.parent().width() - 1) ||
			event.pageY < (panel.parent().offset().top + 1) ||
			event.pageY > (panel.parent().offset().top + panel.parent().height() - 1))) {
			console.log('invalid more outside the box');
			panel.offset({
				top: panel.parent().offset().top + dragPositionStartRow * dragStartHeight,
				left: panel.parent().offset().left + dragPositionStartCol  * dragStartWidth
			});
			panel.width(dragStartWidth);
			panel.height(dragStartHeight);
		}
		panel.title('x:'+ event.pageX + ' y:'+event.pageY);
		*/
	}

	function addPanel(curPanel) {
		
		var i = 0;
		curPanel.find('.jsPanel-btn-close').mousedown(function() {
			panelArray.splice(panelArray.indexOf(curPanel), 1);
			removePanel(curPanel);
		});
		curPanel.find('.panel-title').mousedown(function(event) {
			dragStartPosition(curPanel, event);
		});
		curPanel.find('.panel-title').mouseup(function(event) {
			dragPositionFixup(curPanel, event);
		});

		//curPanel.find('.panel-title').mousemove(function(event) {
		//	dragPositionCheck(curPanel, event);
		//});
		/*
		curPanel.find('.live-tile').dblclick(function() {
			$(this).liveTile({
				repeatCount: 0,
				delay: 0,
				startNow: true,
			});
		});
*/


		if (panelArray.length == 1) {
			rowArray.push(1);
			panelArray[0].data('pos', {
				row: 0,
				col: 0
			});
			panelArray[0].data('width', gridSize);
			panelArray[0].data('height', gridSize);
		} else {
			//check to see if we need to create a new row
			var maxCol = 1;
			for (i = 0; i < rowArray.length; i++) {
				if (rowArray[i] > maxCol) {
					maxCol = rowArray[i];
				}
			}
			if (maxCol > rowArray.length) {
				//new row is needed

				rowArray.push(0); //add the new row size to the rowArray

			}

			var smallestRow = rowArray[0];//index of the smallest row
			var smallestSize = gridSize+1; //value of the smallest row
			for (i = rowArray.length - 1; i >= 0; i--) { //find the index and length of the smallest row
				if (rowArray[i] <= smallestSize) {
					smallestRow = i;
					smallestSize = rowArray[i];
				}
			}
			console.log("smallestRow " + smallestRow);
			console.log("smallestSize " + smallestSize);
			
			curPanel.data('pos', { //create 
				row: smallestRow,
				col: smallestSize,
			});
			rowArray[smallestRow] ++;
			
			var leftover = gridSize - (Math.floor(gridSize / rowArray[smallestRow]) * rowArray[smallestRow]); 
			for (i = 0; i < panelArray.length; i++) {
				if (panelArray[i].data('pos').row == smallestRow) {
					panelArray[i].data('width', Math.floor(gridSize / rowArray[smallestRow]));
					panelArray[i].data('height', Math.floor(gridSize / rowArray.length));
					if (leftover > 0) {
						panelArray[i].data('width', panelArray[i].data('width') + 1);
						leftover--;
					}
				}
				panelArray[i].width((panelArray[i].data('width') * pixPerGrid));
				panelArray[i].height(curPanel.parent().height() / (rowArray.length));
				
			
				if (panelArray[i].data('pos').col != 0) {
					for(var j = 0; j < panelArray.length; j++) {
						if ((panelArray[j].data('pos').row == panelArray[i].data('pos').row) && (panelArray[j].data('pos').col == (panelArray[i].data('pos').col -1 ) )) {
							var offset = panelArray[j].offset();
							break;
						}
					}
					panelArray[i].offset({
						left: offset.left+panelArray[i].width(), 
						top: panelArray[i].parent().offset().top + (panelArray[i].data('pos').row * panelArray[i].height() ) });
				} else if (panelArray[i].data('pos').col == 0 && panelArray[i].data('pos').row != 0) {
					panelArray[i].offset({
						top: panelArray[i].parent().offset().top + (panelArray[i].data('pos').row * panelArray[i].height() ) });
				}
			}
			for (i = 0; i < rowArray.length; i++) {
				if (rowArray[i] % 2 != 0 && rowArray[i] % 3 != 0 && rowArray[i] != 1) {
					for (j = 0; j < panelArray.length; j++) {
						if (panelArray[j].data('pos').row == i && (panelArray[j].data('pos').col+1) == rowArray[i]) {
							panelArray[j].width(panelArray[j].width() + pixPerGrid);
							break;;
						}
					}
				}
			}
			
		}
	}

	function removePanel(panel) {
		var i = 0;
		if( rowArray[panel.data('pos').row] == 1 ) { //check if its the only element in the row
			console.log("removing row " + panel.data('pos').row);
			rowArray.splice(panel.data('pos').row, 1);
			if (panelArray.length == 0) {
				return;
			} else {
				for (i = 0; i < panelArray.length; i++) {
					panelArray[i].height(panel.parent().height() / (rowArray.length));
					if(panel.data('pos').row < panelArray[i].data('pos').row) { //removed the row above (in the layout, actualy less in the row number)
						panelArray[i].data('pos').row = panelArray[i].data('pos').row - 1;
						panelArray[i].offset({top: panelArray[i].parent().offset().top + (panelArray[i].data('pos').row) * (panelArray[i].parent().height() / rowArray.length)})
					} else { //removed the row below (in the layout, above in the row number)
						if (panelArray[i].data('pos').row != 0) {
							var oneUpRowOffset = 0;
							for(var j = 0; j < panelArray.length; j++) {
								if (panelArray[j].data('pos').row == panelArray[i].data('pos').row-1) {
									oneUpRowOffset = panelArray[j].offset();
									break;
								}
							}
							panelArray[i].offset({
								top: oneUpRowOffset.top + (panel.parent().height() / (rowArray.length))
							});
						}
					}
				}
			}
		} else {
			console.log("removing col " + panel.data('pos').col + " from row " + panel.data('pos').row);
			rowArray[panel.data('pos').row]--;
			for(i = 0; i < panelArray.length; i++) {
				if (panelArray[i].data('pos').row == panel.data('pos').row) {
					panelArray[i].width(panelArray[i].parent().width() / rowArray[panel.data('pos').row]);
					if (panelArray[i].data('pos').col > panel.data('pos').col) {
						panelArray[i].data('pos', {
							row: panelArray[i].data('pos').row, 
							col: panelArray[i].data('pos').col - 1
						});
					}
					panelArray[i].offset({
						left: panelArray[i].parent().offset().left + panelArray[i].data('pos').col * (panelArray[i].parent().width() / (rowArray[panelArray[i].data('pos').row]))
					});
				}
			}
		}
		panel.close();
	}



});


		
