<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Karhuenduro laptimer</title>
</head>

<body>
<script>
function displayQuestion(answer) {
  // document.getElementById(answer + 'Question').style.display = "block"; // yesQuestion
  if (answer == "True") { // show additional input
    document.getElementById('ajajalistat').style.display = "block";
  } else {
    document.getElementById('ajajalistat').style.display = "none";
  }
}
</script>

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
	<input type="checkbox" name="static_numbers" id="static" value="True" onchange="displayQuestion(this.value)"/><br>
<div id="ajajalistat" style="display:none;">
Käytettävä ajajalista:<br>
    <select name="ajajalista">
        <option selected value="static">Normikuskit</option>
        <option value="sarjakrossit">Sarjakrossit</option>
        <option value="kanada">Muu</option>
    </select><br>
</div>
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
