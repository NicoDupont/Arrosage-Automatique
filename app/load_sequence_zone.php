<?php
	header('Content-type: application/json');
    ini_set('display_errors', 5);
    include 'config.php';
    try
    {
        $bdd = new PDO("mysql:host=$host;dbname=$bdd;charset=utf8", $user, $pass);
        $bdd->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    catch(Exception $e)
    {
        die('Erreur : '.$e->getMessage());
    }
    // select data
    $qry = $bdd->prepare("SELECT concat(DATE_FORMAT(StartingDate, '%d-%m %H:%i'),'=>',DATE_FORMAT(EndDate, '%H:%i'),' - ',sv,' : ',name) as seq FROM SequenceZone order by 'order',sv;");
    $qry->execute();
    $data = $qry->fetchAll(PDO::FETCH_ASSOC);
    $jsondata = json_encode($data);
    echo $jsondata;
?>