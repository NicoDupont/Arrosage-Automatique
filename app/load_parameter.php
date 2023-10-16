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
    
    $qry = $bdd->prepare("select * from Parameter;");
    $qry->execute();
    $data = $qry->fetchAll(PDO::FETCH_ASSOC);
    $jsondata = json_encode($data);
    echo $jsondata;


	/*
	header('Content-type: application/json');
	ini_set('display_errors', 5);
	include 'config.php';
	$con=mysqli_connect($host, $user, $pass, $bdd);
	if (mysqli_connect_errno()) {
	  echo "Failed to connect to MariaDb: " . mysqli_connect_error();
	}
	$result = mysqli_query($con,"select * from Parameter;");
	$row = mysqli_fetch_assoc($result);
	mysqli_close($con);
	$jsondata = json_encode($row);
	echo $jsondata;	
	*/
?>
