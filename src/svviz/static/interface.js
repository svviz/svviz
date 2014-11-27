/*global $:false */
'use strict';


function dohover (svg) {
  $(svg + " .read").mouseover(function(){
    console.log($(this).data("readid"));
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
        console.log("LOADING:" + result.name);
      }
      dohover('#' +which +'_result');
      $("#" + which + "_result .svg_container").SVGScroller();
      $( ".svg_container" ).resizable();
    });
  }

  addSVG("alt");
  addSVG("ref");
  addSVG("amb");

  $.getJSON('/_disp', {"req":"counts"}, function(data) {
    console.log(data.result);
    var table = $('<table></table>');

    var keys = ["AltCount", "RefCount", "AmbCount"];

    jQuery.each(keys, function(i, key) {
      var val = data.result[key];
      var row = $('<tr></tr>');
      row.append($("<td>"+key+"</td>"));
      row.append($("<td>"+val+"</td>"));

      table.append(row);
      });
    console.log(table);
    $('#description').append(table);
  });
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


$(function() {
  console.log("here");
  loadSVGs();
});
