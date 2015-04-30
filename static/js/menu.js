$('body').ready(function(){

  var body = document.body,
      mask = document.createElement('div'),
      toggleSlideLeft = document.querySelector('.toggle-slide-left');

  mask.className = 'mask';

  $(toggleSlideLeft).click(function() {
    $(body).addClass('sml-open');
    document.body.appendChild(mask);
  });
  /* hide active menu if mask is clicked */
  $(mask).click(function(){
    $(body).removeClass('sml-open');
    document.body.removeChild(mask);
  });
  $('.close-menu').click(function(){
    $(body).removeClass('sml-open');
    document.body.removeChild(mask);
  });
      
});