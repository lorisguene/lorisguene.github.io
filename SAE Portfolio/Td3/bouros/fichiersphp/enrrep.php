<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
<head>
	<title>Site officiel de la commune de Bouros les bains</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link href="./../style.css" rel="stylesheet" type="text/css"/>
</head>
<body>
	<div id="haut">
		<h1>Bienvenue sur le site de Bouros (67)</h1>
		<ul>
			<li><a href="./../actu.htm">Actualités</a></li>
			<li><a href="./../enbref.htm">Bouros en bref </a></li>
			<li><a href="./../conseil.pdf">Le dernier conseil</a></li>
			<li><a href="./../saisie/demande.htm">Recevez le bulletin</a></li>
			<li><a href="./../saisie/questionnaire.htm">Participez à une enquête</a></li>
		</ul>
	</div>
	<div id="centre">
	<?php
	$leNom=$_REQUEST['nom'];
	$lePrénom=$_REQUEST['prenom'];
	$choix=$_REQUEST['heure'];
	$acc=$_REQUEST['acc'];
	$leFichier=fopen("./../reponses.txt","r");
	$trouve=false;
	while (! feof($leFichier) && ! $trouve)
	{	$ligne=fgets($leFichier,250);
		$tableau=explode(";",$ligne);
		if ($tableau[0]==$leNom && $tableau[1]==$lePrénom)
		{	$trouve=true;
		}
	}
	fclose ($leFichier);
	if (!$trouve)
	{	$leFichier=fopen("./../reponses.txt","a");
		$nouvelleLigne=$leNom.";".$lePrénom.";".$choix.";".$acc.";"."\r\n";
		fputs($leFichier,$nouvelleLigne);
		echo "<h1>Vos réponses ont bien été enregistrées</h1>";
		fclose($leFichier);
	}
	else
		echo "<h1>Vous avez déjà répondu à ce questionnaire</h1>";
	?>
	</div>
</body>
</html>