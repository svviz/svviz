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
  $.getJSON('/_disp', {"req":"alt"}, function(data) {
    for (var i=0; i<data.results.length; i++) {
      var result = data.results[i];
      $('#alt_result .' + result.name + ' #track').html(result.svg);
      console.log("LOADING:" + result.name);
    }
    dohover('#alt_result');
    $("#alt_result .svg_container").SVGScroller();
    $( ".svg_container" ).resizable();
  });

  $.getJSON('/_disp', {"req":"ref"}, function(data) {
    $('#ref_result #track').html(data.result);

    dohover('#ref_result');
    $("#ref_result .svg_container").SVGScroller();
  });

  $.getJSON('/_disp', {"req":"amb"}, function(data) {
    $('#amb_result #track').html(data.result);

    dohover('#amb_result');
    $("#amb_result .svg_container").SVGScroller();
  });

  $.getJSON('/_disp', {"req":"counts"}, function(data) {
    console.log(data.result);
    // $('#description').text(JSON.stringify(data.result));
    var table = $('<table></table>');

    var keys = ["AltCount", "RefCount", "AmbCount"];

    jQuery.each(keys, function(i, key) {
      // console.log(key);
      var val = data.result[key];
      var row = $('<tr></tr>');
      row.append($("<td>"+key+"</td>"));
      row.append($("<td>"+val+"</td>"));

      table.append(row);

        // $('#description').append("<p>"+key+":"+val+"</p>");
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
