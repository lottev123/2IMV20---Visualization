<?php

// database arrays
$artists = [];
$songs = [];

function getPageAsDOMDocument($week, $year) {
    $file = "cache/$year-$week.html";
    if (file_exists($file)) {
        $html = file_get_contents($file);
    } else {
        $url = "https://www.top40.nl/top40/$year/week-$week";
        $html = @file_get_contents($url);
        if ($html === false) {
            return false;
        }
        file_put_contents($file, $html);
    }

    if ($html === false) {
        return false;
    }

    libxml_use_internal_errors(true);
    $doc = new DOMDocument();
    $doc->loadHTML($html);
    return $doc;
}

function registerArtist($artist) {
    global $artists;
    $id = array_search($artist, $artists);

    if ($id === false) {
        $artists[] = $artist;
        return count($artists) - 1;
    }

    return $id;
}

function registerSong($artist, $song) {
    global $songs;
    $id = array_search("$artist\t$song", $songs);

    if ($id === false) {
        $songs[] = "$artist\t$song";
        return count($songs) - 1;
    }

    return $id;
}

function getElementByClassName($domelement, $classname) {
    foreach ($domelement->childNodes as $childNode) {
        if (!$childNode instanceof DOMElement) { continue; }
        if ($childNode->getAttribute("class") == $classname) {
            return $childNode;
        }
        $childResult = getElementByClassName($childNode, $classname);
        if ($childResult !== null) {
            return $childResult;
        }
    }
    return null;
}

// for every year; for every week:
for($year = 1965; $year <= date('Y'); $year += 1) {
    for ($week = 1; $week <= 53; $week += 1) {
        $chart = [];
        $doc = getPageAsDOMDocument($week, $year);
		
		// week 52 and 53 don't always exist
        if ($doc === false) {
            echo "no result for $week of $year\n";
            continue;
        }
		
		// <div id="chart-list"> -> third child element
        $songDivs = $doc->getElementById("chart-list")->childNodes->item(3)->childNodes;

        /** @var DOMElement $songDiv */
        $skipFirst = false;
        $n = 0;
        foreach ($songDivs as $songDiv) {
			// the first element of the song list as it contains the table headers
            if (!$skipFirst) { $skipFirst = true; continue; }
			// some elements are for mobile; they dont have child elements
            if ($songDiv->childNodes->length < 0) { continue; }
			// some weeks have more than 40 songs, they're labeled 'no-longer-listed' and are invisible in the page; we skip those.
            if ($songDiv->getAttribute("class") == "no-longer-listed") { continue; }

			// find the <div class="song-details"> element.
            $songDetails = getElementByClassName($songDiv, "song-details");
            if ($songDetails == null) { continue; }

            $n += 1;
            if ($n > 40) { continue; }

			// song name is the first child
            $song = trim($songDetails->childNodes->item(0)->childNodes->item(0)->textContent);
			// song artist is the first child
            $artist = trim($songDetails->childNodes->item(0)->childNodes->item(1)->textContent);

			// add to the database
            $artistId = registerArtist($artist);
            $songId = registerSong($artist, $song);
			
			// add to the weekly charts
            $chart[] = [$artistId, $songId];
        }

        echo "$n songs for week $week of $year\n";

        // output weekly chart CSV file
        $outStr = "position\tartist_id\tsong_id\n";
        for ($i = 0; $i < count($chart); $i += 1) {
            $outStr .= ($i + 1) . "\t" . $chart[$i][0] . "\t" . $chart[$i][1] . "\n";
        }
        file_put_contents("chart_" . $year . "_week_" . $week . ".csv", $outStr);
    }
}

// output artists CSV file
$outStr = "artist_id\tname\n";
for ($i = 0; $i < count($artists); $i += 1) {
    $outStr .= "$i\t$artists[$i]\n";
}
file_put_contents("artists.csv", $outStr);

// output songs CSV file
$outStr = "song_id\tname\n";
for ($i = 0; $i < count($songs); $i += 1) {
    list($artist, $song) = explode("\t", $songs[$i], 2);
    $outStr .= "$i\t$song\n";
}
file_put_contents("songs.csv", $outStr);