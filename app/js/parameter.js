
$(document).ready(function(){

    //-----------------------
    // Append data to the dom
    //-----------------------
    
    $.ajax({
      url: 'load_parameter.php',
      method:"GET",
      dataType: 'json',
      success: function(data){
        
        var mode = data[0].mode;
        var source = data[0].source;
        var dp = data[0].delta_pression_filtre_max;
        var sh = data[0].heure_debut_sequence;
        var shd = data[0].heure_debut_sequence_demande;
        var mi = data[0].minute_debut_sequence;
        var mid = data[0].minute_debut_sequence_demande;
        var coef = data[0].duree_coef;
        var mp = data[0].pression_seuil_bas;
        var max = data[0].pression_seuil_haut;
        
        var td = data[0].duree_test;
        var ocp = data[0].test_pression_canal;
        var ocip = data[0].test_pression_ville;
        var otp = data[0].test_pression_cuve;

        var at = data[0].gestion_cuve;
        var oh = data[0].test_hauteur_eau_cuve;
        var nc = data[0].nb_cuve_ibc;
        var nblc = data[0].nb_litre_cuve_ibc;
        var mic = data[0].seuil_min_capacite_cuve;
        var mac = data[0].seuil_max_capacite_cuve;
        var tt = data[0].seuil_capacite_remplissage_auto_cuve;

        $("#mode").val(mode);
        //$("#modevalue").text(mode);
        $("#source").val(source);

        $("#heure").val(sh);
        $("#heurevalue").text(sh);

        $("#heuredemande").val(shd);
        $("#heuredemandevalue").text(shd);

        $("#minute").val(mi);
        $("#minutevalue").text(mi);

        $("#minutedemande").val(mid);
        $("#minutedemandevalue").text(mid);

        $("#testduration").val(td);
        $("#testdurationvalue").text(td);
        
        $("#coef").val(coef);
        $("#coefvalue").text(coef);

        $("#minpressure").val(mp);
        $("#minpressurevalue").text(mp);
        
        $("#maxpressure").val(max);
        $("#maxpressurevalue").text(max);

        $("#deltapressure").val(dp);
        $("#deltapressurevalue").text(dp);

        $("#nbcuve").val(nc);
        $("#nbcuvevalue").text(nc);

        $("#nblitrecuve").val(nblc);
        $("#nblitrecuvevalue").text(nblc);

        $("#seuilminicuve").val(mic);
        $("#seuilminicuvevalue").text(mic);

        $("#seuilmaxcuve").val(mac);
        $("#seuilmaxcuvevalue").text(mac);

        $("#seuilautocuve").val(tt);
        $("#seuilautocuvevalue").text(tt);


        if (ocp == 1){
            $("#overcanalpressure").prop('checked', true);
        }else{
            $("#overcanalpressure").prop('checked', false);
        
        }

        if (otp == 1){
            $("#overtankpressure").prop('checked', true);
        }else{
            $("#overtankpressure").prop('checked', false);
        
        }

        if (ocip == 1){
          $("#overcitypressure").prop('checked', true);
        }else{
          $("#overcitypressure").prop('checked', false);
      
        }

        if (at == 1){
          $("#activetank").prop('checked', true);
        }else{
          $("#activetank").prop('checked', false);
      
        }

         if (oh == 1){
          $("#overcapacuve").prop('checked', true);
        }else{
          $("#overcapacuve").prop('checked', false);
      
        }

      }
    });

    // update sliders value on input/change
    $("#testduration").on("input",function() {
      $("#testdurationvalue").text(this.value);
    });

    $("#coef").on("input",function() {
      $("#coefvalue").text(this.value);
    });

    $("#minpressure").on("input",function() {
      $("#minpressurevalue").text(this.value);
    });

    $("#maxpressure").on("input",function() {
      $("#maxpressurevalue").text(this.value);
    });

    $("#deltapressure").on("input",function() {
        $("#deltapressurevalue").text(this.value);
    });

    $("#heure").on("input",function() {
      $("#heurevalue").text(this.value);
    });

    $("#heuredemande").on("input",function() {
      $("#heuredemandevalue").text(this.value);
    });

    $("#minute").on("input",function() {
        $("#minutevalue").text(this.value);
    });
  
    $("#minutedemande").on("input",function() {
        $("#minutedemandevalue").text(this.value);
    });

    $("#nbcuve").on("input",function() {
      $("#nbcuvevalue").text(this.value);
    });

    $("#nblitrecuve").on("input",function() {
      $("#nblitrecuvevalue").text(this.value);
    });


    $("#seuilminicuve").on("input",function() {
      $("#seuilminicuvevalue").text(this.value);
    });


    $("#seuilmaxcuve").on("input",function() {
      $("#seuilmaxcuvevalue").text(this.value);
    });


    $("#seuilautocuve").on("input",function() {
      $("#seuilautocuvevalue").text(this.value);
    });



    //---------------------
    // Modify global parameter
    // on Submit event
    //---------------------

    $("#formparameter").submit(function(event) {
      event.preventDefault();
      var form = $(this).serialize();
      console.log("form : "+form);
      $.post("update_parameter.php",form,function(data){
          console.log(data);
          if (data == "ok") {
            window.location = "arrosage.html";
          }else{
            $("#status").append("<div class='alert alert-danger'>There is an error !</div>");
          }
      });
    });
  

});
