<!DOCTYPE html>
<html lang="en" dir="ltr">

<head>
  <meta charset="utf-8">
  <title>Predatory Battle</title>
  <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">

  <meta name='description' content="A web service for identifying predatory journals in paper references. Check if your paper is citing predatory publications with this online tool.">
  <meta name='keywords' content='predatory journals, publications, open access, think check submit, LIM, Laboratorio di Informatica Musicale, music informatics laboratory, università di milano, university of milan'>
  <meta name='author' content='Federico Simonetta'>
  <meta property='og:image' content='http://www.lim.di.unimi.it/images/homepage/logo.png' />
  <meta property='og:title' content='Predatory Battle'>
  <!-- <meta property='og:url' content='something' /> -->
  <meta property='og:site_name' content='LIM - Laboratorio di Informatica Musicale' />
  <meta property='og:type' content='article' />
  <meta property='og:description' content="A web service for identifying predatory journals in paper references. Check if your paper is citing predatory publications with this online tool." />

  <!-- Copied from lim.di.unimi.it -->
  <link rel="icon" type="image/png" href="http://www.lim.di.unimi.it/favicon.ico" />
  <link href="https://fonts.googleapis.com/css?family=PT+Sans:400,700,400italic,700italic" rel="stylesheet" type="text/css">
  <link href="https://fonts.googleapis.com/css?family=PT+Sans+Narrow:400,700&amp;subset=latin,latin-ext" rel="stylesheet" type="text/css">
  <link href="http://www.lim.di.unimi.it/css/style" rel="stylesheet">
  <link href="http://www.lim.di.unimi.it/css/style_small.css" media="(max-width:1350px)" rel="stylesheet" type="text/css">
  <link href="http://www.lim.di.unimi.it/css/style_medium.css" media="(max-width:1650px)" rel="stylesheet" type="text/css">

</head>

<body>
  <h1>Predatory Battle</h1>
  <hr>
  <p>
    <form action="predatorybattle.php" method="post" enctype="multipart/form-data">
      Select a BibTex file to upload:
      <input type="file" name="fileToUpload" id="fileToUpload">
      <input type="submit" value="Upload and parse BibTex" name="submit">
    </form>
  </p>
  <hr>

<?php
$target_dir = "upload/";
$fileType = strtolower(pathinfo($_FILES["fileToUpload"]["name"],PATHINFO_EXTENSION));
$target_file = $target_dir . uniqid() . "." . $fileType;
$uploadOk = 1;
// Check file size (< 1MB)
if ($_FILES["fileToUpload"]["size"] > 1048576) {
    echo "<p>Sorry, your file is too large.</p>";
    $uploadOk = 0;
}
// Allow certain file formats
if($fileType != "bib" && $fileType != "bibtex") {
    echo "<p>Sorry, you should use files with extension '.bib' or '.bibtex'</p>";
    $uploadOk = 0;
}
// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "<p>Sorry, your file was not uploaded.</p>";
// if everything is ok, try to upload file
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        $command = escapeshellcmd('./check_references.py ' . $target_file);
        $output = shell_exec($command);
        echo '<h2>This is your report</h2>';
        echo '<i><b>Note that the journal names here appear whithout stop-words and in lower-case</b></i>';
        echo '<p>' . $output . '</p>';
    } else {
        echo "<p>Sorry, there was an error uploading your file.</p>";
    }
}
// delete files older than 24 hours
$files = glob("./upload/*");
$now   = time();
foreach ($files as $file) {
  if (is_file($file)) {
    if ($now - filemtime($file) >= 3600 * 24) {
      unlink($file);
    }
  }
}
?>
</body>
</html>
