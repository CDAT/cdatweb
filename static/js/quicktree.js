(function( $ ) {
  $.fn.quicktree = function() {

    function click(e){
      var a = $(this);
      a.next('ul').children("li").toggle();
      console.log('click event fired');
      e.preventDefault();
    }

    function child_inserted(e) {
      var new_child = $(e.target);
      if (new_child.parent().get(0) === this) {
        new_child.children('a').click(click);
        new_child.children('ul').quicktree()
      }
    }

    // Grab the LI's and iterate over them
    $(this).find("li").each(function(ind){
      var t = $(this);
      t.children("a").click(click);
      t.children('ul').quicktree();
    });

    $(this).on("DOMNodeInserted", child_inserted);
    return this;
  };

}(jQuery));
