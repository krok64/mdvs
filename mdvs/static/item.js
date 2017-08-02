$(function() {
$('#ItemsToAdd tr:even').addClass('row1');
$('#ItemsToAdd tr:odd').addClass('row2');
});

$(function() { $("#id_type").change(function(event) 
{ var typeIndex=($("#id_type").val()); 
  var formatStr=($("#"+String(typeIndex)).text());
  var formatArr=formatStr.split(",");
  var formParam=["id_dlina","id_visota","id_m","id_s","id_d","id_dy","id_d2","id_s2","id_privod","id_ust","id_test"];
  for(var i=0;i<formParam.length;i++) {
//    alert(formParam[i]+" "+formatArr[i]);
    if(formatArr[i]!="False") {
      $("#"+formParam[i]).removeClass("hidden");
    }
    else {
       $("#"+formParam[i]).addClass("hidden");
    }
  }
  return false; 
})
})
