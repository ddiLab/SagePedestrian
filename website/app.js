//This blog was very useful in setting this up.
//https://kempe.net/blog/2014/06/14/leaflet-pan-zoom-image.html
//Also big thanks to stack overflow for have some incredible answers.

trajectories = updateTrajectoriesList();
//printDictionary(trajectories);

//width, height and url
var w = 2560, h=1920, url='./images/image2.jpg';
var map = L.map('map', {
    minZoom: 1,
    maxZoom: 4,
    center: [w/2,h/2],
    zoom: 1,
    crs: L.CRS.Simple
});

//var drawnLines = L.FeatureGroup();

//get edges of the image by unprojecting coords to the internal latlong system
var sw = map.unproject([w, h], map.getMaxZoom()-1);
var ne = map.unproject([0, 0], map.getMaxZoom()-1);
var bounds = new L.LatLngBounds(sw, ne);

map.createPane('imagePane');
map.getPane('imagePane').style.zIndex = -2;

//set the image overlay to cover the map
L.imageOverlay(url, bounds, {
    pane: 'imagePane',
    attribution: 'Northern Illinois University'
}).addTo(map);

map.setMaxBounds(bounds);

drawTrajectories(map, trajectories);

function drawTrajectories(map, traj) {
    var latlinePoints = [];
    var linesArray = [];
    for (let [key, value] of Object.entries(traj)) {
        var color = 'red';
        //console.log(key);
        for(var i = 0; i < value.length; i++) {
            var pt = [value[i][0], value[i][1]];
            //console.log("Point:", pt);
            var latlongPt = map.unproject(pt, map.getMaxZoom()-1);
            latlinePoints.push(latlongPt);
            //console.log(`${value[i][0]}`, `${value[i][1]}`);
            //console.log("Latlong point: ");
            //console.log(latlongPt);
        }

        if(value[0][1] >= 1200) color = 'blue';
        else color = 'red';

        //draw stuff here
        var polyline = new L.Polyline(latlinePoints, {
            color: color,
            weight: 2,
            opacity: 1,
            smoothfactor: 2
        }).bindPopup("ID: "+key);//"<a href='http://www.google.com'>" + currentId + "</a>");

        //bind mouse click on polyline to open a new window
        polyline.on('click', function() {
            window.open("./debug.php?id="+key);
        })

        //when mouse hovers over polyline change color to yellow
        polyline.on('mouseover', function(e) {
            var layer = e.target;
            layer.setStyle( {
                color: 'yellow',
                weight: 5
            });
        });

        //when mouse hovers over polyline change color to yellow
        polyline.on('mouseout', function(e) {
            var layer = e.target;
            layer.setStyle( {
                color: (value[0][1] >= 1200) ? 'blue' : 'red',
                weight: 2
            });
        });

        polyline.addTo(map);        //add to map
        latlinePoints.length = 0;   //reset array
    }
    //console.log("Full array: ");
    //console.log(latlinePoints);
}

function printDictionary(traj) {
    for (let [key, value] of Object.entries(traj)) {
        console.log(`${key}: ${value}`);
    }
}

function updateTrajectoriesList() {
    return JSON.parse(traj);
}
