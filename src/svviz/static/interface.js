'use strict';


function dohover (svg) {
  $(svg + " .read").mouseover(function(){
    console.log($(this).data("readid"));
    console.log($(this).parents());
    // $(svg + " .info").text($(this).data("readid"));

    $.getJSON('/_info', {"readid":$(this).data("readid")}, function(data) {
      $(svg + " .info").html(data.result);
    });


  });
}


function update () {
  function addSVG(which){
    $.getJSON('/_disp', {"req":which}, function(data) {
      for (var i=0; i<data.results.length; i++) {
        var result = data.results[i];
        $('#' +which +'_result .' + result.name + ' .track').html(result.svg);
        // console.log("LOADING:" + result.name);
      }
      dohover('#' +which +'_result');
      $("#" + which + "_result .svg_container").SVGScroller();
      // $( ".svg_container" ).resizable();
    });
  }

  addSVG("alt");
  addSVG("ref");
  addSVG("amb");
}


function loadSVGs() {
  $.getJSON('/_disp', {"req":"progress"},
    function(data) {
      if (data.result == "done"){
        update()
      } else {
        setTimeout(loadSVGs, 100);
      }
  });
}


function setupExport() {
  $.getJSON('/_haspdfexport', function(data) {
    if (data.haspdfexport) {
      $(".requiresRSVG").prop("disabled", false);
      $("#requiresRSVGText").hide();
    }
  });

  $("#runExport").click(function(){
    $("#exportModal").modal("hide");
  })
}

$(function() {
  loadSVGs();
  setupExport();
});
