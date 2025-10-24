<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1" />

<title>Karhuenduro laptimer</title>
</head>

<body>
<H2>Laptimer</H2>
<P>
<form action="https://www.karhuenduro.fi/cgi-bin/tulokset.py">Lokin PVM:<br>
    <input type="date" min="2021-01-01" name="date"><br>
Kisan/erän alkuaika:<br>
    <input type="time" name="start"><br>
Kisan/erän loppuaika:<br>
    <input type="time" name="end"><br>
Laskettavien kierrosten määrä:<br>
    <input type="number" name="laps"><br>
Lämppärit:<br>
	<input type="number" name="offset" value="0"><br>
Laskennan tyyppi:<br>
    <select name="mode">
        <option selected value="laptime">Kierrosaika</option>
        <option value="laptime2">Kierrosaika, kisan alku kellosta</option>
        <option value="stage">Pätkäaika</option>
    </select><br>
Käytä kiinteitä numeroita:
	<input type="checkbox" name="static_numbers" value="True"><br>
Tee staattinen tulos-sivu:
	<input type="checkbox" name="static_output" value="True"><br>
Tulos-sivun nimi:
	<input type="text" name="output_file_name" value="tulokset-<?php echo date("Ymd") ?>.html"><br>
Käytä pelkästään "omia" TAGeja (0000*):
	<input type="checkbox" name="bad" value="True"><br>
Debug:
    <input type="checkbox" name="debug" value="True"><br>

    <input type="submit" value="Laske">
</form>
</P>
</body>
</html> 
