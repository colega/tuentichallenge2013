<?php
if ($_COOKIE["adminsession"] === "true") {
	?>
<html>
	<head>
		<title>Problem draft</title>
	</head>
	<body>
		<pre>For each input N return the sum of digits of N!</pre>
	</body>
</html>
	<?
	die();
} else {
	header('HTTP/1.0 403 Forbidden');
	?>
<html>
	<head>
		<title>Forbidden</title>
	</head>
	<body>
		<h1>Forbidden</h1>
		<p>You don't have permission to access this file</p>
		<hr>
		<p><em>Tuenti Contest 2013</em></p>
	<?
	die();
}
