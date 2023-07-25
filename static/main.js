let HOME = {lat: 0, lon: 0};

const svg = d3.select("#map");
svg.attr('width', window.innerWidth);
svg.attr('height', window.innerHeight);
const width = svg.attr("width");
const height = svg.attr("height");
const projection = d3.geoNaturalEarth1()
    .scale(Math.min(width, height * 1.86) / 1.9 / Math.PI)
    .translate([width / 2, height / 2]);

const drawWorld = () => {
    return d3.json("/static/world.geojson").then((data) => {
        svg.append("path")
            .datum(d3.geoGraticule())
            .attr("d", d3.geoPath().projection(projection))
            .style("fill", "none")
            .style("stroke", "#424242");
        svg.append("path")
            .datum(d3.geoCircle().radius(179.9))
            .attr("d", d3.geoPath().projection(projection))
            .style("fill", "none")
            .style("stroke", "#424242");
        svg.append("g")
            .selectAll("path")
            .data(data.features)
            .join("path")
                .attr("fill", "black")
                .attr("d", d3.geoPath().projection(projection))
                .style("stroke", "green");
    });
}

const connectWebsocket = () => {
    let socket = new WebSocket(`wss://${window.location.host}/data`);
    socket.onerror = (e) => {
        console.log("Websocket is disconnected");
    }
    socket.onmessage = ret => {
        message = JSON.parse(ret.data);
        if(message.home){
            console.log("WebSocket is connected");
            HOME = {lat: message.lat, lon: message.lon};
        }
        else{
            drawTrace(message.lat, message.lon);
        }
    };
}

const drawTrace = (lat, lon) => {
    let start = projection([lon, lat]);
    let end = projection([HOME.lon, HOME.lat]);
    console.log(`Drawing trace from ${lat}, ${lon}`);

    let path = svg.append("path")
        .datum({type: "LineString", coordinates: [[lon, lat], [HOME.lon, HOME.lat]]})
        .attr("class", "arc")
        .attr("d", d3.geoPath().projection(projection))
        .style("fill", "none")
        .attr('stroke', 'white');

    const markerId = `marker${lat}_${lon}`.replaceAll('.', '');
    let existingMarker = d3.select(`#${markerId}`);
    if(existingMarker.node()){
        const newRadius = Math.min(Number(existingMarker.attr('r')) + 0.5, 5);
        existingMarker.attr('r', newRadius);
    }
    else{
        svg.append('circle')
            .attr('id', markerId)
            .attr('r', 1)
            .attr('cx', start[0])
            .attr('cy', start[1])
            .attr('stroke', 'red')
            .attr('fill', 'red');
    }

    const length = path.node().getTotalLength();
    path.attr("stroke-dasharray", `${length * 0.2} ${length * 0.8}`)
        .attr("stroke-dashoffset", length)
        .transition()
        .ease(d3.easeCubicInOut)
        .attr("stroke-dashoffset", (length * 0.2))
        .duration(1200)
        .on('end', () => {path.remove()});
}

window.addEventListener('load', () => {
    drawWorld().then(connectWebsocket);
});
