// main.js

// Masonry js
var $grid = $('.grid').masonry({
  itemSelector: '.grid-item',
  columnWidth: 200,
  gutter: 15,
  isFitWidth: true
});

// layout Masonry after each image loads
$grid.imagesLoaded().progress( function() {
  $grid.masonry('layout');
});
