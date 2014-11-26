/*global $:false */
'use strict';

var selectStartPoint = 0;
function dozoom (svg) {
  // svgPanZoom(svg, {
  //   zoomEnabled: true,
  //     // controlIconsEnabled: true,
  //     fit: true,
  //     center: true,
  //     minZoom:0.05,
  //     maxZoom:25
  //   });
}

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
    $('#alt_result #track').html(data.result);
    dozoom('#alt_result svg');
    dohover('#alt_result');

    $(".svg_container").SVGScroller();

  });
  $.getJSON('/_disp', {"req":"ref"}, function(data) {
    $('#ref_result #track').html(data.result);
    dozoom('#ref_result svg');
    dohover('#ref_result');
  });
  $.getJSON('/_disp', {"req":"amb"}, function(data) {
    $('#amb_result #track').html(data.result);
    dozoom('#amb_result svg');
    dohover('#amb_result');
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
  console.log($(".svg_viewport"));
  loadSVGs();
});
