//This blog was very useful in setting this up.
//https://kempe.net/blog/2014/06/14/leaflet-pan-zoom-image.html
//Also big thanks to stack overflow for having some incredible answers.

trajectories = updateTrajectoriesList();    //get list of points

//width, height and url
var w = 2560, h=1920, url='./images/image2.jpg';    //background images for picture
//create new map
var map = L.map('map', {
    minZoom: 1,
    maxZoom: 4,
    center: [w/2,h/2],  //center of the image
    zoom: 1,
    crs: L.CRS.Simple
});

//var drawnLines = L.FeatureGroup();

//get edges of the image by unprojecting coords to the internal latlong system
var se = map.unproject([w, h], map.getMaxZoom()-1); //bottom right is south east
var nw = map.unproject([0, 0], map.getMaxZoom()-1); //0,0 is north west
var bounds = new L.LatLngBounds(se, nw);

map.createPane('imagePane');    //create image pane
map.getPane('imagePane').style.zIndex = -2; //set z so it's behind other elements

//set the image overlay to cover the map
L.imageOverlay(url, bounds, {   //overlay the image onto the map
    pane: 'imagePane',
    attribution: 'Northern Illinois University'
}).addTo(map);

map.setMaxBounds(bounds);   //set bounds of the map

drawTrajectories(map, trajectories);    //draw lines

function drawTrajectories(map, traj) {
    var latlinePoints = [];
    var linesArray = [];
    if(traj === null) return;
    for (let [key, value] of Object.entries(traj)) {    //loop through points
        var color = 'red';
        for(var i = 0; i < value.length; i++) {
            var pt = [value[i][0], value[i][1]];    //get point
            var latlongPt = map.unproject(pt, map.getMaxZoom()-1);  //convert to a latlong coord
            latlinePoints.push(latlongPt);  //add to array
        }

        if(value[0][1] >= 1200) color = 'blue'; //set color based on starting spot
        else color = 'red';

        //draw stuff here
        var polyline = new L.Polyline(latlinePoints, {  //create a new poly line based on points
            color: color,
            weight: 2,
            opacity: 1,
            smoothfactor: 2
        }).bindPopup("ID: "+key);   //add popup with id

        //bind mouse click on polyline to open a new window
        polyline.on('click', function() {   //open a new page when line is clicked
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
}

//Prints dictionary for debugging purposes
function printDictionary(traj) {
    for (let [key, value] of Object.entries(traj)) {
        console.log(`${key}: ${value}`);
    }
}

//updates the trajectories array
function updateTrajectoriesList() {
    var result = JSON.parse(traj);
    console.log(traj);
    return result;    //parse traj from the php file
}