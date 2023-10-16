<?php
  require('/home/pi/vendor/autoload.php');

  use \PhpMqtt\Client\MqttClient;
  use \PhpMqtt\Client\ConnectionSettings;

  include 'config.php';

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

  ini_set('display_errors', 5);

  if($_POST){
    date_default_timezone_set("Europe/Paris");
    
    $idsv = $_POST['idsv'];
    $typesv = $_POST['typesv'];
    $code = $_POST['code'];
    $nom = $_POST['nom'];
    $order = $_POST['numero'];
    $gpio = $_POST['gpio'];
    $seq = $_POST['sequence'];
    $dur = $_POST['duree'];
    $coef = $_POST['coeff'];
    
    //$mon = $_POST['lundi'];
    //$tue = $_POST['mardi'];
    //$wed = $_POST['mercredi'];
    //$thu = $_POST['jeudi'];
    //$fri = $_POST['vendredi'];
    //$sat = $_POST['samedi'];
    //$sun = $_POST['dimanche'];

    if (isset($_POST['active']) && $_POST['active'] == 'yes'){ $act = 1; } else{ $act = 0; }
    if (isset($_POST['open']) && $_POST['open'] == 'yes'){ $opn = 1; } else{ $opn = 0; }
    if (isset($_POST['lundi']) && $_POST['lundi'] == 'yes'){ $mon = 1;} else{ $mon = 0; }
    if (isset($_POST['mardi']) && $_POST['mardi'] == 'yes'){ $tue = 1;} else{ $tue = 0; }
    if (isset($_POST['mercredi']) && $_POST['mercredi'] == 'yes'){ $wed = 1;} else{ $wed = 0; }
    if (isset($_POST['jeudi']) && $_POST['jeudi'] == 'yes'){ $thu = 1;} else{ $thu = 0; }
    if (isset($_POST['vendredi']) && $_POST['vendredi'] == 'yes'){ $fri = 1;} else{ $fri = 0; }
    if (isset($_POST['samedi']) && $_POST['samedi'] == 'yes'){ $sat = 1;} else{ $sat = 0; }
    if (isset($_POST['dimanche']) && $_POST['dimanche'] == 'yes'){ $sun = 1;} else{ $sun = 0; }
    if (isset($_POST['even']) && $_POST['even'] == 'yes'){ $even = 1;} else{ $even = 0; }
    if (isset($_POST['odd']) && $_POST['odd'] == 'yes'){ $odd = 1;} else{ $odd = 0; }
    
    if ($even == 1 || $odd == 1){
      $mon = 0;
      $tue = 0;
      $wed = 0;
      $thu = 0;
      $fri = 0;
      $sun = 0;
      $sat = 0;
    }

    $con=mysqli_connect($host, $user, $pass, $bdd);
    if (mysqli_connect_errno()) {
    	echo "Failed to connect to MySQL: " . mysqli_connect_error();
      //echo "ko";
    }else { //bdd ok

      
        //select actual data
        $result = mysqli_query($con,"select sv,open,active,duration from Zone where id_sv='".$idsv."' limit 1;");
        $row = mysqli_fetch_assoc($result);
        //publish mqtt
        if ($row["open"] != $opn or $row["duration"] != $dur or $row["active"] != $act) {
         $mqttsession = ConnectMqtt($usermqtt,$passmqtt,$servermqtt,$portmqtt);
          if ($row["open"] != $opn)     {PublishMqtt ($mqttsession,"ha/arrosage/".$row["sv"]."/etat",$opn,1,true);}
          if ($row["active"] != $act)   {PublishMqtt ($mqttsession,"ha/arrosage/".$row["sv"]."/active",$act,1,true);}
          if ($row["duration"] != $dur) {PublishMqtt ($mqttsession,"ha/arrosage/".$row["sv"]."/duree",$dur,1,true);}
          DisconnectMqtt($mqttsession);
        }

        // update parameters for single sv

          $sql = "UPDATE Zone SET 
          `order` = '".$order."' 
          , duration = '".$dur."'
          , sv = '".$code."' 
          , name = '".$nom."' 
          , sequence = '".$seq."' 
          , gpio = '".$gpio."' 
          , active = '".$act."' 
          , open = '".$opn."' 
          , even = '".$even."' 
          , odd = '".$odd."' 
          , coef = '".$coef."'
          , monday='".$mon."'
          , tuesday='".$tue."'
          , wednesday='".$wed."'
          , thursday='".$thu."'
          , friday='".$fri."'
          , saturday='".$sat."'
          , sunday='".$sun."'
           where id_sv='".$idsv."'
          ";
        
      	mysqli_query($con,$sql);
        mysqli_close($con);
        echo "ok";
        //echo $sql;
    }

}else {  //post ko
    echo "ko post";
}

?>
