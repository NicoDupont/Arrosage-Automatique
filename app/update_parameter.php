<?php

    require('/home/pi/vendor/autoload.php');

    use \PhpMqtt\Client\MqttClient;
    use \PhpMqtt\Client\ConnectionSettings;

    include 'mqtt.php';
  
    function ConnectMqtt($user,$pass,$server,$port){
        $connectionSettings = new ConnectionSettings();
        $connectionSettings = $connectionSettings
                ->setUsername($user)
                ->setPassword($pass);
        $mqtt = new MqttClient($server, $port, 'mqttphp');
        $mqtt->connect($connectionSettings);
        return $mqtt;

    }

    function DisconnectMqtt($session){
        $session->disconnect();
    }
    
    function PublishMqtt ($session,$topic,$payload,$qos,$retain){
        $session->publish($topic,$payload,$qos,$retain);
  
    }

  if($_POST){
    ini_set('display_errors', 5);
    date_default_timezone_set("Europe/Paris");
    
    $mo = $_POST['mode'];
    $so = $_POST['source'];
    $sh = $_POST['heure'];
    $shd = $_POST['heuredemande'];
    $mi = $_POST['minute'];
    $mid = $_POST['minutedemande'];
    $td = $_POST['testduration'];
    $minp = $_POST['minpressure'];
    $maxp = $_POST['maxpressure'];
    $dp = $_POST['deltapressure'];
    $duree_coef = $_POST['coef'];
    $nc = $_POST['nbcuve'];
    $nblc = $_POST['nblitrecuve'];
    $mic = $_POST['seuilminicuve'];
    $mac = $_POST['seuilmaxcuve'];
    $tt = $_POST['seuilautocuve'];


    if (isset($_POST['overcanalpressure']) && $_POST['overcanalpressure'] == 'yes'){
        $ocp = 1;
    }else{
        $ocp = 0;
    }

    if (isset($_POST['overcitypressure']) && $_POST['overcitypressure'] == 'yes'){
        $ocip = 1;
    }else{
        $ocip = 0;
    }

    if (isset($_POST['overtankpressure']) && $_POST['overtankpressure'] == 'yes'){
        $otp = 1;
    }else{
        $otp = 0;
    }

    if (isset($_POST['activetank']) && $_POST['activetank'] == 'yes'){
        $at = 1;
    }else{
        $at = 0;
    }

    if (isset($_POST['overcapacuve']) && $_POST['overcapacuve'] == 'yes'){
        $oh = 1;
    }else{
        $oh = 0;
    }


		include 'config.php';
        $con=mysqli_connect($host, $user, $pass, $bdd);
    	if (mysqli_connect_errno()) {
    	echo "Failed to connect to MySQL: " . mysqli_connect_error();
        echo "ko";
    	}else { //bdd ok

        //select actual data
        $result = mysqli_query($con,"select * from Parameter limit 1;");
        $row = mysqli_fetch_assoc($result);
    

        if ($row["mode"] != $mo or 
            $row["source"] != $so or 
            $row["heure_debut_sequence"] != $sh or 
            $row["heure_debut_sequence_demande"] != $shd or 
            $row["minute_debut_sequence"] != $mi or 
            $row["minute_debut_sequence_demande"] != $mid or 
            $row["duree_test"] != $td or 
            $row["duree_coef"] != $duree_coef or 
            $row["pression_seuil_bas"] != $minp or 
            $row["pression_seuil_haut"] != $maxp or
            $row["delta_pression_filtre_max"] != $dp or
            $row["test_pression_cuve"] != $otp or
            $row["test_pression_canal"] != $ocp or
            $row["test_pression_ville"] != $ocip or
            $row["nb_cuve_ibc"] != $nc or
            $row["nb_litre_cuve_ibc"] != $nblc or
            $row["seuil_min_capacite_cuve"] != $mic or
            $row["seuil_max_capacite_cuve"] != $mac or
            $row["seuil_capacite_remplissage_auto_cuve"] != $tt or
            $row["gestion_cuve"] != $at or
            $row["test_hauteur_eau_cuve"] != $oh) {
                
            $mqttsession = ConnectMqtt($usermqtt,$passmqtt,$servermqtt,$portmqtt);
            
            if ($row["mode"] != $mo) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/mode',$mo,1,true);}
            if ($row["source"] != $so) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/source_arrosage',$so,1,true);}
            if ($row["heure_debut_sequence"] != $sh) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/heure_debut_sequence',$sh,1,true);}
            if ($row["heure_debut_sequence_demande"] != $shd) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/heure_debut_sequence_demande',$shd,1,true);}
            if ($row["minute_debut_sequence"] != $mi) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/minute_debut_sequence',$mi,1,true);}
            if ($row["minute_debut_sequence_demande"] != $mid) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/minute_debut_sequence_demande',$mid,1,true);}
            if ($row["duree_test"] != $td) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/duree_test',$td,1,true);}
            if ($row["duree_coef"] != $duree_coef) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/duree_coef',$duree_coef,1,true);}
            if ($row["pression_seuil_bas"] != $minp) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/pression_seuil_bas',$minp,1,true);}
            if ($row["pression_seuil_haut"] != $maxp) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/pression_seuil_haut',$maxp,1,true);}
            if ($row["delta_pression_filtre_max"] != $dp) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/delta_pression_filtre_max',$dp,1,true);}
            if ($row["test_pression_cuve"] != $otp) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/test_pression_cuve',$otp,1,true);}
            if ($row["test_pression_canal"] != $ocp) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/test_pression_canal',$ocp,1,true);}
            if ($row["test_pression_ville"] != $ocip) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/test_pression_ville',$ocip,1,true);}
            if ($row["nb_cuve_ibc"] != $nc) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/nb_cuve_ibc',$nc,1,true);}
            if ($row["nb_litre_cuve_ibc"] != $nblc) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/nb_litre_cuve_ibc',$nblc,1,true);}
            if ($row["seuil_min_capacite_cuve"] != $mic) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/seuil_min_capacite_cuve',$mic,1,true);}
            if ($row["seuil_max_capacite_cuve"] != $mac) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/seuil_max_capacite_cuve',$mac,1,true);}
            if ($row["seuil_capacite_remplissage_auto_cuve"] != $tt) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/seuil_capacite_remplissage_auto_cuve',$tt,1,true);}
            if ($row["gestion_cuve"] != $at) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/gestion_cuve',$at,1,true);}
            if ($row["test_hauteur_eau_cuve"] != $oh) {PublishMqtt ($mqttsession,'ha/arrosage/parametre/test_hauteur_eau_cuve',$oh,1,true);}

            DisconnectMqtt($mqttsession);
                
        }


        // update global parameters
      	mysqli_query($con,"UPDATE Parameter SET 
                          duree_test = '".$td."'
                        , duree_coef = '".$duree_coef."'
                        , pression_seuil_bas='".$minp."'
                        , pression_seuil_haut='".$maxp."'
                        , delta_pression_filtre_max='".$dp."'
                        , test_pression_cuve='".$otp."'
                        , test_pression_canal='".$ocp."'
                        , heure_debut_sequence='".$sh."'
                        , heure_debut_sequence_demande='".$shd."'
                        , minute_debut_sequence='".$mi."'
                        , minute_debut_sequence_demande='".$mid."'
                        , mode = '".$mo."'
                        , source = '".$so."'
                        , test_pression_ville = '".$ocip."'
                        , nb_cuve_ibc = '".$nc."'
                        , nb_litre_cuve_ibc = '".$nblc."'
                        , seuil_min_capacite_cuve = '".$mic."'
                        , seuil_max_capacite_cuve = '".$mac."'
                        , seuil_capacite_remplissage_auto_cuve = '".$tt."'
                        , gestion_cuve = '".$at."'
                        , test_hauteur_eau_cuve = '".$oh."'
                        ");
    }
        mysqli_close($con);

        echo "ok";
      
    }else {  //post ko
        echo "ko post";
    }

?>
